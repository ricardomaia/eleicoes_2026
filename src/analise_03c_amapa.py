"""Etapa 3c — Amapá com todas as seções (teste da seção 7 sem amostragem).

Com a amostra de 400 seções, o Amapá foi a única UF em que o teto 0% para
a taxa Flávio(1T)→Lula(2T) foi rejeitado com correção de Bonferroni. Aqui o
mesmo modelo é ajustado com as 1.914 seções do estado, e também separando
capital (Macapá e Santana) e interior. Intervalos: bootstrap por município
(16 municípios; por isso também se reporta o bootstrap por seção).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from comum import INTERIM, SEMENTE, TABELAS
from ei import ajustar, deviance, preparar, sobredispersao, teste_restricao

O = ["a_1", "b_1", "o_1", "bn_1", "abst_1"]
D = ["a_2", "b_2", "bn_2", "abst_2"]


def main():
    bu = pd.read_parquet(INTERIM / "bu_t2_completo_AP.parquet").rename(columns={"mun": "cd_mun"})
    bu = bu[bu.erro == ""]
    sec = pd.read_parquet(INTERIM / "secoes_2026.parquet")
    s = sec[sec.uf == "AP"].drop(columns=["a_2", "b_2"]).merge(
        bu[["uf", "cd_mun", "zona", "secao", "v13", "v22", "comparecimento", "aptos"]],
        on=["uf", "cd_mun", "zona", "secao"])
    s["a_2"], s["b_2"] = s.v13.fillna(0), s.v22.fillna(0)
    confere = int(((s.a_2 + s.b_2) != s.validos_2).sum() + (s.comparecimento != s.comp_2).sum())
    s["grupo"] = np.where(s.nm_municipio.isin(["MACAPÁ", "SANTANA"]), "Macapá e Santana", "interior")
    rng = np.random.default_rng(SEMENTE)
    linhas = []
    for nome, g in [("Amapá (todas as seções)", s)] + list(s.groupby("grupo")):
        R, C, N, ok = preparar(g, O, D)
        X = R / N[:, None]
        B, _, _ = ajustar(X, C)
        d0 = deviance(B, X, C)
        phi, gl = sobredispersao(B, X, C)
        boot = []
        for _ in range(200):
            i = rng.integers(0, len(X), len(X))
            Bb, _, _ = ajustar(X[i], C[i], B0=B)
            boot.append(Bb[1, 0])
        for teto in (0.0, 0.01, 0.02, 0.05):
            Bc, _, _ = ajustar(X, C, B0=B, limites_celula={(1, 0): (0, teto)}) if B[1, 0] > teto else (B, 0, 0)
            F, p = teste_restricao(d0, deviance(Bc, X, C), phi, 1, gl)
            linhas.append({"conjunto": nome, "secoes": len(g), "teto": teto, "taxa_FL_livre": B[1, 0],
                           "taxa_FL_ic95_inf_boot_secao": np.percentile(boot, 2.5),
                           "taxa_FL_ic95_sup_boot_secao": np.percentile(boot, 97.5),
                           "taxa_L_abst": B[0, 3], "taxa_F_abst": B[1, 3], "taxa_A_L": B[4, 0],
                           "phi": phi, "F": F, "p": p, "divergencias_bu_detalhe": confere})
    t = pd.DataFrame(linhas)
    t.to_csv(TABELAS / "03c_amapa_todas_secoes.csv", index=False)
    with pd.option_context("display.width", 250, "display.float_format", "{:,.4f}".format):
        print(t.to_string())


if __name__ == "__main__":
    main()
