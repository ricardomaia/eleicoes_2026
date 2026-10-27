"""Auditoria 6 — Correlação parte-todo entre variação de válidos e crescimento de cada finalista.

Identidade por município: ΔLula + ΔFlávio = Outros(1T) + Δválidos. Logo
ΔLula é, por construção, uma parte de (Outros + Δválidos). A correlação
municipal publicada entre Δválidos e ΔLula (0,78) e o coeficiente 0,67 (voto
de Lula por voto válido adicional) contêm uma componente puramente aritmética.

Teste: distribuição nula em que o ganho conjunto G_i = Outros_i + Δválidos_i
é repartido entre Lula e Flávio SEM nenhuma relação com Δválidos — cada
município recebe uma fração s_i sorteada (a) constante = fração nacional
(0,736); (b) binomial com essa fração; (c) Beta com a média nacional e a
dispersão observada das frações municipais (preserva a heterogeneidade real
da repartição, mas a torna independente de Δválidos). Comparam-se correlação
e coeficiente observados com os da nula. Medidas que não contêm a identidade:
correlação entre Δválidos e a fração do ganho que foi para Lula
(ΔLula / G), e entre Δválidos e a variação do log-razão Lula/Flávio.
Tudo em taxas por apto do 1T e também em valores absolutos.

Saídas: resultados/auditoria/tabelas/06_parte_todo.csv
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from auditoria_comum import TAB, municipios_2026, salvar_json
from comum import SEMENTE


def corr_w(x, y, w):
    mx, my = np.average(x, weights=w), np.average(y, weights=w)
    return float(np.average((x - mx) * (y - my), weights=w) /
                 np.sqrt(np.average((x - mx) ** 2, weights=w) * np.average((y - my) ** 2, weights=w)))


def coef_w(y, x, w):
    mx, my = np.average(x, weights=w), np.average(y, weights=w)
    return float(np.average((x - mx) * (y - my), weights=w) / np.average((x - mx) ** 2, weights=w))


def main(n_sim=2000):
    m = municipios_2026()
    m = m[(m.uf != "ZZ") & (m.aptos_1 > 0) & (m.validos_1 > 0)].copy()
    w = m.aptos_1.to_numpy(float)
    dV = (m.validos_2 - m.validos_1).to_numpy(float)
    dL = (m.a_2 - m.a_1).to_numpy(float)
    dF = (m.b_2 - m.b_1).to_numpy(float)
    O = m.o_1.to_numpy(float)
    G = O + dV
    assert np.allclose(dL + dF, G)
    s_nac = dL.sum() / G.sum()
    pos = G > 0
    frac = np.where(pos, dL / np.where(pos, G, 1), np.nan)
    # Beta com média s_nac e a dispersão real das frações municipais, descontada a parte binomial;
    # só municípios com ganho conjunto ≥ 200 votos, onde a fração é bem medida
    grande = pos & (G >= 200)
    fr, ww = frac[grande], w[grande]
    var_obs = np.average((fr - np.average(fr, weights=ww)) ** 2, weights=ww)
    var_bin = np.average(s_nac * (1 - s_nac) / G[grande], weights=ww)
    var_het = max(var_obs - var_bin, 1e-6)
    kappa = max(s_nac * (1 - s_nac) / var_het - 1, 1.0)
    rng = np.random.default_rng(SEMENTE)
    obs = {"corr_dV_dL_taxa": corr_w(dV / w, dL / w, w), "corr_dV_dF_taxa": corr_w(dV / w, dF / w, w),
           "coef_dL_sobre_dV_taxa": coef_w(dL / w, dV / w, w), "coef_dF_sobre_dV_taxa": coef_w(dF / w, dV / w, w),
           "corr_dV_dL_abs": corr_w(dV, dL, w), "corr_dV_fracao_ganho_lula": corr_w((dV / w)[pos], frac[pos], w[pos]),
           "corr_dV_dlograzao": corr_w(dV / w, np.log((m.a_2 + 1) / (m.b_2 + 1)) - np.log((m.a_1 + 1) / (m.b_1 + 1)), w),
           "fracao_nacional_ganho_lula": s_nac, "kappa_beta": kappa}
    nulos = {"constante": [], "binomial": [], "beta": []}
    for _ in range(n_sim):
        for nome in nulos:
            if nome == "constante":
                s = np.full(len(G), s_nac)
            elif nome == "binomial":
                s = np.where(pos, rng.binomial(np.clip(G, 0, None).astype(int), s_nac) / np.where(pos, G, 1), s_nac)
            else:
                s = rng.beta(s_nac * kappa, (1 - s_nac) * kappa, len(G))
            dLs = s * G
            nulos[nome].append((corr_w(dV / w, dLs / w, w), coef_w(dLs / w, dV / w, w), corr_w(dV, dLs, w)))
    linhas = [{"medida": k, "observado": v} for k, v in obs.items()]
    for nome, vals in nulos.items():
        a = np.array(vals)
        for j, med in enumerate(("corr_dV_dL_taxa", "coef_dL_sobre_dV_taxa", "corr_dV_dL_abs")):
            linhas.append({"medida": med, "nula": nome, "media_nula": a[:, j].mean(), "q025_nula": np.percentile(a[:, j], 2.5),
                           "q975_nula": np.percentile(a[:, j], 97.5), "observado": obs[med],
                           "observado_menos_media_nula": obs[med] - a[:, j].mean()})
    t = pd.DataFrame(linhas)
    t.to_csv(TAB / "06_parte_todo.csv", index=False)
    salvar_json(obs, TAB / "06_resumo.json")
    with pd.option_context("display.width", 200, "display.float_format", "{:,.4f}".format):
        print(t.to_string())


if __name__ == "__main__":
    main()
