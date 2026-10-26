"""Etapa 9 — Comparação histórica normalizada (2018, 2022, 2026).

Todas as grandezas em votos por 100 aptos (ou p.p.), para neutralizar o
tamanho do eleitorado. "a" = finalista do PT; "b" = finalista de direita.
Inclui a heterogeneidade territorial das variações (desvio-padrão entre
municípios, ponderado pelos aptos) e reúne, de outras etapas, as taxas de
transição estimadas e a distribuição dos resíduos.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from comum import INTERIM, TABELAS

NOMES = {2026: ("Lula", "Flávio Bolsonaro"), 2022: ("Lula", "Jair Bolsonaro"), 2018: ("Haddad", "Jair Bolsonaro")}


def dp_pond(x, w):
    m = np.average(x, weights=w)
    return float(np.sqrt(np.average((x - m) ** 2, weights=w)))


def main():
    linhas = []
    for ano in (2026, 2022, 2018):
        mun = pd.read_parquet(INTERIM / f"municipios_{ano}.parquet")
        mun = mun[(mun.uf != "ZZ") & (mun.aptos_1 > 0)]
        s = mun.sum(numeric_only=True)
        k = 100 / s.aptos_1
        w = mun.aptos_1
        dA = 100 * (mun.a_2 - mun.a_1) / mun.aptos_1
        dB = 100 * (mun.b_2 - mun.b_1) / mun.aptos_1
        a, b = NOMES[ano]
        linhas.append({
            "ano": ano, "finalista_PT": a, "finalista_direita": b,
            "lider_1T": a if s.a_1 > s.b_1 else b, "vencedor_2T": a if s.a_2 > s.b_2 else b,
            "a_1T_pct_validos": 100 * s.a_1 / s.validos_1, "b_1T_pct_validos": 100 * s.b_1 / s.validos_1,
            "a_2T_pct_validos": 100 * s.a_2 / s.validos_2, "b_2T_pct_validos": 100 * s.b_2 / s.validos_2,
            "crescimento_a_por100aptos": k * (s.a_2 - s.a_1), "crescimento_b_por100aptos": k * (s.b_2 - s.b_1),
            "crescimento_a_pct_proprio": 100 * (s.a_2 / s.a_1 - 1), "crescimento_b_pct_proprio": 100 * (s.b_2 / s.b_1 - 1),
            "eliminados_por100aptos": k * s.o_1, "eliminados_pct_validos": 100 * s.o_1 / s.validos_1,
            "var_validos_por100aptos": k * (s.validos_2 - s.validos_1),
            "var_brancos_nulos_por100aptos": k * (s.bn_2 - s.bn_1),
            "var_comparecimento_pp": 100 * (s.comp_2 / s.aptos_2 - s.comp_1 / s.aptos_1),
            "parcela_crescimento_a_no_crescimento_conjunto": (s.a_2 - s.a_1) / ((s.a_2 - s.a_1) + (s.b_2 - s.b_1)),
            "crescimento_a_menos_eliminados_por100aptos": k * (s.a_2 - s.a_1 - s.o_1),
            "dp_municipal_cresc_a": dp_pond(dA, w), "dp_municipal_cresc_b": dp_pond(dB, w),
            "corr_municipal_eliminados_cresc_a": float(np.corrcoef(mun.o_1 / mun.aptos_1, dA)[0, 1]),
            "corr_municipal_eliminados_cresc_b": float(np.corrcoef(mun.o_1 / mun.aptos_1, dB)[0, 1]),
        })
    t = pd.DataFrame(linhas)
    t.to_csv(TABELAS / "09_comparacao_historica.csv", index=False)
    with pd.option_context("display.width", 200, "display.float_format", "{:,.3f}".format):
        print(t.T)


if __name__ == "__main__":
    main()
