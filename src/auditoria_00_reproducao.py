"""Auditoria 0 — Reprodução do Modelo A (2026, seção, origens base) sem o cache.

analise_03_inferencia_ecologica.py reaproveita blocos gravados em
interim/ei_bloco_*.pkl. Aqui o bloco principal (2026, seção, origens base) é
recalculado do zero, com a mesma semente, e comparado célula a célula com a
tabela publicada (resultados/tabelas/03_matriz_transicao_nacional_2026.csv).
Saída: resultados/auditoria/tabelas/00_reproducao_modeloA.csv
"""
from __future__ import annotations

import time

import numpy as np
import pandas as pd

from analise_03_inferencia_ecologica import N_BOOT, ORIG_BASE, estimar, unidades
from auditoria_comum import TAB, salvar_json
from comum import SEMENTE, TABELAS


def main():
    t0 = time.time()
    niveis, totais_uf = unidades(2026)
    rng = np.random.default_rng([SEMENTE, 2026, len("secao"), len("base")])
    nac, uf, tst = estimar(niveis["secao"], ORIG_BASE, totais_uf, rng, n_boot=N_BOOT, tetos=True, ano=2026)
    pub = pd.read_csv(TABELAS / "03_matriz_transicao_nacional_2026.csv")
    pub = pub[(pub.nivel == "secao") & (pub.origens == "base")]
    cmp = nac.merge(pub, on=["origem", "destino"], suffixes=("_repro", "_pub"))
    cmp["dif_taxa"] = cmp.taxa_repro - cmp.taxa_pub
    cmp["dif_ic_inf"] = cmp.taxa_ic95_inf_repro - cmp.taxa_ic95_inf_pub
    cmp["dif_ic_sup"] = cmp.taxa_ic95_sup_repro - cmp.taxa_ic95_sup_pub
    cmp[["origem", "destino", "taxa_pub", "taxa_repro", "dif_taxa", "taxa_ic95_inf_pub", "taxa_ic95_inf_repro",
         "dif_ic_inf", "taxa_ic95_sup_pub", "taxa_ic95_sup_repro", "dif_ic_sup"]].to_csv(
        TAB / "00_reproducao_modeloA.csv", index=False)
    pub_t = pd.read_csv(TABELAS / "03_teste_migracao_2026_secao.csv")
    from analise_03_inferencia_ecologica import resumir_testes
    rt = resumir_testes(tst, ORIG_BASE)
    ct = rt.merge(pub_t, on=["hipotese", "teto"], suffixes=("_repro", "_pub"))
    ct[["hipotese", "teto", "chi2_total_pub", "chi2_total_repro", "p_conjunto_pub", "p_conjunto_repro"]].to_csv(
        TAB / "00_reproducao_teste_migracao.csv", index=False)
    resumo = {"tempo_s": time.time() - t0, "max_abs_dif_taxa": float(cmp.dif_taxa.abs().max()),
              "max_abs_dif_ic": float(max(cmp.dif_ic_inf.abs().max(), cmp.dif_ic_sup.abs().max())),
              "max_abs_dif_chi2": float((ct.chi2_total_pub - ct.chi2_total_repro).abs().max())}
    salvar_json(resumo, TAB / "00_reproducao_resumo.json")
    with pd.option_context("display.width", 250, "display.float_format", "{:,.6f}".format):
        print(cmp[["origem", "destino", "taxa_pub", "taxa_repro", "dif_taxa", "dif_ic_inf", "dif_ic_sup"]].to_string())
        print(ct.to_string())
    print(resumo)


if __name__ == "__main__":
    main()
