"""Etapa 10 — Dados do painel interativo (docs/, publicado no GitHub Pages).

Gera dois arquivos JavaScript (carregáveis também abrindo o HTML direto do
disco, sem servidor):
  docs/dados.js     window.DADOS  = tabelas e resultados resumidos
  docs/mapa.js      window.MAPA   = contornos dos municípios e das UFs,
                       projetados (SIRGAS 2000 / Brazil Polyconic, EPSG 5880)
                       e simplificados (tolerância de 1,5 km), como caminhos SVG
Tudo vem das tabelas de resultados/tabelas e das bases de interim/; nada é
recalculado com outro método.
"""
from __future__ import annotations

import json

import geopandas as gpd
import numpy as np
import pandas as pd

from comum import DERIVADOS, INTERIM, PROJETO, RAW, REGIAO, TABELAS

SAIDA = PROJETO / "docs"
UF_IBGE = {"11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA", "16": "AP", "17": "TO",
           "21": "MA", "22": "PI", "23": "CE", "24": "RN", "25": "PB", "26": "PE", "27": "AL",
           "28": "SE", "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP", "41": "PR",
           "42": "SC", "43": "RS", "50": "MS", "51": "MT", "52": "GO", "53": "DF"}
NOMES = {2026: ("Lula", "Flávio Bolsonaro"), 2022: ("Lula", "Jair Bolsonaro"), 2018: ("Haddad", "Jair Bolsonaro")}


def r(x, n=4):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return None
    return round(float(x), n)


def registros(df, casas=4):
    out = []
    for rec in df.to_dict(orient="records"):
        out.append({k: (r(v, casas) if isinstance(v, (float, np.floating)) else
                        int(v) if isinstance(v, (np.integer,)) else v) for k, v in rec.items()})
    return out


def caminho(geom, transf):
    partes = []
    polys = [geom] if geom.geom_type == "Polygon" else list(geom.geoms)
    for p in polys:
        for anel in [p.exterior] + list(p.interiors):
            xy = np.asarray(anel.coords)
            if len(xy) < 4:
                continue
            pts = transf(xy)
            d = "M" + "L".join(f"{x:.0f} {y:.0f}" for x, y in pts) + "Z"
            partes.append(d)
    return "".join(partes)


def mapa():
    geo = gpd.read_file(RAW / "ibge" / "malha_municipios_BR.geojson")
    col = "codarea" if "codarea" in geo else geo.columns[0]
    geo["cd_ibge"] = geo[col].astype(str)
    geo = geo.to_crs(5880)
    geo["uf"] = geo.cd_ibge.str[:2].map(UF_IBGE)
    xmin, ymin, xmax, ymax = geo.total_bounds
    larg = 1000.0
    esc = larg / (xmax - xmin)
    alt = (ymax - ymin) * esc

    def transf(xy):
        return np.column_stack([(xy[:, 0] - xmin) * esc, (ymax - xy[:, 1]) * esc])

    mun_s = geo.copy()
    mun_s["geometry"] = mun_s.geometry.simplify(1500, preserve_topology=True)
    muns = {row.cd_ibge: caminho(row.geometry, transf) for row in mun_s.itertuples()}
    ufs = geo.dissolve("uf")
    ufs["geometry"] = ufs.geometry.simplify(2500, preserve_topology=True)
    contornos = {uf: caminho(g, transf) for uf, g in zip(ufs.index, ufs.geometry)}
    return {"largura": larg, "altura": round(alt, 1), "municipios": muns, "ufs": contornos}


def municipios():
    m = pd.read_parquet(INTERIM / "municipios_2026.parquet")
    m = m[m.uf != "ZZ"].copy()
    res = pd.read_parquet(INTERIM / "residuos_2026_municipio.parquet")[["uf", "cd_mun", "zr_pt", "q_pt"]]
    m = m.merge(res, on=["uf", "cd_mun"], how="left")
    t = pd.DataFrame({
        "id": m.cd_ibge.astype(str), "uf": m.uf, "nome": m.nm_municipio,
        "aptos": m.aptos_1.astype(int),
        "l1": 100 * m.a_1 / m.validos_1, "f1": 100 * m.b_1 / m.validos_1,
        "l2": 100 * m.a_2 / m.validos_2, "f2": 100 * m.b_2 / m.validos_2,
        "o1": 100 * m.o_1 / m.validos_1,
        "dL": 100 * (m.a_2 - m.a_1) / m.aptos_1, "dF": 100 * (m.b_2 - m.b_1) / m.aptos_1,
        "dV": 100 * (m.validos_2 - m.validos_1) / m.aptos_1,
        "dC": 100 * (m.comp_2 / m.aptos_2 - m.comp_1 / m.aptos_1),
        "dBN": 100 * (m.bn_2 - m.bn_1) / m.aptos_1,
        "dM": 100 * ((m.a_2 - m.b_2) / m.validos_2 - (m.a_1 - m.b_1) / m.validos_1),
        "z": m.zr_pt, "q": m.q_pt,
    })
    cols = ["id", "uf", "nome", "aptos", "l1", "f1", "l2", "f2", "o1", "dL", "dF", "dV", "dC", "dBN", "dM", "z", "q"]
    linhas = []
    for rec in t[cols].itertuples(index=False):
        linhas.append([rec[0], rec[1], rec[2], int(rec[3])] + [r(x, 2) if i < 12 else r(x, 3)
                                                               for i, x in enumerate(rec[4:])])
    return {"colunas": cols, "linhas": linhas}


def matrizes():
    t = pd.concat([pd.read_csv(TABELAS / f"03_matriz_transicao_nacional{s}.csv") for s in ("_2026", "_2022_2018")])
    t = t[["ano", "nivel", "origens", "origem", "destino", "taxa", "taxa_ic95_inf", "taxa_ic95_sup",
           "votos", "votos_ic95_inf", "votos_ic95_sup"]]
    return registros(t, 5)


def faixas():
    f = pd.read_csv(TABELAS / "02_variacoes_por_faixa_de_vantagem.csv")
    f = f[f.nivel.isin(["secao", "municipio"])]
    return registros(f[["ano", "nivel", "faixa", "unidades", "pct_aptos", "pct_dV_nacional", "dV_por_100_aptos",
                        "dC_por_100_aptos", "dBN_por_100_aptos", "dA_por_100_aptos", "dB_por_100_aptos"]], 3)


def bn_regiao():
    out = []
    for ano in (2026, 2022, 2018):
        s = pd.read_parquet(INTERIM / f"secoes_{ano}.parquet", columns=["uf", "comp_1", "comp_2", "bn_1", "bn_2"])
        s = s[s.uf != "ZZ"]
        g = s.assign(reg=s.uf.map(REGIAO)).groupby("reg").sum(numeric_only=True)
        for reg, x in g.iterrows():
            out.append({"ano": ano, "regiao": reg, "bn1": r(100 * x.bn_1 / x.comp_1, 2), "bn2": r(100 * x.bn_2 / x.comp_2, 2)})
    return out


def histograma(v, bins):
    h, e = np.histogram(np.clip(v, bins[0], bins[-1] - 1e-9), bins=bins)
    return {"bordas": [r(x, 5) for x in e], "contagens": h.tolist()}


def monte_carlo():
    d = pd.read_parquet(INTERIM / "monte_carlo_sorteios.parquet")
    rs = pd.read_csv(TABELAS / "05_monte_carlo_resumo.csv")
    par = json.loads((TABELAS / "05_monte_carlo_parametros.json").read_text(encoding="utf-8"))
    fams = {}
    for f, g in d.groupby("familia", sort=False):
        fams[f] = {
            "dev": histograma(1000 * g.dev_por_eleitor.to_numpy(), np.linspace(2, 12, 81)),
            "FL": histograma(100 * g.cal_FL.to_numpy(), np.linspace(0, 20, 81)),
            "erro": histograma(g.erro_bruto_lula_pp.to_numpy(), np.linspace(-10, 4, 71)),
        }
    return {"familias": fams, "resumo": registros(rs, 5), "dev_ref": 1000 * par["dev_ref_matriz_nacional_unica"],
            "definicoes": par["familias"]}


def legislativo():
    leg = pd.read_parquet(INTERIM / "legislativo_secao_2026.parquet")
    sec = pd.read_parquet(INTERIM / "secoes_2026.parquet", columns=["uf", "cd_mun", "zona", "secao", "a_1", "b_1", "validos_1"])
    d = sec.merge(leg, on=["uf", "cd_mun", "zona", "secao"])
    dep = [c for c in d.columns if c.startswith("dep_") and c not in ("dep_bn", "dep_dir_estrita")]
    d["dv"] = d[dep].sum(1)
    d = d[(d.dv > 20) & (d.validos_1 > 20)]
    x = 100 * d.dep_pl / d.dv
    bins = np.linspace(0, 80, 41)
    out = {}
    for nome, y in (("flavio", 100 * d.b_1 / d.validos_1), ("lula", 100 * d.a_1 / d.validos_1)):
        h, _, _ = np.histogram2d(np.clip(x, 0, 79.99), np.clip(y, 0, 99.99), bins=[bins, np.linspace(0, 100, 51)])
        out[nome] = h.astype(int).T.tolist()  # linhas = y
    cad = pd.read_csv(TABELAS / "06_votos_cadeiras_partidos.csv")
    cad = cad[cad.votos > 0]
    split = pd.read_csv(TABELAS / "06_voto_dividido_inferencia_ecologica.csv")
    hist = pd.read_csv(TABELAS / "06_historico_partido_vs_presidente.csv")
    comb = pd.read_csv(TABELAS / "06_combinacoes_divergentes_secao.csv")
    resumo = json.loads((TABELAS / "06_resumo.json").read_text(encoding="utf-8"))
    return {"hist2d": out, "x_bordas": bins.tolist(), "y_bordas": np.linspace(0, 100, 51).tolist(),
            "secoes": int(len(d)),
            "cadeiras": registros(cad[["cargo", "partido", "sigla", "bloco", "votos", "pct_votos", "eleitos", "pct_cadeiras"]], 3),
            "split": registros(split, 4), "historico": registros(hist, 4), "combinacoes": registros(comb, 3),
            "resumo": {k: r(v, 4) if isinstance(v, float) else v for k, v in resumo.items()}}


def anomalias():
    dist = pd.read_csv(TABELAS / "07_distribuicao_residuos_por_ano.csv")
    mor = pd.read_csv(TABELAS / "07_moran_por_ano.csv")
    urna = pd.read_csv(TABELAS / "07_residuo_por_modelo_urna.csv")
    top = pd.read_csv(TABELAS / "07_maiores_residuos_municipios_2026.csv")
    top = top[top.q_pt < 0.05][["uf", "nm_municipio", "aptos_1", "lula_1T_pct", "lula_2T_pct", "zr_pt", "q_pt",
                                "dcomp_pp", "dbn_pp", "aptos_mudaram"]]
    hists = {}
    for ano in (2026, 2022, 2018):
        z = pd.read_parquet(INTERIM / f"residuos_{ano}_municipio.parquet").zr_pt.to_numpy()
        hists[ano] = histograma(z, np.linspace(-8, 8, 65))
    ext = pd.read_csv(TABELAS / "07_extremos_comparecimento_2026.csv")
    return {"distribuicao": registros(dist, 4), "moran": registros(mor, 4), "urna": registros(urna, 4),
            "sinalizados": registros(top, 3), "hist": hists, "extremos_comparecimento": registros(ext, 3)}


def testes():
    linhas = []
    for ano in (2026, 2022, 2018):
        for nivel in ("secao", "municipio"):
            t = pd.read_csv(TABELAS / f"03_teste_migracao_{ano}_{nivel}.csv")
            linhas += registros(t[["ano", "nivel", "hipotese", "descricao_hipotese", "teto", "chi2_total", "p_conjunto",
                                   "ufs_rejeitadas_5pct", "ufs_rejeitadas_bonferroni", "ufs_maior_incompatibilidade"]], 6)
    por_uf = pd.read_csv(TABELAS / "03_testes_migracao_por_uf_2026.csv")
    por_uf = por_uf[["uf", "nivel", "hipotese", "teto", "taxa_livre", "F", "p", "phi"]].copy()
    por_uf["hipotese"] = por_uf.hipotese.replace({"flavio_para_lula": "direita_para_pt", "lula_para_flavio": "pt_para_direita"})
    ap = pd.read_csv(TABELAS / "03c_amapa_todas_secoes.csv")
    return {"conjunto": linhas, "por_uf": registros(por_uf, 5), "amapa": registros(ap, 5)}


def main():
    SAIDA.mkdir(exist_ok=True)
    rec = pd.read_csv(TABELAS / "01_reconciliacao_nacional.csv", index_col=0)
    qm = pd.read_csv(TABELAS / "01_quantidades_minimas.csv")
    lim = pd.read_csv(TABELAS / "01_limites_municipio.csv")
    rk = pd.read_csv(TABELAS / "02_ranking_uf_comparecimento_validos.csv")
    reg = pd.read_csv(TABELAS / "02_regressoes.csv")
    cor = pd.read_csv(TABELAS / "02_correlacoes.csv")
    sens = pd.read_csv(TABELAS / "03b_sensibilidade_estratos.csv")
    bay = pd.read_csv(TABELAS / "04_bayes_matriz_nacional.csv")
    bdiag = json.loads((TABELAS / "04_bayes_diagnosticos.json").read_text(encoding="utf-8"))
    hist = pd.read_csv(TABELAS / "09_comparacao_historica.csv")
    conf = pd.read_csv(TABELAS / "01_conferencia_oficial.csv")
    manifesto = pd.read_csv(PROJETO / "integridade" / "manifesto_downloads.csv")
    manifesto = manifesto.drop_duplicates("url", keep="last")
    dados = {
        "gerado_em": pd.Timestamp.now(tz="America/Sao_Paulo").strftime("%d/%m/%Y %H:%M"),
        "reconciliacao": [{"indicador": i, **{k: r(v, 3) for k, v in row.items()}} for i, row in rec.iterrows()],
        "conferencia": registros(conf, 0),
        "quantidades_minimas": registros(qm, 0),
        "limites_municipio": registros(lim, 5),
        "ufs": registros(rk.rename(columns={rk.columns[0]: "uf"}), 3),
        "governador_2t": ["AC", "DF", "TO"],
        "faixas": faixas(),
        "bn_regiao": bn_regiao(),
        "regressoes": registros(reg[reg.ano == 2026], 5),
        "correlacoes": registros(cor, 4),
        "municipios": municipios(),
        "matrizes": matrizes(),
        "sensibilidade": registros(sens, 5),
        "bayes": registros(bay, 5),
        "bayes_diag": bdiag,
        "testes": testes(),
        "monte_carlo": monte_carlo(),
        "legislativo": legislativo(),
        "anomalias": anomalias(),
        "historico": registros(hist, 4),
        "fontes": registros(manifesto[["url", "acesso_utc", "tamanho_bytes", "sha256", "last_modified_servidor"]], 0),
        "nomes": {str(k): v for k, v in NOMES.items()},
    }
    js = "window.DADOS = " + json.dumps(dados, ensure_ascii=False, separators=(",", ":"), allow_nan=False) + ";\n"
    (SAIDA / "dados.js").write_text(js, encoding="utf-8")
    m = mapa()
    (SAIDA / "mapa.js").write_text("window.MAPA = " + json.dumps(m, ensure_ascii=False, separators=(",", ":")) + ";\n",
                                   encoding="utf-8")
    for f in ("dados.js", "mapa.js"):
        print(f, round((SAIDA / f).stat().st_size / 1e6, 2), "MB")


if __name__ == "__main__":
    main()
