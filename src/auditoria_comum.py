"""Funções e caminhos comuns aos scripts da auditoria metodológica (auditoria_*.py).

Todos os resultados da auditoria ficam em resultados/auditoria/ para não
substituir as tabelas originais (resultados/tabelas/), que são preservadas
para comparação.
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd

from comum import INTERIM, PROJETO, REGIAO, SEMENTE, salvar_json  # noqa: F401

# No Windows o console usa cp1252 e não imprime "→"; as tabelas em disco são sempre UTF-8.
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

AUD = PROJETO / "resultados" / "auditoria"
TAB = AUD / "tabelas"
FIG = AUD / "figuras"
for _p in (TAB, FIG):
    _p.mkdir(parents=True, exist_ok=True)

ORIG = ["a_1", "b_1", "o_1", "bn_1", "abst_1"]
DEST = ["a_2", "b_2", "bn_2", "abst_2"]
ROT_O = {"a_1": "Lula", "b_1": "Flávio", "o_1": "Outros", "bn_1": "Brancos/nulos", "abst_1": "Abstenção"}
ROT_D = {"a_2": "Lula", "b_2": "Flávio", "bn_2": "Brancos/nulos", "abst_2": "Abstenção"}
iL, iF, iO, iBN, iA = range(5)
jL, jF, jBN, jA = range(4)


import os

# Com AUDITORIA_TODAS_SECOES=1, as análises por seção usam todas as seções instaladas com votação do
# 2º turno (arquivo votacao_secao completo, publicado pelo TSE em 26/10/2026 às 17h42 UTC) em vez da
# amostra de 50.821 BUs; as saídas recebem o sufixo "_todas" para não substituir as da amostra.
TODAS_SECOES = os.environ.get("AUDITORIA_TODAS_SECOES", "") == "1"
SUFIXO = "_todas" if TODAS_SECOES else ""


def amostra_2026() -> pd.DataFrame:
    """Seções usadas nas análises por seção: a amostra de BUs do 2º turno (50.821) ou, com
    AUDITORIA_TODAS_SECOES=1, todas as seções com votação por candidato no 2º turno."""
    sec = pd.read_parquet(INTERIM / "secoes_2026.parquet")
    if TODAS_SECOES:
        return sec[sec.a_2.notna() & (sec.aptos_1 > 0) & (sec.instalada_2 != "Não")].copy()
    return sec[sec.na_amostra_bu.fillna(False).astype(bool)].copy()


def todas_secoes_2026() -> pd.DataFrame:
    return pd.read_parquet(INTERIM / "secoes_2026.parquet")


def municipios_2026() -> pd.DataFrame:
    return pd.read_parquet(INTERIM / "municipios_2026.parquet")


def totais_por_uf(sec: pd.DataFrame, origens=ORIG) -> pd.DataFrame:
    """Totais de cada origem por UF (todas as seções), com o ajuste de cadastro
    usado em ei.preparar (aptos que só existem no 2T entram como abstenção 1T)."""
    t = sec.groupby("uf")[origens].sum()
    d = sec.groupby("uf").apply(lambda g: (g.aptos_2 - g.aptos_1).clip(lower=0).sum(), include_groups=False)
    t["abst_1"] = t["abst_1"] + d
    return t


def matrizes_RC(df: pd.DataFrame, origens=ORIG, destinos=DEST):
    """R (n×5), C (n×4), N (n) com ajuste de cadastro; remove unidades com N = 0."""
    R = df[origens].to_numpy(float, copy=True)
    C = df[destinos].to_numpy(float, copy=True)
    d = C.sum(1) - R.sum(1)
    R[:, -1] += np.clip(d, 0, None)
    C[:, -1] += np.clip(-d, 0, None)
    N = R.sum(1)
    ok = N > 0
    return R[ok], C[ok], N[ok], ok


def variancia_transicao(X: np.ndarray, B: np.ndarray, N: np.ndarray) -> np.ndarray:
    """Variância da proporção de cada destino quando cada eleitor de origem r
    transita de forma independente com probabilidades B[r, :]:
        Var(y_c / N) = Σ_r x_r B_rc (1 − B_rc) / N.
    É menor que a variância multinomial p_c(1 − p_c)/N (p = xB) porque esta
    última inclui a variação entre as linhas de B como se fosse aleatória."""
    v = (X[:, :, None] * (B * (1 - B))[None]).sum(1)
    return v / N[:, None]


def fluxo_nacional(Bs: dict, totais: pd.DataFrame, origens=ORIG) -> np.ndarray:
    fl = np.zeros((len(origens), 4))
    for uf, B in Bs.items():
        fl += totais.loc[uf, origens].to_numpy(float)[:, None] * B
    return fl


def taxa_nacional(Bs: dict, totais: pd.DataFrame, origens=ORIG) -> np.ndarray:
    fl = fluxo_nacional(Bs, totais, origens)
    return fl / fl.sum(1, keepdims=True)


def matriz_para_linhas(B, **tags):
    return [{"origem": o, "destino": d, "taxa": float(B[i, j]), **tags}
            for i, o in enumerate(ORIG) for j, d in enumerate(DEST)]
