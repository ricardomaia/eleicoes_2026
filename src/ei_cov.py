"""Inferência ecológica com taxas que variam entre unidades (extensões do Modelo A).

Dois modelos alternativos ao de constância (ei.py), ajustados por máxima
quase-verossimilhança multinomial:

M1 — covariável de contexto. Para a unidade i, cada linha r da matriz é
     B_i[r, ·] = softmax(α_r + β_r · z_i), com z_i uma covariável padronizada
     (ex.: margem Lula − Flávio no município no 1º turno). O destino
     "abstenção 2T" é a referência (logito 0). Com β = 0 o modelo é o de
     constância. É a extensão de King com covariável; permite que todas as
     taxas (inclusive a conversão de brancos/nulos e de abstencionistas)
     dependam do contexto político local. Gradiente analítico.

M2 — preferência latente. Quem votou em branco/nulo ou se absteve no 1º turno
     tem uma preferência latente que acompanha a da sua seção:
     π_i = Lula1 / (Lula1 + Flávio1). Para essas duas linhas,
       P(→Lula) = π_i · τ_L,   P(→Flávio) = (1 − π_i) · τ_F,
       P(→branco/nulo) = ν,     P(→abstenção) = o resto,
     onde τ_L, τ_F são taxas de comparecimento/conversão dos simpatizantes de
     cada lado e ν é constante. As linhas Lula, Flávio e outros são constantes.
     A participação eleitoral depende, assim, da preferência latente, e a
     conversão de brancos/nulos/abstencionistas para Lula varia com a seção
     sem nenhum parâmetro extra por seção. Parametrização por sigmoides garante
     probabilidades em [0, 1].

As duas extensões são identificadas só porque restringem a FORMA da
dependência entre as taxas e a composição; são hipóteses alternativas à
constância, não hipóteses mais fracas.
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import minimize
from scipy.special import expit

from ei import ajustar

EPS = 1e-12


def _softmax_ref(eta):
    """eta: n×5×3 (logitos em relação ao destino de referência) → B: n×5×4."""
    full = np.concatenate([eta, np.zeros(eta.shape[:-1] + (1,))], axis=-1)
    full = full - full.max(-1, keepdims=True)
    e = np.exp(full)
    return e / e.sum(-1, keepdims=True)


# --------------------------------------------------------------------------- M1
def B_M1(alpha, beta, z):
    eta = alpha[None] + beta[None] * z[:, None, None]
    return _softmax_ref(eta)


def _nll_M1(params, X, Y, z):
    alpha = params[:15].reshape(5, 3)
    beta = params[15:].reshape(5, 3)
    B = B_M1(alpha, beta, z)                           # n×5×4
    P = np.clip(np.einsum("ir,irc->ic", X, B), EPS, None)
    ll = (Y * np.log(P)).sum()
    W = Y / P                                          # n×4
    # g_irc = x_ir B_irc [W_ic − Σ_c' W_ic' B_irc']
    S = np.einsum("ic,irc->ir", W, B)                  # n×5
    G = X[:, :, None] * B * (W[:, None, :] - S[:, :, None])   # n×5×4
    G = G[:, :, :3]                                    # referência não tem parâmetro
    d_alpha = G.sum(0)
    d_beta = (G * z[:, None, None]).sum(0)
    return -ll, -np.concatenate([d_alpha.ravel(), d_beta.ravel()])


def ajustar_M1(X, Y, z, B0=None, beta0=None, max_iter=500):
    if B0 is None:
        B0, _, _ = ajustar(X, Y)
    Bc = np.clip(B0, 1e-6, None)
    alpha0 = np.log(Bc[:, :3] / Bc[:, 3:4])
    alpha0 = np.clip(alpha0, -12, 12)
    beta0 = np.zeros((5, 3)) if beta0 is None else beta0
    x0 = np.concatenate([alpha0.ravel(), beta0.ravel()])
    res = minimize(_nll_M1, x0, args=(X, Y, z), jac=True, method="L-BFGS-B",
                   options={"maxiter": max_iter, "ftol": 1e-12, "gtol": 1e-7})
    alpha = res.x[:15].reshape(5, 3)
    beta = res.x[15:].reshape(5, 3)
    return alpha, beta, -res.fun, res


# --------------------------------------------------------------------------- M2
def B_M2(params, pi):
    """params: 9 logitos (linhas Lula, Flávio, outros; 3 por linha) + 6 (linhas BN e abst: a, b, c)."""
    n = len(pi)
    B = np.empty((n, 5, 4))
    eta = params[:9].reshape(3, 3)
    B[:, :3, :] = _softmax_ref(np.broadcast_to(eta[None], (n, 3, 3)))
    for k, r in enumerate((3, 4)):
        a, b, c = params[9 + 3 * k: 12 + 3 * k]
        tL, tF = expit(a), expit(b)
        nu = expit(c) * (1 - max(tL, tF))
        pL = pi * tL
        pF = (1 - pi) * tF
        B[:, r, 0] = pL
        B[:, r, 1] = pF
        B[:, r, 2] = nu
        B[:, r, 3] = 1 - pL - pF - nu
    return B


def _nll_M2(params, X, Y, pi):
    B = B_M2(params, pi)
    P = np.clip(np.einsum("ir,irc->ic", X, B), EPS, None)
    return -(Y * np.log(P)).sum()


def ajustar_M2(X, Y, pi, B0=None, max_iter=2000):
    if B0 is None:
        B0, _, _ = ajustar(X, Y)
    Bc = np.clip(B0, 1e-6, None)
    eta0 = np.clip(np.log(Bc[:3, :3] / Bc[:3, 3:4]), -12, 12).ravel()
    extra = []
    for r in (3, 4):
        tL = min(0.98, 2 * Bc[r, 0])  # π médio ≈ 0,5: τ ≈ 2 × taxa média
        tF = min(0.98, 2 * Bc[r, 1])
        nu = Bc[r, 2] / max(1 - max(tL, tF), 1e-3)
        extra += [np.log(tL / (1 - tL)), np.log(tF / (1 - tF)), np.log(np.clip(nu, 1e-4, 0.999) / (1 - np.clip(nu, 1e-4, 0.999)))]
    x0 = np.concatenate([eta0, extra])
    res = minimize(_nll_M2, x0, args=(X, Y, pi), method="L-BFGS-B", options={"maxiter": max_iter, "ftol": 1e-12})
    return res.x, -res.fun, res


def pi_latente(df):
    s = (df.a_1 + df.b_1).to_numpy(float)
    with np.errstate(divide="ignore", invalid="ignore"):
        pi = np.where(s > 0, df.a_1.to_numpy(float) / s, 0.5)
    return pi


def deviance_unidades(P, Y):
    N = Y.sum(1, keepdims=True)
    E = N * np.clip(P, EPS, None)
    with np.errstate(divide="ignore", invalid="ignore"):
        return float(2 * np.where(Y > 0, Y * np.log(Y / E), 0.0).sum())
