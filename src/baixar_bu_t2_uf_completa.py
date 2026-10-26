"""Baixa os BUs do 2º turno de TODAS as seções de uma UF (complemento da amostra).

Usado para o Amapá, única UF em que o teste "taxa Flávio→Lula = 0" foi
rejeitado com correção de Bonferroni na amostra de seções. Uso:
    python baixar_bu_t2_uf_completa.py AP
Saída: interim/bu_t2_completo_<UF>.parquet
"""
from __future__ import annotations

import concurrent.futures as cf
import sys

import pandas as pd

from baixar_bu_t2_amostra import baixar_secao, universo
from comum import INTERIM


def main(uf: str, paralelo: int = 8) -> None:
    u = universo()
    u = u[u.uf == uf]
    linhas = list(u[["uf", "mun", "zona", "secao"]].itertuples(index=False, name=None))
    with cf.ThreadPoolExecutor(paralelo) as ex:
        regs = list(ex.map(baixar_secao, linhas))
    df = pd.DataFrame(regs)
    df.to_parquet(INTERIM / f"bu_t2_completo_{uf}.parquet", index=False)
    print(uf, len(df), "seções; erros:", (df.erro != "").sum())


if __name__ == "__main__":
    main(sys.argv[1])
