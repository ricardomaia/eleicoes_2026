"""Funções comuns para tabelas de transição entre turnos.

Uma unidade territorial i tem margens do 1º turno (linhas) e do 2º turno
(colunas). Todas as pessoas aptas aparecem uma vez em cada turno, como
votante de alguém, branco/nulo ou abstenção. Quando o número de aptos muda
entre os turnos (transferência temporária, agregação de seções), a diferença
entra como linha "entrada" (aptos que só existem no 2º turno) ou coluna
"saida" (aptos que só existem no 1º turno). Assim as duas margens têm sempre a
mesma soma e as contas são exatas.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

LINHAS_BASE = ["a_1", "b_1", "o_1", "bn_1", "abst_1"]
LINHAS_DETALHADAS = ["a_1", "b_1", "cury_1", "renan_1", "caiado_1", "zema_1", "outros_peq_1", "bn_1", "abst_1"]
COLUNAS = ["a_2", "b_2", "bn_2", "abst_2"]

ROTULO = {
    "a_1": "Lula (1T)", "b_1": "Flávio (1T)", "o_1": "Outros candidatos (1T)",
    "cury_1": "Augusto Cury (1T)", "renan_1": "Renan Santos (1T)", "caiado_1": "Ronaldo Caiado (1T)",
    "zema_1": "Romeu Zema (1T)", "outros_peq_1": "Demais candidatos (1T)",
    "demais_1": "Zema e demais candidatos (1T)",
    "bn_1": "Brancos e nulos (1T)", "abst_1": "Abstenção (1T)", "entrada": "Aptos só no 2T",
    "a_2": "Lula (2T)", "b_2": "Flávio (2T)", "bn_2": "Brancos e nulos (2T)",
    "abst_2": "Abstenção (2T)", "saida": "Aptos só no 1T",
}


def margens(df: pd.DataFrame, linhas=LINHAS_BASE, colunas=COLUNAS) -> tuple[np.ndarray, np.ndarray, list, list]:
    """Retorna (R, C, nomes_linhas, nomes_colunas) com o ajuste de cadastro."""
    R = df[linhas].to_numpy(dtype=float)
    C = df[colunas].to_numpy(dtype=float)
    d = C.sum(1) - R.sum(1)
    R = np.column_stack([R, np.clip(d, 0, None)])
    C = np.column_stack([C, np.clip(-d, 0, None)])
    return R, C, list(linhas) + ["entrada"], list(colunas) + ["saida"]


def limites_frechet(R: np.ndarray, C: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Limites de Fréchet (Duncan e Davis) de cada célula, somados nas unidades.

    Para uma unidade com total N, a célula (r, c) satisfaz
        max(0, R_r + C_c − N) ≤ x_rc ≤ min(R_r, C_c).
    A soma dos limites das unidades é limite válido para o total agregado e
    é atingível célula a célula (não necessariamente todas ao mesmo tempo).
    """
    N = R.sum(1)
    lo = np.clip(R[:, :, None] + C[:, None, :] - N[:, None, None], 0, None)
    hi = np.minimum(R[:, :, None], C[:, None, :])
    return lo.sum(0), hi.sum(0)


def tabela_limites(R, C, nl, nc, nivel: str) -> pd.DataFrame:
    lo, hi = limites_frechet(R, C)
    tot_r = R.sum(0)
    linhas = []
    for i, r in enumerate(nl):
        for j, c in enumerate(nc):
            if tot_r[i] == 0:
                continue
            linhas.append({"nivel": nivel, "origem": r, "destino": c,
                           "min_votos": lo[i, j], "max_votos": hi[i, j],
                           "min_taxa": lo[i, j] / tot_r[i], "max_taxa": hi[i, j] / tot_r[i],
                           "total_origem": tot_r[i]})
    return pd.DataFrame(linhas)
