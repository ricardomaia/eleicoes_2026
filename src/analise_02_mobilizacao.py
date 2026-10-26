"""Etapa 2 — Mobilização eleitoral (H3) e Pergunta central A.

Pergunta A: os votos válidos adicionais do 2º turno concentraram-se onde Lula
já tinha vantagem no 1º turno?

Medidas por unidade i (seção, zona, município, UF):
  ΔV_i = V2 − V1 (válidos), ΔC_i = C2 − C1 (comparecimento), ΔBN_i = BN2 − BN1
  taxas = Δ / aptos do 1º turno
  margem_1 = (Lula1 − Flávio1) / V1   (vantagem inicial; > 0 favorece Lula)

O mesmo código roda para 2018 e 2022 (finalista do PT = "a", finalista de
direita = "b"), para servir de referência histórica.

Atenção à interpretação: ΔV e ΔC são variações líquidas. Elas não dizem
quem mudou de comportamento; uma seção com ΔC = 0 pode ter tido muitas
pessoas que votaram só no 1º turno e outras tantas que votaram só no 2º.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.api as sm

from comum import DERIVADOS, INTERIM, REGIAO, TABELAS, salvar_json

FAIXAS = [-1.01, -0.20, -0.10, 0.0, 0.10, 0.20, 1.01]
ROT_FAIXAS = ["b ≥ +20 pp", "b +10 a +20", "b 0 a +10", "a 0 a +10", "a +10 a +20", "a ≥ +20 pp"]


def corr_pond(x, y, w) -> float:
    m = np.isfinite(x) & np.isfinite(y) & np.isfinite(w)
    x, y, w = x[m], y[m], w[m]
    mx, my = np.average(x, weights=w), np.average(y, weights=w)
    cov = np.average((x - mx) * (y - my), weights=w)
    return cov / np.sqrt(np.average((x - mx) ** 2, weights=w) * np.average((y - my) ** 2, weights=w))


def covariaveis() -> pd.DataFrame:
    ibge = pd.read_csv(DERIVADOS / "ibge_municipios.csv", dtype={"cd_ibge": str})
    t2 = pd.read_parquet(INTERIM / "t2_municipios_2026.parquet")[["uf", "cd_mun_tse", "cd_ibge"]]
    t2 = t2.assign(uf=t2.uf.str.upper(), cd_mun=t2.cd_mun_tse.astype(int)).drop(columns="cd_mun_tse")
    cov = t2.merge(ibge, on="cd_ibge", how="left")
    cov["log_renda_pc"] = np.log(cov.renda_pc_media)
    cov["log_pop"] = np.log(cov.pop_2022)
    return cov


def preparar(df: pd.DataFrame) -> pd.DataFrame:
    d = df[(df.aptos_1 > 0) & (df.validos_1 > 0)].copy()
    d["margem_1"] = (d.a_1 - d.b_1) / d.validos_1
    d["faixa"] = pd.cut(d.margem_1, FAIXAS, labels=ROT_FAIXAS)
    d["dV"] = d.validos_2 - d.validos_1
    d["dC"] = d.comp_2 - d.comp_1
    d["dBN"] = d.bn_2 - d.bn_1
    for c in ("dV", "dC", "dBN"):
        d[f"{c}_taxa"] = d[c] / d.aptos_1
    d["share_a1"] = d.a_1 / d.validos_1
    d["share_b1"] = d.b_1 / d.validos_1
    d["share_o1"] = d.o_1 / d.validos_1
    d["taxa_bn1"] = d.bn_1 / d.comp_1.where(d.comp_1 > 0)
    d["taxa_abst1"] = d.abst_1 / d.aptos_1
    if "a_2" in d and d.a_2.notna().any():
        d["dA"] = d.a_2 - d.a_1
        d["dB"] = d.b_2 - d.b_1
        d["dA_taxa"] = d.dA / d.aptos_1
        d["dB_taxa"] = d.dB / d.aptos_1
    return d


def por_faixa(d: pd.DataFrame, nivel: str, ano: int) -> pd.DataFrame:
    g = d.groupby("faixa", observed=False)
    t = pd.DataFrame({
        "unidades": g.size(), "aptos_1": g.aptos_1.sum(),
        "dV": g.dV.sum(), "dC": g.dC.sum(), "dBN": g.dBN.sum(),
    })
    if "dA" in d:
        t["dA"], t["dB"] = g.dA.sum(), g.dB.sum()
        t["o_1"] = g.o_1.sum()
    t["pct_aptos"] = 100 * t.aptos_1 / t.aptos_1.sum()
    t["pct_dV_nacional"] = 100 * t.dV / t.dV.sum()
    t["dV_por_100_aptos"] = 100 * t.dV / t.aptos_1
    t["dC_por_100_aptos"] = 100 * t.dC / t.aptos_1
    t["dBN_por_100_aptos"] = 100 * t.dBN / t.aptos_1
    if "dA" in t:
        t["dA_por_100_aptos"] = 100 * t.dA / t.aptos_1
        t["dB_por_100_aptos"] = 100 * t.dB / t.aptos_1
    return t.reset_index().assign(nivel=nivel, ano=ano)


def correlacoes(d: pd.DataFrame, nivel: str, ano: int) -> list[dict]:
    w = d.aptos_1.to_numpy(float)
    out = []
    pares = [("share_a1", "dV_taxa"), ("share_b1", "dV_taxa"), ("share_a1", "dC_taxa"),
             ("share_b1", "dC_taxa"), ("share_a1", "dBN_taxa"), ("share_o1", "dV_taxa")]
    if "dA_taxa" in d:
        pares += [("dV_taxa", "dA_taxa"), ("dV_taxa", "dB_taxa"), ("dBN_taxa", "dA_taxa"),
                  ("dC_taxa", "dA_taxa"), ("share_o1", "dA_taxa"), ("share_o1", "dB_taxa")]
    for x, y in pares:
        out.append({"ano": ano, "nivel": nivel, "x": x, "y": y, "n": len(d),
                    "r_ponderado_aptos": corr_pond(d[x].to_numpy(float), d[y].to_numpy(float), w),
                    "r_sem_peso": d[[x, y]].corr().iloc[0, 1]})
    return out


def regressao(d: pd.DataFrame, y: str, xs: list[str], nivel: str, ano: int, fe_uf=True,
              cluster: str | None = "cd_mun") -> pd.DataFrame:
    cols = [y] + xs + (["uf"] if fe_uf else []) + ([cluster] if cluster and cluster in d else []) + ["aptos_1"]
    z = d[[c for c in dict.fromkeys(cols) if c in d]].replace([np.inf, -np.inf], np.nan).dropna()
    X = z[xs].astype(float)
    if fe_uf:
        X = pd.concat([X, pd.get_dummies(z.uf, prefix="uf", drop_first=True, dtype=float)], axis=1)
    X = sm.add_constant(X)
    mod = sm.WLS(z[y].astype(float), X, weights=z.aptos_1.astype(float))
    if cluster and cluster in z and z[cluster].nunique() > 30:
        fit = mod.fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(z.uf + z[cluster].astype(str))[0]})
    else:
        fit = mod.fit(cov_type="HC1")
    ci = fit.conf_int()
    return pd.DataFrame({"ano": ano, "nivel": nivel, "y": y, "termo": xs, "coef": fit.params[xs].values,
                         "ep": fit.bse[xs].values, "ic95_inf": ci.loc[xs, 0].values,
                         "ic95_sup": ci.loc[xs, 1].values, "p": fit.pvalues[xs].values,
                         "n": int(fit.nobs), "r2": fit.rsquared, "efeitos_fixos_uf": fe_uf})


def ranking_uf(mun: pd.DataFrame) -> pd.DataFrame:
    uf = mun.groupby("uf").sum(numeric_only=True)
    r = pd.DataFrame({
        "aptos": uf.aptos_1,
        "comparecimento_1T_pct": 100 * uf.comp_1 / uf.aptos_1,
        "comparecimento_2T_pct": 100 * uf.comp_2 / uf.aptos_2,
        "validos_1T": uf.validos_1, "validos_2T": uf.validos_2,
        "lula_1T_pct_validos": 100 * uf.a_1 / uf.validos_1,
        "lula_2T_pct_validos": 100 * uf.a_2 / uf.validos_2,
        "outros_1T_pct_validos": 100 * uf.o_1 / uf.validos_1,
    })
    r["var_comparecimento_pp"] = r.comparecimento_2T_pct - r.comparecimento_1T_pct
    r["var_validos_abs"] = r.validos_2T - r.validos_1T
    r["var_validos_por_100_aptos"] = 100 * r.var_validos_abs / r.aptos
    r["var_lula_abs"] = uf.a_2 - uf.a_1
    r["var_flavio_abs"] = uf.b_2 - uf.b_1
    r["var_lula_por_100_aptos"] = 100 * r.var_lula_abs / r.aptos
    r["var_flavio_por_100_aptos"] = 100 * r.var_flavio_abs / r.aptos
    r["rank_var_comparecimento"] = r.var_comparecimento_pp.rank(ascending=False).astype(int)
    r["rank_var_validos"] = r.var_validos_por_100_aptos.rank(ascending=False).astype(int)
    r["regiao"] = r.index.map(REGIAO)
    return r.sort_values("var_comparecimento_pp", ascending=False)


def main() -> dict:
    cov = covariaveis()
    faixas, cors, regs, resumo = [], [], [], {}
    for ano in (2026, 2022, 2018):
        sec = pd.read_parquet(INTERIM / f"secoes_{ano}.parquet")
        mun = pd.read_parquet(INTERIM / f"municipios_{ano}.parquet")
        sec = sec[(sec.uf != "ZZ")]
        mun = mun[(mun.uf != "ZZ")]
        zona = sec.groupby(["uf", "cd_mun", "zona"], as_index=False).sum(numeric_only=True)
        if ano == 2026:
            # 2º turno por candidato existe por município (JSON) e na amostra de seções.
            sec = sec.drop(columns=["a_2", "b_2"], errors="ignore")
            zona = zona.drop(columns=["a_2", "b_2"], errors="ignore")
        ufs = mun.groupby("uf", as_index=False).sum(numeric_only=True)
        niveis = {"secao": sec, "zona": zona, "municipio": mun, "uf": ufs}
        for nivel, df in niveis.items():
            d = preparar(df)
            if nivel != "uf":
                d = d.merge(cov, on=["uf", "cd_mun"], how="left")
            faixas.append(por_faixa(d, nivel, ano))
            cors += correlacoes(d, nivel, ano)
            if nivel in ("secao", "zona", "municipio"):
                xs = ["share_a1", "share_o1", "taxa_bn1", "taxa_abst1"]
                ctrl = ["log_pop", "pct_urbana", "alfabetizacao_15", "log_renda_pc", "pct_preta_parda"]
                regs.append(regressao(d, "dV_taxa", xs, nivel, ano))
                regs.append(regressao(d, "dV_taxa", xs + ctrl, nivel + "+controles", ano))
                regs.append(regressao(d, "dC_taxa", xs + ctrl, nivel + "+controles", ano))
                if "dA_taxa" in d:
                    regs.append(regressao(d, "dA_taxa", ["dV_taxa", "share_a1", "share_o1"] + ctrl,
                                          nivel + "+controles", ano))
                    regs.append(regressao(d, "dB_taxa", ["dV_taxa", "share_a1", "share_o1"] + ctrl,
                                          nivel + "+controles", ano))
        if ano == 2026:
            rk = ranking_uf(mun)
            rk.to_csv(TABELAS / "02_ranking_uf_comparecimento_validos.csv")
            resumo["ranking_uf_top5"] = rk.head(5)[["var_comparecimento_pp", "var_validos_por_100_aptos"]].to_dict()

    ft = pd.concat(faixas, ignore_index=True)
    ft.to_csv(TABELAS / "02_variacoes_por_faixa_de_vantagem.csv", index=False)
    ct = pd.DataFrame(cors)
    ct.to_csv(TABELAS / "02_correlacoes.csv", index=False)
    rt = pd.concat(regs, ignore_index=True)
    rt.to_csv(TABELAS / "02_regressoes.csv", index=False)
    with pd.option_context("display.width", 250, "display.max_columns", 40, "display.float_format", "{:,.3f}".format):
        print(ft[ft.nivel.isin(["secao", "municipio"])].to_string())
        print(ct[ct.ano == 2026].to_string())
        print(rt[(rt.ano == 2026)].to_string())
    resumo["ok"] = True
    salvar_json(resumo, TABELAS / "02_resumo.json")
    return resumo


if __name__ == "__main__":
    main()
