"""Etapa 7 — Modelo D: detecção de padrões atípicos (H5).

Resíduos do Modelo A. Para cada unidade i na UF s, com matriz B_s estimada:
  esperado do finalista do PT no 2T (Lula em 2026 e 2022; Haddad em 2018): E_i = N_i · (x_i · B_s)[Lula]
  resíduo na proporção: r_i = y_i/N_i − p_i
  variância esperada: p_i(1 − p_i) · (1/N_i + τ²_s)
      1/N_i  = variação de amostragem (binomial), que diminui com o tamanho;
      τ²_s   = variação entre lugares que o modelo não explica e que NÃO
               diminui com o tamanho (estimada por UF pelo método de
               DerSimonian e Laird).
  z_i = r_i / sqrt(variância). Sem o termo τ², municípios grandes teriam z
  enorme por qualquer diferença pequena de comportamento (a primeira versão
  desta etapa usava só a sobredispersão φ, proporcional a N, e listava as
  capitais como os maiores resíduos por esse motivo; o z de Pearson continua
  gravado na coluna z_pt_pearson para comparação).
  z robusto = (z − mediana) / (1,4826 · desvio absoluto mediano), dentro de cada
  ano e nível; p-valor bilateral normal; correção de Benjamini-Hochberg para
  múltiplas comparações (q-valor).

Outras verificações:
  - concentração geográfica dos maiores resíduos (por UF, teste qui-quadrado);
  - autocorrelação espacial dos resíduos municipais (I de Moran, vizinhança por
    contiguidade "queen" da malha do IBGE; p-valor por 999 permutações) e
    agrupamentos locais (LISA);
  - os mesmos indicadores para 2022 e 2018 (mesmo modelo, mesmo código);
  - resíduo por modelo de urna, com efeito fixo de município (compara urnas de
    modelos diferentes dentro do mesmo município);
  - seções com variação extrema de comparecimento (todas as 499 mil seções).

A Lei de Benford não é usada: a distribuição do primeiro dígito de contagens
de votos por seção depende do tamanho das seções (limitado pela lei a cerca de
400–500 eleitores) e da participação de cada candidato, de modo que desvios
são esperados em eleições sem nenhuma irregularidade (Deckert, Myagkov e
Ordeshook, 2011; Mebane, 2011 discute a versão do segundo dígito com as mesmas
ressalvas).
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd
from scipy import stats

from comum import FIGURAS, INTERIM, RAW, REGIAO, SEMENTE, TABELAS, salvar_json

ORIG = ["a_1", "b_1", "o_1", "bn_1", "abst_1"]
DEST = ["a_2", "b_2", "bn_2", "abst_2"]


def matrizes_uf(ano: int, nivel: str):
    sufixo = "_2026" if ano == 2026 else "_2022_2018"
    t = pd.read_csv(TABELAS / f"03_matriz_transicao_por_uf{sufixo}.csv")
    t = t[(t.ano == ano) & (t.nivel == nivel) & (t.origens == "base")]
    Bs, phis = {}, {}
    for uf, g in t.groupby("uf"):
        B = g.pivot(index="origem", columns="destino", values="taxa").loc[ORIG, DEST].to_numpy()
        Bs[uf], phis[uf] = B, g.phi.iloc[0]
    return Bs, phis


def bh(p):
    p = np.asarray(p)
    n = len(p)
    o = np.argsort(p)
    q = p[o] * n / np.arange(1, n + 1)
    q = np.minimum.accumulate(q[::-1])[::-1]
    out = np.empty(n)
    out[o] = np.clip(q, 0, 1)
    return out


def residuos(df, Bs, phis):
    R = df[ORIG].to_numpy(float, copy=True)
    Y = df[DEST].to_numpy(float, copy=True)
    d = Y.sum(1) - R.sum(1)
    R[:, -1] += np.clip(d, 0, None)
    Y[:, -1] += np.clip(-d, 0, None)
    N = R.sum(1)
    X = R / np.where(N > 0, N, 1)[:, None]
    P = np.stack([X[i] @ Bs[u] for i, u in enumerate(df.uf)])
    phi = df.uf.map(phis).to_numpy(float)
    out = df[["uf", "cd_mun"] + [c for c in ("zona", "secao", "nm_municipio") if c in df]].copy()
    out["N"] = N
    for j, nome in enumerate(["pt", "direita"]):  # finalista do PT / finalista de direita
        p = np.clip(P[:, j], 1e-9, 1 - 1e-9)
        e = Y[:, j] - N * p
        out[f"esperado_{nome}"] = N * p
        out[f"obs_{nome}"] = Y[:, j]
        out[f"z_{nome}_pearson"] = e / np.sqrt(phi * N * p * (1 - p))
        r = Y[:, j] / N - p
        v0 = p * (1 - p) / N
        tau2 = np.zeros(len(df))
        # τ² estimado no mesmo agrupamento usado para estimar B (região, se a UF tem < 20 unidades)
        cont = df.uf.value_counts()
        grupo = df.uf.where(df.uf.map(cont) >= 20, df.uf.map(REGIAO)).to_numpy()
        for gname in np.unique(grupo):
            m = grupo == gname
            w = 1 / v0[m]
            k = m.sum()
            q = (w * r[m] ** 2).sum()
            c = w.sum() - (w ** 2).sum() / w.sum()
            tau2[m] = max(0.0, (q - (k - 1)) / c) / max(np.mean(p[m] * (1 - p[m])), 1e-9) if k > 1 else 0.0
        out[f"tau2_{nome}"] = tau2
        out[f"z_{nome}"] = r / np.sqrt(v0 + tau2 * p * (1 - p))
    E = np.clip(N[:, None] * P, 1e-9, None)
    with np.errstate(divide="ignore", invalid="ignore"):
        out["dev_unidade"] = 2 * np.where(Y > 0, Y * np.log(Y / E), 0).sum(1) - 2 * (Y - E).sum(1)
    out["dev_esc"] = out.dev_unidade / phi
    out["p_dev"] = stats.chi2.sf(out.dev_esc, 3)
    z = out.z_pt
    med = np.median(z)
    mad = 1.4826 * np.median(np.abs(z - med))
    out["zr_pt"] = (z - med) / mad
    out["p_pt"] = 2 * stats.norm.sf(np.abs(out.zr_pt))
    out["q_pt"] = bh(out.p_pt)
    out["q_dev"] = bh(out.p_dev)
    return out


def resumo_distribuicao(r, ano, nivel):
    z = r.z_pt
    return {"ano": ano, "nivel": nivel, "unidades": len(r), "dp_z": float(z.std()),
            "dp_robusto_z": float(1.4826 * np.median(np.abs(z - z.median()))),
            "frac_abs_zr_gt3": float((r.zr_pt.abs() > 3).mean()),
            "frac_abs_zr_gt4": float((r.zr_pt.abs() > 4).mean()),
            "n_q_lula_lt_005": int((r.q_pt < 0.05).sum()),
            "n_q_dev_lt_005": int((r.q_dev < 0.05).sum()),
            "curtose_excesso_z": float(stats.kurtosis(z)), "assimetria_z": float(stats.skew(z))}


def moran(r_mun, ano):
    import geopandas as gpd
    from esda.moran import Moran, Moran_Local
    from libpysal.weights import Queen
    geo = gpd.read_file(RAW / "ibge" / "malha_municipios_BR.geojson")
    col = "codarea" if "codarea" in geo else geo.columns[0]
    geo["cd_ibge"] = geo[col].astype(str)
    mapa = pd.read_parquet(INTERIM / "t2_municipios_2026.parquet")[["uf", "cd_mun_tse", "cd_ibge"]]
    mapa = mapa.assign(uf=mapa.uf.str.upper(), cd_mun=mapa.cd_mun_tse.astype(int))
    r = r_mun.merge(mapa[["uf", "cd_mun", "cd_ibge"]], on=["uf", "cd_mun"])
    g = geo.merge(r, on="cd_ibge", how="inner").reset_index(drop=True)
    w = Queen.from_dataframe(g, use_index=False, silence_warnings=True)
    w.transform = "r"
    np.random.seed(SEMENTE)  # esda usa o gerador global do numpy nas permutações
    mi = Moran(g.zr_pt.to_numpy(), w, permutations=999)
    lisa = Moran_Local(g.zr_pt.to_numpy(), w, permutations=999, seed=SEMENTE)
    sig = lisa.p_sim < 0.05
    g["lisa"] = np.where(~sig, "não significativo",
                         np.select([lisa.q == 1, lisa.q == 3, lisa.q == 2, lisa.q == 4],
                                   ["alto-alto", "baixo-baixo", "baixo-alto", "alto-baixo"], "?"))
    lisa_uf = g[g.lisa.isin(["alto-alto", "baixo-baixo"])].groupby(["uf", "lisa"]).size().unstack(fill_value=0)
    return {"ano": ano, "moran_I": float(mi.I), "p_permutacao": float(mi.p_sim), "z_norm": float(mi.z_norm),
            "municipios": int(len(g)), "lisa_alto_alto": int((g.lisa == "alto-alto").sum()),
            "lisa_baixo_baixo": int((g.lisa == "baixo-baixo").sum())}, lisa_uf, g[["cd_ibge", "uf", "cd_mun", "zr_pt", "lisa", "geometry"]]


def efeito_modelo_urna(rs, sec):
    """Resíduo de seção por modelo de urna, com efeito fixo de município."""
    import statsmodels.api as sm
    d = rs.merge(sec[["uf", "cd_mun", "zona", "secao", "modelo_urna_2"]], on=["uf", "cd_mun", "zona", "secao"])
    d = d[d.modelo_urna_2.str.startswith("UE")]
    d["g"] = d.uf + d.cd_mun.astype(str)
    cnt = d.groupby("g").modelo_urna_2.transform("nunique")
    d = d[cnt > 1]  # só municípios com mais de um modelo de urna na amostra
    dum = pd.get_dummies(d.modelo_urna_2, drop_first=False, dtype=float)
    ref = dum.columns[0]
    dum = dum.drop(columns=ref)
    y = d.zr_pt - d.groupby("g").zr_pt.transform("mean")
    X = dum - dum.groupby(d.g).transform("mean")
    fit = sm.OLS(y, X).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(d.g)[0]})
    return pd.DataFrame({"modelo": X.columns, "referencia": ref, "coef_z": fit.params.values,
                         "ep": fit.bse.values, "p": fit.pvalues.values, "secoes": len(d),
                         "municipios": d.g.nunique()})


def extremos_comparecimento(sec):
    s = sec[(sec.aptos_1 > 0) & (sec.aptos_2 > 0)].copy()
    s["dcomp_pp"] = 100 * (s.comp_2 / s.aptos_2 - s.comp_1 / s.aptos_1)
    s["aptos_mudaram"] = s.aptos_1 != s.aptos_2
    tab = []
    for lim in (10, 15, 20, 30):
        m = s.dcomp_pp.abs() > lim
        tab.append({"limite_pp": lim, "secoes": int(m.sum()), "pct": 100 * m.mean(),
                    "das_quais_aptos_mudaram": int((m & s.aptos_mudaram).sum()),
                    "das_quais_aptos_menor_50": int((m & (s.aptos_1 < 50)).sum())})
    return pd.DataFrame(tab), s


def main():
    resumos, morans, top, urna = [], [], [], []
    for ano in (2026, 2022, 2018):
        mun = pd.read_parquet(INTERIM / f"municipios_{ano}.parquet")
        sec = pd.read_parquet(INTERIM / f"secoes_{ano}.parquet")
        for nivel in ("municipio", "secao"):
            Bs, phis = matrizes_uf(ano, nivel)
            if nivel == "municipio":
                df = mun[mun.validos_1 > 0]
            else:
                if ano == 2026:
                    df = sec[sec.na_amostra_bu.fillna(False).astype(bool)]
                else:
                    from analise_03_inferencia_ecologica import amostra_historica
                    df = amostra_historica(sec, ano)
            # UF sem matriz própria (estimada pela região) usa a matriz registrada para ela
            df = df[df.uf.isin(Bs)]
            r = residuos(df, Bs, phis)
            r.to_parquet(INTERIM / f"residuos_{ano}_{nivel}.parquet", index=False)
            resumos.append(resumo_distribuicao(r, ano, nivel))
            if nivel == "municipio":
                m, lisa_uf, g = moran(r, ano)
                morans.append(m)
                lisa_uf.to_csv(TABELAS / f"07_lisa_por_uf_{ano}.csv")
                g.to_parquet(INTERIM / f"lisa_{ano}.parquet")
                conc = r.assign(sig=r.q_pt < 0.05).groupby("uf").agg(unidades=("sig", "size"), sinalizados=("sig", "sum"))
                conc["esperado"] = conc.unidades * conc.sinalizados.sum() / conc.unidades.sum()
                conc.to_csv(TABELAS / f"07_concentracao_uf_{ano}.csv")
                if ano == 2026:
                    x = mun[["uf", "cd_mun", "aptos_1", "a_1", "b_1", "validos_1", "a_2", "validos_2",
                             "comp_1", "comp_2", "aptos_2", "bn_1", "bn_2", "n_secoes"]]
                    t = r.merge(x, on=["uf", "cd_mun"])
                    t["lula_1T_pct"] = 100 * t.a_1 / t.validos_1
                    t["lula_2T_pct"] = 100 * t.a_2 / t.validos_2
                    t["dcomp_pp"] = 100 * (t.comp_2 / t.aptos_2 - t.comp_1 / t.aptos_1)
                    t["dbn_pp"] = 100 * (t.bn_2 / t.comp_2 - t.bn_1 / t.comp_1)
                    t["aptos_mudaram"] = t.aptos_1 != t.aptos_2
                    t = t.reindex(t.zr_pt.abs().sort_values(ascending=False).index)
                    t.head(40).to_csv(TABELAS / "07_maiores_residuos_municipios_2026.csv", index=False)
                    top = t.head(40)
            elif ano in (2026, 2022):
                urna.append(efeito_modelo_urna(r, sec).assign(ano=ano))
        if ano == 2026:
            ext, s = extremos_comparecimento(sec)
            ext.to_csv(TABELAS / "07_extremos_comparecimento_2026.csv", index=False)
            r = pd.read_parquet(INTERIM / "residuos_2026_secao.parquet")
            r.reindex(r.zr_pt.abs().sort_values(ascending=False).index).head(40).merge(
                sec[["uf", "cd_mun", "zona", "secao", "aptos_1", "aptos_2", "comp_1", "comp_2", "a_1", "b_1",
                     "a_2", "b_2", "origem_voto_2", "modelo_urna_2"]], on=["uf", "cd_mun", "zona", "secao"]
            ).to_csv(TABELAS / "07_maiores_residuos_secoes_amostra_2026.csv", index=False)
    pd.DataFrame(resumos).to_csv(TABELAS / "07_distribuicao_residuos_por_ano.csv", index=False)
    pd.DataFrame(morans).to_csv(TABELAS / "07_moran_por_ano.csv", index=False)
    pd.concat(urna).to_csv(TABELAS / "07_residuo_por_modelo_urna.csv", index=False)
    with pd.option_context("display.width", 250, "display.max_columns", 30, "display.float_format", "{:,.3f}".format):
        print(pd.DataFrame(resumos).to_string())
        print(pd.DataFrame(morans).to_string())
        print(pd.concat(urna).to_string())
        print(top[["uf", "nm_municipio", "aptos_1", "lula_1T_pct", "lula_2T_pct", "z_pt", "zr_pt", "q_pt",
                   "dcomp_pp", "dbn_pp", "aptos_mudaram"]].head(25).to_string())
        print(ext.to_string())


if __name__ == "__main__":
    main()
