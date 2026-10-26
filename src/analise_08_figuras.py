"""Etapa 8 — Mapas e gráficos (PNG em resultados/figuras/).

Cada figura traz, no rodapé, a natureza do que mostra:
  "Dado oficial (TSE)"       contagens publicadas, sem modelo
  "Estimativa (Modelo X)"    resultado de modelo estatístico, com incerteza
  "Simulação (Modelo C)"     sorteios de cenários hipotéticos
Paleta: sequencial azul para magnitudes; divergente azul–cinza–vermelho para
grandezas com sinal; categórica em ordem fixa (Lula, Flávio, brancos/nulos,
abstenção).
"""
from __future__ import annotations

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap, Normalize, TwoSlopeNorm  # noqa: E402

from comum import FIGURAS, INTERIM, RAW, TABELAS  # noqa: E402

SUP, TINTA, TINTA2, MUDO, GRADE = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9"
COR = {"lula": "#eb6834", "flavio": "#2a78d6", "bn": "#1baf7a", "abst": "#eda100", "outros": "#6250d6"}
SEQ = LinearSegmentedColormap.from_list("seq", ["#cde2fb", "#86b6ef", "#3987e5", "#256abf", "#184f95", "#0d366b"])
DIV = LinearSegmentedColormap.from_list("div", ["#184f95", "#5598e7", "#f0efec", "#e66767", "#a32b2b"])

plt.rcParams.update({
    "figure.facecolor": SUP, "axes.facecolor": SUP, "savefig.facecolor": SUP,
    "axes.edgecolor": "#c3c2b7", "axes.labelcolor": TINTA2, "xtick.color": MUDO, "ytick.color": MUDO,
    "text.color": TINTA, "axes.grid": True, "grid.color": GRADE, "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False, "font.family": "sans-serif",
    "font.sans-serif": ["Segoe UI", "DejaVu Sans"], "font.size": 9,
})


def rodape(fig, texto):
    fig.text(0.01, 0.005, texto, fontsize=7.5, color=MUDO, ha="left", va="bottom")


def salvar(fig, nome):
    fig.savefig(FIGURAS / nome, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("figura", nome, flush=True)


def base_mapa():
    geo = gpd.read_file(RAW / "ibge" / "malha_municipios_BR.geojson")
    col = "codarea" if "codarea" in geo else geo.columns[0]
    geo["cd_ibge"] = geo[col].astype(str)
    mun = pd.read_parquet(INTERIM / "municipios_2026.parquet")
    mun = mun[mun.uf != "ZZ"].copy()
    mun["cd_ibge"] = mun.cd_ibge.astype(str)
    return geo.merge(mun, on="cd_ibge", how="inner")


def mapa(g, coluna, titulo, nome, cmap=SEQ, norm=None, rot_cor="", fonte="Dado oficial (TSE)", vmin=None, vmax=None):
    if norm is None:
        norm = Normalize(vmin if vmin is not None else g[coluna].min(), vmax if vmax is not None else g[coluna].max())
    fig, ax = plt.subplots(figsize=(7.2, 7.4))
    g.plot(column=coluna, cmap=cmap, norm=norm, ax=ax, linewidth=0,
           legend=True, legend_kwds={"shrink": 0.55, "label": rot_cor, "orientation": "vertical"},
           missing_kwds={"color": "#d9d8d2"})
    ax.set_axis_off()
    ax.set_title(titulo, loc="left", fontsize=11, color=TINTA)
    rodape(fig, f"{fonte}. Unidade: município ({len(g):,} na malha do IBGE)".replace(",", ".") + ".")
    salvar(fig, nome)


def mapas():
    g = base_mapa()
    g["dL"] = 100 * (g.a_2 - g.a_1) / g.aptos_1
    g["dF"] = 100 * (g.b_2 - g.b_1) / g.aptos_1
    g["dV"] = 100 * (g.validos_2 - g.validos_1) / g.aptos_1
    g["outros"] = 100 * g.o_1 / g.validos_1
    g["dmarg"] = 100 * ((g.a_2 - g.b_2) / g.validos_2 - (g.a_1 - g.b_1) / g.validos_1)
    q = lambda s, a, b: (np.nanpercentile(s, a), np.nanpercentile(s, b))  # noqa: E731
    lo, hi = q(g.dL, 1, 99)
    mapa(g, "dL", "Crescimento de Lula entre os turnos (votos a mais por 100 aptos)", "mapa_crescimento_lula.png",
         rot_cor="votos por 100 aptos", vmin=lo, vmax=hi)
    lo, hi = q(g.dF, 1, 99)
    mapa(g, "dF", "Variação de Flávio Bolsonaro entre os turnos (votos por 100 aptos)", "mapa_crescimento_flavio.png",
         cmap=DIV, norm=TwoSlopeNorm(0, lo, hi), rot_cor="votos por 100 aptos")
    lo, hi = q(g.dV, 1, 99)
    mapa(g, "dV", "Variação dos votos válidos entre os turnos (por 100 aptos)", "mapa_variacao_validos.png",
         cmap=DIV, norm=TwoSlopeNorm(0, min(lo, -0.1), hi), rot_cor="votos por 100 aptos")
    lo, hi = q(g.outros, 1, 99)
    mapa(g, "outros", "Votos dos candidatos eliminados no 1º turno (% dos válidos)", "mapa_votos_eliminados.png",
         rot_cor="% dos válidos no 1º turno", vmin=lo, vmax=hi)
    lim = np.nanpercentile(np.abs(g.dmarg), 99)
    mapa(g, "dmarg", "Variação da margem Lula − Flávio (pontos percentuais dos válidos)", "mapa_variacao_margem.png",
         cmap=DIV, norm=TwoSlopeNorm(0, -lim, lim), rot_cor="pontos percentuais (+ = a favor de Lula)")
    # resíduos e LISA
    p = INTERIM / "lisa_2026.parquet"
    if p.exists():
        lz = gpd.read_parquet(p)
        lim = 4
        fig, ax = plt.subplots(figsize=(7.2, 7.4))
        lz.plot(column="zr_pt", cmap=DIV, norm=TwoSlopeNorm(0, -lim, lim), ax=ax, linewidth=0, legend=True,
                legend_kwds={"shrink": 0.55, "label": "resíduo padronizado robusto (votos de Lula no 2T)"})
        ax.set_axis_off()
        ax.set_title("Resíduos do Modelo A por município (observado − esperado)", loc="left", fontsize=11)
        rodape(fig, "Estimativa (Modelo A, matriz por UF, nível município). Valores limitados a ±4.")
        salvar(fig, "mapa_residuos_modeloA.png")
        cores = {"alto-alto": "#e34948", "baixo-baixo": "#2a78d6", "alto-baixo": "#e87ba4",
                 "baixo-alto": "#86b6ef", "não significativo": "#e8e7e1"}
        fig, ax = plt.subplots(figsize=(7.2, 7.4))
        for k, c in cores.items():
            s = lz[lz.lisa == k]
            if len(s):
                s.plot(color=c, ax=ax, linewidth=0, label=f"{k} ({len(s)})")
        ax.set_axis_off()
        ax.legend(loc="lower left", frameon=False, fontsize=8)
        ax.set_title("Agrupamentos locais dos resíduos (LISA, p < 0,05 por permutação)", loc="left", fontsize=11)
        rodape(fig, "Estimativa (Modelo A + I de Moran local). Sem correção para múltiplas comparações.")
        salvar(fig, "mapa_lisa_residuos.png")


def dispersoes():
    mun = pd.read_parquet(INTERIM / "municipios_2026.parquet")
    mun = mun[(mun.uf != "ZZ") & (mun.validos_1 > 0)].copy()
    mun["dL"] = 100 * (mun.a_2 - mun.a_1) / mun.aptos_1
    mun["dF"] = 100 * (mun.b_2 - mun.b_1) / mun.aptos_1
    mun["dV"] = 100 * (mun.validos_2 - mun.validos_1) / mun.aptos_1
    mun["o1"] = 100 * mun.o_1 / mun.aptos_1
    mun["marg"] = 100 * (mun.a_1 - mun.b_1) / mun.validos_1
    s = 4 + 40 * np.sqrt(mun.aptos_1 / mun.aptos_1.max())
    pares = [("o1", "dL", "Outros candidatos no 1T (por 100 aptos)", "Δ Lula (por 100 aptos)", COR["lula"]),
             ("o1", "dF", "Outros candidatos no 1T (por 100 aptos)", "Δ Flávio (por 100 aptos)", COR["flavio"]),
             ("dV", "dL", "Δ votos válidos (por 100 aptos)", "Δ Lula (por 100 aptos)", COR["lula"]),
             ("dV", "dF", "Δ votos válidos (por 100 aptos)", "Δ Flávio (por 100 aptos)", COR["flavio"]),
             ("marg", "dV", "Margem Lula − Flávio no 1T (p.p. dos válidos)", "Δ votos válidos (por 100 aptos)", "#256abf"),
             ("marg", "dL", "Margem Lula − Flávio no 1T (p.p. dos válidos)", "Δ Lula (por 100 aptos)", COR["lula"])]
    fig, axs = plt.subplots(3, 2, figsize=(9, 11))
    for ax, (x, y, lx, ly, c) in zip(axs.ravel(), pares):
        ax.scatter(mun[x], mun[y], s=s, c=c, alpha=0.35, linewidths=0)
        w = mun.aptos_1
        b = np.polyfit(mun[x], mun[y], 1, w=np.sqrt(w))
        xs = np.linspace(np.nanpercentile(mun[x], 0.5), np.nanpercentile(mun[x], 99.5), 50)
        ax.plot(xs, np.polyval(b, xs), color=TINTA, lw=1.4)
        r = np.cov(mun[x], mun[y], aweights=w)[0, 1] / np.sqrt(np.cov(mun[x], aweights=w) * np.cov(mun[y], aweights=w))
        ax.set_xlabel(lx); ax.set_ylabel(ly)
        ax.set_title(f"r ponderado = {r:.2f}; inclinação = {b[0]:.2f}", loc="left", fontsize=9, color=TINTA2)
        ax.set_xlim(np.nanpercentile(mun[x], 0.5), np.nanpercentile(mun[x], 99.5))
        ax.set_ylim(np.nanpercentile(mun[y], 0.5), np.nanpercentile(mun[y], 99.5))
    fig.suptitle("Relações entre variações por município (área do ponto proporcional ao eleitorado)", x=0.01, ha="left", fontsize=11)
    rodape(fig, "Dado oficial (TSE); reta = mínimos quadrados ponderados pelos aptos (descritiva). Eixos cortados nos percentis 0,5–99,5.")
    fig.tight_layout(rect=(0, 0.02, 1, 0.97))
    salvar(fig, "dispersao_variacoes_municipios.png")


def matrizes():
    t = pd.concat([pd.read_csv(TABELAS / f"03_matriz_transicao_nacional{s}.csv")
                   for s in ("_2026", "_2022_2018")])
    ordem_o = ["a_1", "b_1", "o_1", "bn_1", "abst_1"]
    ordem_d = ["a_2", "b_2", "bn_2", "abst_2"]
    nomes = {2026: ("Lula", "Flávio"), 2022: ("Lula", "J. Bolsonaro"), 2018: ("Haddad", "J. Bolsonaro")}
    fig, axs = plt.subplots(1, 3, figsize=(14, 4.8))
    for ax, ano in zip(axs, (2026, 2022, 2018)):
        g = t[(t.ano == ano) & (t.nivel == "secao") & (t.origens == "base")].set_index(["origem", "destino"])
        M = np.array([[g.loc[(o, d), "taxa"] for d in ordem_d] for o in ordem_o])
        lo = np.array([[g.loc[(o, d), "taxa_ic95_inf"] for d in ordem_d] for o in ordem_o])
        hi = np.array([[g.loc[(o, d), "taxa_ic95_sup"] for d in ordem_d] for o in ordem_o])
        ax.imshow(M, cmap=SEQ, vmin=0, vmax=1)
        for i in range(5):
            for j in range(4):
                cor = "white" if M[i, j] > 0.55 else TINTA
                ax.text(j, i, f"{100*M[i,j]:.1f}%\n[{100*lo[i,j]:.1f}–{100*hi[i,j]:.1f}]",
                        ha="center", va="center", fontsize=7.5, color=cor)
        a, b = nomes[ano]
        ax.set_xticks(range(4), [a, b, "Br./nulos", "Abstenção"])
        ax.set_yticks(range(5), [a, b, "Outros", "Br./nulos", "Abstenção"])
        ax.set_xlabel("2º turno"); ax.set_ylabel("1º turno")
        ax.set_title(str(ano), loc="left", fontsize=11)
        ax.grid(False)
    fig.suptitle("Taxas de transição estimadas (linha soma 100%) e intervalos de 95% (bootstrap por município)",
                 x=0.01, ha="left", fontsize=11)
    rodape(fig, "Estimativa (Modelo A: inferência ecológica por UF, amostra de seções). Intervalos não incluem o erro da hipótese de constância.")
    fig.tight_layout(rect=(0, 0.03, 1, 0.95))
    salvar(fig, "matrizes_transicao_modeloA.png")


def teste_secao7():
    linhas = []
    for ano in (2026, 2022, 2018):
        for nivel in ("secao", "municipio"):
            p = TABELAS / f"03_teste_migracao_{ano}_{nivel}.csv"
            if p.exists():
                linhas.append(pd.read_csv(p))
    if not linhas:
        return
    t = pd.concat(linhas)
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
    cores_ano = {2026: "#2a78d6", 2022: "#eb6834", 2018: "#1baf7a"}
    legenda = {2026: "2026: Flávio Bolsonaro e Lula", 2022: "2022: Jair Bolsonaro e Lula",
               2018: "2018: Jair Bolsonaro e Haddad"}
    for ax, h, tit in zip(axs, ["direita_para_pt", "pt_para_direita"],
                          ["Teto: finalista de direita (1T) → finalista do PT (2T)",
                           "Teto: finalista do PT (1T) → finalista de direita (2T)"]):
        for ano in (2026, 2022, 2018):
            g = t[(t.hipotese == h) & (t.ano == ano) & (t.nivel == "secao")].sort_values("teto")
            if len(g):
                y = -np.log10(g.p_conjunto.clip(lower=1e-12))
                ax.plot(100 * g.teto, y, marker="o", ms=6, lw=2, color=cores_ano[ano], label=legenda[ano])
        ax.axhline(-np.log10(0.05), color=MUDO, lw=1, ls="--")
        ax.text(10, -np.log10(0.05) + 0.2, "p = 0,05", ha="right", fontsize=7.5, color=MUDO)
        ax.set_xlabel("teto imposto em todas as UFs (%)")
        ax.set_title(tit, loc="left", fontsize=10)
    axs[0].set_ylabel("−log10(p) do teste conjunto (maior = mais incompatível)")
    axs[1].legend(frameon=False, title="eleição e finalistas", loc="upper right")
    rodape(fig, "Estimativa (Modelo A, amostra de seções). Teste F de quase-verossimilhança somado nas UFs em que o teto altera o ajuste.")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    salvar(fig, "teste_migracao_minima.png")


def monte_carlo():
    p = INTERIM / "monte_carlo_sorteios.parquet"
    if not p.exists():
        return
    d = pd.read_parquet(p)
    fams = list(dict.fromkeys(d.familia))
    rot = {f: f.split("_", 1)[0] for f in fams}
    cores = ["#2a78d6", "#eb6834", "#1baf7a", "#6250d6"]
    fig, axs = plt.subplots(1, 3, figsize=(14, 4.2))
    for k, f in enumerate(fams):
        g = d[d.familia == f]
        axs[0].hist(1000 * g.dev_por_eleitor, bins=80, histtype="step", lw=2, color=cores[k], label=rot[f], density=True)
        axs[1].hist(100 * g.cal_FL, bins=80, histtype="step", lw=2, color=cores[k], label=rot[f], density=True)
        axs[2].hist(g.erro_bruto_lula_pp, bins=80, histtype="step", lw=2, color=cores[k], label=rot[f], density=True)
    import json
    ref = json.loads((TABELAS / "05_monte_carlo_parametros.json").read_text(encoding="utf-8"))
    axs[0].axvline(1000 * ref["dev_ref_matriz_nacional_unica"], color=TINTA, lw=1.2, ls="--")
    axs[0].text(1000 * ref["dev_ref_matriz_nacional_unica"], axs[0].get_ylim()[1] * 0.95, " melhor ajuste\n matriz única", fontsize=7.5)
    axs[0].set_xlabel("deviance por 1.000 eleitores (menor = melhor)")
    axs[0].set_xlim(right=np.percentile(1000 * d.dev_por_eleitor, 99))
    axs[1].set_xlabel("taxa Flávio(1T)→Lula(2T) após calibração (%)")
    axs[2].set_xlabel("erro do sorteio bruto no total de Lula (p.p. dos aptos)")
    axs[2].axvline(0, color=TINTA, lw=1)
    for ax in axs:
        ax.set_yticks([])
    axs[0].legend(frameon=False)
    fig.suptitle("Famílias de cenários: ajuste territorial e taxas implícitas (20.000 sorteios por família)", x=0.01, ha="left", fontsize=11)
    rodape(fig, "Simulação (Modelo C). Densidades dependem da largura escolhida para cada família; não são probabilidades das hipóteses.")
    fig.tight_layout(rect=(0, 0.03, 1, 0.94))
    salvar(fig, "monte_carlo_familias.png")


def ranking_uf():
    r = pd.read_csv(TABELAS / "02_ranking_uf_comparecimento_validos.csv").sort_values("var_comparecimento_pp")
    fig, axs = plt.subplots(1, 2, figsize=(10, 7), sharey=True)
    axs[0].barh(r.uf, r.var_comparecimento_pp, color=np.where(r.var_comparecimento_pp >= 0, "#2a78d6", "#e34948"), height=0.7)
    axs[0].set_xlabel("variação do comparecimento (p.p. dos aptos)")
    axs[1].barh(r.uf, r.var_validos_por_100_aptos, color=np.where(r.var_validos_por_100_aptos >= 0, "#2a78d6", "#e34948"), height=0.7)
    axs[1].set_xlabel("variação dos votos válidos (por 100 aptos)")
    for ax in axs:
        ax.axvline(0, color="#c3c2b7", lw=1)
        ax.grid(axis="y", visible=False)
    fig.suptitle("UFs ordenadas pela variação do comparecimento entre os turnos", x=0.01, ha="left", fontsize=11)
    rodape(fig, "Dado oficial (TSE).")
    fig.tight_layout(rect=(0, 0.02, 1, 0.96))
    salvar(fig, "ranking_uf_comparecimento_validos.png")


def bayes():
    p = TABELAS / "04_bayes_matriz_nacional.csv"
    if not p.exists():
        return
    t = pd.read_csv(p)
    celulas = [("b_1", "a_2", "Flávio→Lula"), ("a_1", "b_2", "Lula→Flávio"), ("o_1", "a_2", "Outros→Lula"),
               ("o_1", "b_2", "Outros→Flávio"), ("bn_1", "a_2", "Br/nulos→Lula"), ("abst_1", "a_2", "Abstenção→Lula"),
               ("abst_1", "b_2", "Abstenção→Flávio")]
    priors = list(dict.fromkeys(t.prior))
    cores = ["#2a78d6", "#eb6834", "#1baf7a"]
    fig, ax = plt.subplots(figsize=(9, 4.5))
    for k, pr in enumerate(priors):
        for j, (o, d, n) in enumerate(celulas):
            g = t[(t.prior == pr) & (t.origem == o) & (t.destino == d)].iloc[0]
            y = j + (k - 1) * 0.22
            ax.plot([100 * g.ic95_inf, 100 * g.ic95_sup], [y, y], color=cores[k], lw=2)
            ax.plot(100 * g.media, y, "o", color=cores[k], ms=6, label=pr if j == 0 else None)
    ax.set_yticks(range(len(celulas)), [c[2] for c in celulas])
    ax.invert_yaxis()
    ax.set_xlabel("taxa nacional de transição (%) — média e intervalo de credibilidade de 95%")
    ax.legend(frameon=False, title="prior")
    ax.set_title("Sensibilidade às distribuições a priori (Modelo B)", loc="left", fontsize=11)
    rodape(fig, "Estimativa (Modelo B, bayesiano hierárquico, amostra de seções do 2T).")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    salvar(fig, "bayes_sensibilidade_priors.png")


def legislativo():
    p = INTERIM / "legislativo_secao_2026.parquet"
    if not p.exists():
        return
    leg = pd.read_parquet(p)
    sec = pd.read_parquet(INTERIM / "secoes_2026.parquet", columns=["uf", "cd_mun", "zona", "secao", "a_1", "b_1", "validos_1"])
    d = sec.merge(leg, on=["uf", "cd_mun", "zona", "secao"])
    d["dep_validos"] = d[[c for c in d.columns if c.startswith("dep_") and c not in ("dep_bn", "dep_dir_estrita")]].sum(1)
    d = d[(d.dep_validos > 20) & (d.validos_1 > 20)]
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.8))
    for ax, y, ny in zip(axs, ["b_1", "a_1"], ["Flávio no 1T (% válidos)", "Lula no 1T (% válidos)"]):
        hb = ax.hexbin(100 * d.dep_pl / d.dep_validos, 100 * d[y] / d.validos_1, gridsize=70, cmap=SEQ, bins="log", mincnt=1)
        ax.plot([0, 100], [0, 100], color=MUDO, lw=1, ls="--")
        ax.set_xlabel("PL para deputado federal (% dos válidos)")
        ax.set_ylabel(ny)
        ax.set_xlim(0, 80); ax.set_ylim(0, 100)
        fig.colorbar(hb, ax=ax, label="seções (escala log)")
    fig.suptitle("Voto no PL para a Câmara × voto presidencial, por seção (1º turno)", x=0.01, ha="left", fontsize=11)
    rodape(fig, f"Dado oficial (TSE). Linha tracejada: igualdade. {len(d):,} seções no Brasil com mais de 20 votos válidos.".replace(",", "."))
    fig.tight_layout(rect=(0, 0.03, 1, 0.95))
    salvar(fig, "legislativo_pl_vs_presidente.png")


def main():
    for f in (mapas, dispersoes, matrizes, teste_secao7, monte_carlo, ranking_uf, bayes, legislativo):
        try:
            f()
        except Exception as e:  # uma figura com problema não impede as outras
            print("ERRO em", f.__name__, repr(e), flush=True)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        for nome in sys.argv[1:]:
            globals()[nome]()
    else:
        main()
