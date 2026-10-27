"""Auditoria 9 — O que os dados permitem dizer sobre o voto cruzado (legislativo × presidente).

A seção V do relatório estima por inferência ecológica que 5,4% dos
eleitores do PL para deputado federal votaram em Lula no 1º turno. Aqui se
calcula o que a aritmética sozinha permite: limites de Fréchet por seção
(todas as 499 mil) para os fluxos entre blocos partidários (voto para
deputado federal) e candidatos a presidente, no 1º turno, somados
nacionalmente. Mesma população nas duas pontas: quem compareceu. A
classificação em blocos é a de analise_06_legislativo.py; o mesmo cálculo é
feito com "direita estrita" (PL+PP+União+Republicanos+Novo) como bloco.

Saída: resultados/auditoria/tabelas/09_limites_voto_cruzado.csv
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from auditoria_comum import TAB
from comum import INTERIM
from fluxos import limites_frechet


def main():
    leg = pd.read_parquet(INTERIM / "legislativo_secao_2026.parquet")
    sec = pd.read_parquet(INTERIM / "secoes_2026.parquet",
                          columns=["uf", "cd_mun", "zona", "secao", "comp_1", "a_1", "b_1", "o_1", "validos_1", "na_amostra_bu",
                                   "a_2", "b_2", "bn_2", "abst_2", "aptos_1"])
    d = sec.merge(leg, on=["uf", "cd_mun", "zona", "secao"], how="inner")
    d = d[d.comp_1 > 0].copy()
    origens = ["dep_pl", "dep_dir_outros", "dep_centro", "dep_fe_brasil", "dep_esq_outros"]
    if "dep_outros" in d:
        d["dep_bn"] = d.dep_bn + d.dep_outros
    d["dep_resto"] = d.comp_1 - d[origens].sum(1)   # brancos, nulos e votos não computados para deputado
    d["bn_1x"] = d.comp_1 - d.a_1 - d.b_1 - d.o_1
    R = d[origens + ["dep_resto"]].to_numpy(float)
    C = d[["a_1", "b_1", "o_1", "bn_1x"]].to_numpy(float)
    assert np.allclose(R.sum(1), C.sum(1))
    lo, hi = limites_frechet(R, C)
    tot = R.sum(0)
    nomes_o = ["PL", "outros de direita", "centro", "federação PT", "outros de esquerda", "branco/nulo/sem voto p/ deputado"]
    nomes_d = ["Lula", "Flávio", "outros", "branco/nulo"]
    linhas = []
    for i, o in enumerate(nomes_o):
        for j, c in enumerate(nomes_d):
            linhas.append({"turno": "1T (todas as seções)", "origem_deputado": o, "destino_presidente": c, "eleitores_origem": tot[i],
                           "min_votos": lo[i, j], "max_votos": hi[i, j], "min_taxa": lo[i, j] / tot[i], "max_taxa": hi[i, j] / tot[i]})
    # 2T na amostra: quem votou para deputado (comparecimento 1T) + abstenção 1T → destinos do 2T
    am = d[d.na_amostra_bu.fillna(False).astype(bool) & d.a_2.notna()].copy()
    am["abst_1x"] = am.aptos_1 - am.comp_1
    R2 = am[origens + ["dep_resto", "abst_1x"]].to_numpy(float, copy=True)
    C2 = am[["a_2", "b_2", "bn_2", "abst_2"]].to_numpy(float, copy=True)
    dd = C2.sum(1) - R2.sum(1)
    R2[:, -1] += np.clip(dd, 0, None)
    C2[:, -1] += np.clip(-dd, 0, None)
    lo2, hi2 = limites_frechet(R2, C2)
    tot2 = R2.sum(0)
    for i, o in enumerate(nomes_o + ["abstenção 1T"]):
        for j, c in enumerate(["Lula", "Flávio", "branco/nulo", "abstenção"]):
            linhas.append({"turno": "2T (amostra de 50.821 seções)", "origem_deputado": o, "destino_presidente": c,
                           "eleitores_origem": tot2[i], "min_votos": lo2[i, j], "max_votos": hi2[i, j],
                           "min_taxa": lo2[i, j] / tot2[i], "max_taxa": hi2[i, j] / tot2[i]})
    t = pd.DataFrame(linhas)
    t.to_csv(TAB / "09_limites_voto_cruzado.csv", index=False)
    with pd.option_context("display.width", 200, "display.float_format", "{:,.4f}".format):
        print(t.to_string())


if __name__ == "__main__":
    main()
