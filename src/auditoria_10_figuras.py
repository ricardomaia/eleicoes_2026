"""Auditoria 10 — Figuras comparativas (resultados/auditoria/figuras/).

  aud_fronteira_heterogeneidade.png   fração mínima do eleitorado fora da matriz comum × taxa
                                      Flávio→Lula imposta (média nacional e UFs extremas)
  aud_sintetico_vies_FL.png           estimativa × verdade da taxa Flávio→Lula por cenário sintético
  aud_sintetico_bn_abst.png           idem para brancos/nulos→Lula e abstenção→Lula
  aud_intervalos_FL.png               taxa Flávio→Lula nacional com intervalos de todos os métodos
  aud_limites_hipoteses.png           limites identificados sob S0–S4 (municípios)
  aud_amapa_perfil_troca.png          Amapá: o que o modelo troca por migração
  aud_parte_todo.png                  correlação Δválidos × ΔLula observada e sob a nula aritmética
Cada figura indica se mostra dado oficial, estimativa ou simulação.
"""
from __future__ import annotations

import json

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from auditoria_comum import FIG, TAB
from comum import TABELAS

matplotlib.use("Agg")
plt.rcParams.update({"font.size": 9, "axes.titlesize": 10, "figure.dpi": 130})


def fronteira():
    try:
        n = pd.read_csv(TAB / "01_fronteira_heterogeneidade_nacional.csv")
        u = pd.read_csv(TAB / "01_fronteira_heterogeneidade_por_uf.csv")
    except FileNotFoundError:
        return
    n = n.dropna(subset=["teto_FL"]).sort_values("teto_FL")
    fig, ax = plt.subplots(figsize=(7, 4.2))
    for uf, g in u[u.status == 0].dropna(subset=["teto_FL"]).groupby("uf"):
        g = g.sort_values("teto_FL")
        ax.plot(100 * g.teto_FL, 100 * g.fracao_minima_desviante, color="0.8", lw=0.8)
    ax.plot(100 * n.teto_FL, 100 * n.fracao_minima_desviante_media_pond, "o-", color="C3", lw=2, label="média nacional ponderada")
    for uf in ("AP", "SP", "BA"):
        g = u[(u.uf == uf) & (u.status == 0)].dropna(subset=["teto_FL"]).sort_values("teto_FL")
        if len(g):
            ax.plot(100 * g.teto_FL, 100 * g.fracao_minima_desviante, "s--", lw=1, label=uf)
    ax.set_xlabel("taxa Flávio→Lula imposta à matriz comum da UF (%)")
    ax.set_ylabel("fração mínima do eleitorado com comportamento\nfora da matriz comum (%)")
    ax.set_title("Fronteira de heterogeneidade (programa linear; amostra de seções) — estimativa")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / "aud_fronteira_heterogeneidade.png")
    plt.close(fig)


def sintetico():
    try:
        r = pd.read_csv(TAB / "02_sintetico_resumo_celulas.csv")
    except FileNotFoundError:
        return
    ordem = ["A", "B1_5", "B1_10", "B1_15", "B2_5", "B2_10", "B2_15", "C", "D", "E", "F"]
    for cel, nome, arq in [(("b_1", "a_2"), "Flávio→Lula", "aud_sintetico_vies_FL.png")]:
        g = r[(r.origem == cel[0]) & (r.destino == cel[1]) & (r.n_sec == 10000) & r.cenario.isin(ordem)].set_index("cenario").loc[ordem]
        fig, ax = plt.subplots(figsize=(7.5, 4))
        x = np.arange(len(g))
        ax.bar(x - 0.2, 100 * g.verdade_media, 0.4, label="taxa verdadeira (simulação)", color="0.5")
        ax.bar(x + 0.2, 100 * g.estimada_media, 0.4, label="estimada pelo Modelo A", color="C0")
        ax.errorbar(x + 0.2, 100 * g.estimada_media, yerr=100 * 1.96 * g.vies_ep_mc, fmt="none", color="k", lw=0.8)
        ax.set_xticks(x); ax.set_xticklabels(g.index, rotation=30)
        ax.set_ylabel(f"taxa {nome} (%)")
        ax.set_title("Dados sintéticos (10.000 seções, 12 repetições): verdade × estimativa — simulação")
        ax.legend()
        fig.tight_layout(); fig.savefig(FIG / arq); plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.8))
    for ax, (o, nome) in zip(axes, [("bn_1", "brancos/nulos→Lula"), ("abst_1", "abstenção→Lula")]):
        g = r[(r.origem == o) & (r.destino == "a_2") & (r.n_sec == 10000) & r.cenario.isin(ordem)].set_index("cenario").loc[ordem]
        x = np.arange(len(g))
        ax.bar(x - 0.2, 100 * g.verdade_media, 0.4, label="verdadeira", color="0.5")
        ax.bar(x + 0.2, 100 * g.estimada_media, 0.4, label="estimada", color="C0")
        ax.set_xticks(x); ax.set_xticklabels(g.index, rotation=40, fontsize=7)
        ax.set_title(nome); ax.set_ylabel("%")
    axes[0].legend(fontsize=8)
    fig.suptitle("Dados sintéticos: conversão de não votantes — simulação", fontsize=10)
    fig.tight_layout(); fig.savefig(FIG / "aud_sintetico_bn_abst.png"); plt.close(fig)


def intervalos():
    linhas = []
    pub = pd.read_csv(TABELAS / "03_matriz_transicao_nacional_2026.csv")
    p = pub[(pub.nivel == "secao") & (pub.origens == "base") & (pub.origem == "b_1") & (pub.destino == "a_2")].iloc[0]
    linhas.append(("Modelo A, bootstrap 200 (publicado)", p.taxa, p.taxa_ic95_inf, p.taxa_ic95_sup))
    try:
        b = pd.read_csv(TAB / "03_bootstrap_1000.csv")
        b = b[(b.origem == "b_1") & (b.destino == "a_2")].iloc[0]
        linhas.append(("Modelo A, bootstrap 1000 por município (percentil)", b.taxa, b.ic95_percentil_inf_municipio, b.ic95_percentil_sup_municipio))
        linhas.append(("Modelo A, bootstrap 1000 por município (básico)", b.taxa, b.ic95_basico_inf_municipio, b.ic95_basico_sup_municipio))
        linhas.append(("Modelo A, bootstrap 1000 por seção", b.taxa, b.ic95_percentil_inf_secao, b.ic95_percentil_sup_secao))
    except FileNotFoundError:
        pass
    try:
        g = pd.read_csv(TAB / "01_goodman_wls_nacional.csv")
        for _, r in g[(g.origem == "b_1") & (g.destino == "a_2")].iterrows():
            linhas.append((f"Goodman sem restrições, EP por município ({r.nivel})", r.coef_nacional, r.ic95_inf, r.ic95_sup))
    except FileNotFoundError:
        pass
    for pr in ("neutra", "fidelidade_alta", "troca_alta"):
        try:
            b = pd.read_csv(TAB / f"04_bayes_matriz_nacional_{pr}.csv")
            b = b[(b.origem == "b_1") & (b.destino == "a_2")].iloc[0]
            linhas.append((f"Modelo B (1000+1000), prior {pr}", b.media, b.ic95_inf, b.ic95_sup))
        except FileNotFoundError:
            pass
    try:
        c = pd.read_csv(TAB / "05_taxas_nacionais_por_modelo.csv")
        for m in ("M1", "M2"):
            r = c[(c.modelo == m) & (c.origem == "b_1") & (c.destino == "a_2")].iloc[0]
            linhas.append((f"{m} (taxas dependentes do contexto)", r.taxa, r.ic95_inf, r.ic95_sup))
    except FileNotFoundError:
        pass
    try:
        l = pd.read_csv(TAB / "01_limites_lp_conjuntos_hipoteses.csv")
        for _, r in l[(l.nivel == "secao (amostra)") & (l.origem == "b_1") & (l.destino == "a_2")].iterrows():
            linhas.append((f"conjunto identificado {r.conjunto}", np.nan, r.min_taxa_expandida, r.max_taxa_expandida))
    except FileNotFoundError:
        pass
    fig, ax = plt.subplots(figsize=(8, 0.35 * len(linhas) + 1.5))
    for k, (nome, est, lo, hi) in enumerate(linhas):
        y = len(linhas) - k
        ax.plot([100 * lo, 100 * hi], [y, y], color="C0" if np.isfinite(est) else "C3", lw=2)
        if np.isfinite(est):
            ax.plot(100 * est, y, "o", color="C0")
        ax.text(-4.5, y, nome, ha="right", va="center", fontsize=7.5)
    ax.axvline(0, color="0.7", lw=0.8)
    ax.set_yticks([]); ax.set_xlim(-4.5, 20)
    ax.set_xscale("symlog", linthresh=1)
    ax.set_xlabel("taxa Flávio(1T)→Lula(2T) nacional (%), eixo logarítmico acima de 1%")
    ax.set_title("Mesma quantidade, métodos diferentes: estimativas (azul) e conjuntos identificados (vermelho)")
    fig.tight_layout(); fig.savefig(FIG / "aud_intervalos_FL.png", bbox_inches="tight"); plt.close(fig)


def limites():
    try:
        l = pd.read_csv(TAB / "01_limites_lp_conjuntos_hipoteses.csv")
    except FileNotFoundError:
        return
    l = l[l.nivel == "municipio (todos)"]
    cel = [("b_1", "a_2"), ("o_1", "a_2"), ("bn_1", "a_2"), ("abst_1", "a_2")]
    nomes = ["Flávio→Lula", "outros→Lula", "brancos/nulos→Lula", "abstenção→Lula"]
    fig, axes = plt.subplots(1, 4, figsize=(11, 3.5), sharey=False)
    for ax, (o, d), nome in zip(axes, cel, nomes):
        g = l[(l.origem == o) & (l.destino == d)]
        for k, (_, r) in enumerate(g.iterrows()):
            ax.plot([100 * r.min_taxa_soma, 100 * r.max_taxa_soma], [k, k], lw=3, color="C3")
        ax.set_yticks(range(len(g))); ax.set_yticklabels([c[:3] for c in g.conjunto], fontsize=8)
        ax.set_title(nome, fontsize=9); ax.set_xlabel("taxa (%)")
    fig.suptitle("Conjuntos identificados por município sob hipóteses S0–S4 (programação linear) — limites, não estimativas", fontsize=10)
    fig.tight_layout(); fig.savefig(FIG / "aud_limites_hipoteses.png"); plt.close(fig)


def amapa():
    try:
        p = pd.read_csv(TAB / "07_amapa_perfil_troca.csv")
    except FileNotFoundError:
        return
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.6))
    for conj, g in p.groupby("conjunto"):
        axes[0].plot(100 * g.FL_fixo, 100 * g.L_abst, "o-", label=conj)
        axes[1].plot(100 * g.FL_fixo, g.dev_escalada_phi, "o-", label=conj)
    axes[0].set_xlabel("Flávio→Lula imposta (%)"); axes[0].set_ylabel("Lula→abstenção ajustada (%)")
    axes[1].set_xlabel("Flávio→Lula imposta (%)"); axes[1].set_ylabel("aumento de deviance / φ")
    axes[0].legend(fontsize=7)
    fig.suptitle("Amapá, todas as seções: o que o modelo troca por migração — estimativa", fontsize=10)
    fig.tight_layout(); fig.savefig(FIG / "aud_amapa_perfil_troca.png"); plt.close(fig)


def parte_todo():
    try:
        t = pd.read_csv(TAB / "06_parte_todo.csv")
    except FileNotFoundError:
        return
    g = t[(t.medida == "corr_dV_dL_taxa") & t.nula.notna()]
    fig, ax = plt.subplots(figsize=(6, 3.2))
    x = np.arange(len(g))
    ax.bar(x, g.media_nula, color="0.6", label="nula aritmética (repartição independente de Δválidos)")
    ax.errorbar(x, g.media_nula, yerr=[g.media_nula - g.q025_nula, g.q975_nula - g.media_nula], fmt="none", color="k")
    ax.axhline(g.observado.iloc[0], color="C3", label=f"observada: {g.observado.iloc[0]:.2f}")
    ax.set_xticks(x); ax.set_xticklabels(g.nula)
    ax.set_ylabel("correlação Δválidos × ΔLula (municípios)")
    ax.set_title("Correlação parte-todo — dado oficial × distribuição nula", fontsize=9)
    ax.legend(fontsize=7)
    fig.tight_layout(); fig.savefig(FIG / "aud_parte_todo.png"); plt.close(fig)


def main():
    for f in (fronteira, sintetico, intervalos, limites, amapa, parte_todo):
        try:
            f()
        except Exception as e:  # uma figura que falhe não impede as outras
            print("aviso:", f.__name__, repr(e)[:200])
    print("figuras em", FIG)


if __name__ == "__main__":
    main()
