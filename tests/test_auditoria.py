"""Testes dos módulos da auditoria metodológica (auditoria_*.py, ei_cov.py).

Todos rodam sem os dados do TSE (só método). Execução: pytest -q tests/
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from auditoria_01_identificacao import CONJUNTOS, _fronteira_uf, _limites_unidade  # noqa: E402
from auditoria_02_sintetico import B_A, cenarios, compensacao_constante, gerar  # noqa: E402
from auditoria_comum import variancia_transicao  # noqa: E402
from ei import ajustar  # noqa: E402
from ei_cov import B_M1, _nll_M1, ajustar_M1, ajustar_M2, B_M2  # noqa: E402
from fluxos import limites_frechet  # noqa: E402


def test_gerador_contabilidade():
    d = gerar(cenarios()["A"], 300, 1)
    # cada eleitor aparece uma vez em cada turno; os fluxos verdadeiros somam as margens
    assert np.allclose(d["M"].sum(2), d["R"]) and np.allclose(d["M"].sum(1), d["Y"])
    assert np.allclose(d["R"].sum(1), d["N"]) and np.allclose(d["Y"].sum(1), d["N"])
    assert np.allclose(d["verdade"].sum(1), 1)


def test_compensacao_constante_preserva_totais():
    comp = np.array([.339, .353, .059, .038, .211])
    B = compensacao_constante(B_A, 0.10, comp)
    assert np.allclose(B.sum(1), 1) and (B >= 0).all()
    assert np.allclose(comp @ B, comp @ B_A)          # mesmos totais nacionais
    assert abs(B[1, 0] - B_A[1, 0] - 0.10) < 1e-12


def test_B2_equivalente_a_A_por_secao():
    cz = cenarios()
    dA = gerar(cz["A"], 500, 3)
    dB = gerar(cz["B2_10"], 500, 3)
    X = dA["R"] / dA["N"][:, None]
    assert np.allclose(X, dB["R"] / dB["N"][:, None])   # mesma composição (mesma semente)
    pA = (X[:, :, None] * dA["Bi"]).sum(1)
    pB = (X[:, :, None] * dB["Bi"]).sum(1)
    assert np.abs(pA - pB).max() < 1e-10               # esperanças idênticas
    assert dB["esperada"][1, 0] - dA["esperada"][1, 0] > 0.08   # migração verdadeira ≈ 10 p.p. maior


def test_modelo_A_nao_distingue_B2_de_A():
    cz = cenarios()
    dB = gerar(cz["B2_10"], 3000, 11)
    X = dB["R"] / dB["N"][:, None]
    B, _, _ = ajustar(X, dB["Y"])
    assert dB["verdade"][1, 0] > 0.08
    assert B[1, 0] < 0.02   # estimativa fica perto da matriz "A", não da verdadeira


def test_limites_lp_S0_igual_frechet():
    rng = np.random.default_rng(0)
    R = rng.integers(10, 100, 5).astype(float)
    # coluna compatível: sorteia uma matriz e soma
    M = np.array([rng.multinomial(int(r), rng.dirichlet(np.ones(4))) for r in R], float)
    C = M.sum(0)
    res = _limites_unidade((R, C, [(1, 0), (0, 1)], {"S0_sem_hipoteses": {}}))
    lo, hi = limites_frechet(R[None], C[None])
    assert abs(res[("S0_sem_hipoteses", 1, 0)][0] - lo[1, 0]) < 1e-6
    assert abs(res[("S0_sem_hipoteses", 1, 0)][1] - hi[1, 0]) < 1e-6
    # com hipótese: os limites só podem apertar
    res2 = _limites_unidade((R, C, [(1, 0)], CONJUNTOS))
    for nome in CONJUNTOS:
        a, b, viavel = res2[(nome, 1, 0)]
        if viavel:
            assert a >= lo[1, 0] - 1e-6 and b <= hi[1, 0] + 1e-6


def test_fronteira_zero_quando_matriz_constante_exata():
    rng = np.random.default_rng(2)
    B = B_A
    n = 40
    R = rng.integers(20, 60, (n, 5)).astype(float)
    M = R[:, :, None] * B[None]           # fluxos exatos (não inteiros): nenhuma heterogeneidade
    C = M.sum(1)
    res = _fronteira_uf(("t", R, C, None))
    assert res["status"] == 0 and res["fracao_minima_desviante"] < 1e-6
    assert abs(res["B_b_1_a_2"] - B[1, 0]) < 1e-4
    # impondo outra taxa, a fração desviante passa a ser positiva (a matriz comum B̄ é livre nas
    # demais células, por isso só a variação ENTRE seções das compensações conta como desvio)
    res2 = _fronteira_uf(("t", R, C, 0.10))
    assert res2["status"] == 0 and res2["fracao_minima_desviante"] > 1e-4


def test_gradiente_M1():
    rng = np.random.default_rng(4)
    n = 50
    X = rng.dirichlet([8, 8, 1.5, 0.6, 3], size=n)
    z = rng.normal(size=n)
    N = rng.integers(100, 300, n)
    Y = np.array([rng.multinomial(N[i], X[i] @ B_A) for i in range(n)], float)
    p = rng.normal(size=30) * 0.5
    f, g = _nll_M1(p, X, Y, z)
    for k in rng.choice(30, 6, replace=False):
        e = np.zeros(30); e[k] = 1e-6
        num = (_nll_M1(p + e, X, Y, z)[0] - _nll_M1(p - e, X, Y, z)[0]) / 2e-6
        assert abs(num - g[k]) < 1e-3 * max(1.0, abs(g[k]))


def test_M1_recupera_dependencia_em_z():
    rng = np.random.default_rng(5)
    n = 4000
    X = rng.dirichlet([8, 8, 1.5, 0.6, 3], size=n)
    z = rng.normal(size=n)
    N = rng.integers(150, 400, n)
    alpha = np.clip(np.log(B_A[:, :3] / B_A[:, 3:4]), -12, 12)
    beta = np.zeros((5, 3)); beta[4, 0] = 0.8; beta[3, 0] = 0.6
    Bi = B_M1(alpha, beta, z)
    Y = np.array([rng.multinomial(N[i], X[i] @ Bi[i]) for i in range(n)], float)
    a, b, ll, res = ajustar_M1(X, Y, z)
    # a linha da abstenção (≈ 15% do eleitorado) é bem identificada; a de brancos/nulos (≈ 3%) muito menos
    assert abs(b[4, 0] - 0.8) < 0.25 and abs(b[3, 0] - 0.6) < 0.7
    assert ll > -1e12


def test_M2_probabilidades_validas():
    rng = np.random.default_rng(6)
    pi = rng.uniform(0, 1, 100)
    B = B_M2(rng.normal(size=15), pi)
    assert (B >= -1e-12).all() and np.allclose(B.sum(2), 1)


def test_variancia_transicao_menor_que_multinomial():
    rng = np.random.default_rng(7)
    X = rng.dirichlet([8, 8, 1.5, 0.6, 3], size=20)
    N = np.full(20, 300.0)
    P = X @ B_A
    assert (variancia_transicao(X, B_A, N) <= P * (1 - P) / N[:, None] + 1e-12).all()
