"""Inferência ecológica R×C por quase-verossimilhança multinomial com restrições.

Modelo (por UF s): para cada unidade i (seção ou município),
    contagens do 2º turno y_i ~ Multinomial(N_i, p_i),  p_i = x_i · B_s
onde x_i é a composição do 1º turno (proporções das origens sobre os aptos) e
B_s é a matriz de transição (linhas = origens do 1T, colunas = destinos do 2T),
com B ≥ 0 e cada linha somando 1. A hipótese central é que, dentro da UF, a
probabilidade de transição de cada grupo de origem é a mesma em todas as
unidades (hipótese de constância, de Goodman). Desvios dessa hipótese aparecem
como sobredispersão (φ > 1) e são levados em conta nos testes (quase-
verossimilhança: a deviance é dividida por φ).

A log-verossimilhança é côncava em B, mas não estritamente: há direções em que
B muda e o ajuste não muda (não identificação). Por isso, além da estimativa
pontual, calculam-se:
  - intervalos de bootstrap por conglomerado (municípios), que medem a
    variabilidade amostral do ajuste;
  - ajustes com restrições sobre uma célula (ex.: taxa Flávio→Lula ≤ c) e o
    aumento de deviance correspondente, que mede quanto pior fica o ajuste
    quando se impõe uma hipótese (teste F de quase-verossimilhança).

Ajuste de cadastro: aptos que só existem no 2º turno são somados à abstenção do
1º turno; aptos que só existem no 1º turno são somados à abstenção do 2º turno
(ambos < 0,05% do eleitorado; ver 01_reconciliacao).
"""
from __future__ import annotations

import numpy as np
from scipy import stats

EPS = 1e-12


def preparar(df, origens, destinos):
    R = df[origens].to_numpy(float, copy=True)
    C = df[destinos].to_numpy(float, copy=True)
    d = C.sum(1) - R.sum(1)
    R[:, -1] += np.clip(d, 0, None)   # última origem = abstenção 1T
    C[:, -1] += np.clip(-d, 0, None)  # último destino = abstenção 2T
    N = R.sum(1)
    ok = N > 0
    return R[ok], C[ok], N[ok], ok


def loglik(B, X, Y):
    P = np.clip(X @ B, EPS, None)
    return float((Y * np.log(P)).sum())


def _passo_m(Z, limites_celula):
    """Passo M: B ∝ Z por linha, respeitando limites (r, c) -> (min, max) de forma exata."""
    B = Z / np.clip(Z.sum(1, keepdims=True), EPS, None)
    if limites_celula:
        for (r, c), (lo, hi) in limites_celula.items():
            alvo = min(max(B[r, c], lo), hi)
            if alvo != B[r, c]:
                outros = np.delete(np.arange(B.shape[1]), c)
                resto = Z[r, outros]
                B[r, outros] = (1 - alvo) * (resto / resto.sum() if resto.sum() > 0 else 1 / len(outros))
                B[r, c] = alvo
    return B


def _em(B, X, Y, limites_celula):
    P = np.clip(X @ B, EPS, None)
    return _passo_m(B * (X.T @ (Y / P)), limites_celula)


def ajustar(X, Y, B0=None, limites_celula=None, max_iter=20000, tol=1e-11):
    """Maximiza a log-verossimilhança multinomial sob B ≥ 0, linhas somando 1.

    Algoritmo EM (cada passo nunca reduz a verossimilhança) com aceleração
    SQUAREM (Varadhan e Roland, 2008). Restrições de célula são impostas de
    forma exata no passo M.
    X: n×R proporções do 1T; Y: n×C contagens do 2T.
    limites_celula: dict {(r, c): (min, max)} para impor hipóteses.
    """
    nR, nC = X.shape[1], Y.shape[1]
    B = np.full((nR, nC), 1.0 / nC) if B0 is None else B0.copy()
    B = _passo_m(np.clip(B, 1e-6, None), limites_celula)
    ll = loglik(B, X, Y)
    escala = abs(ll) + 1
    convergiu = False
    pequenos = 0
    for it in range(max_iter):
        B1 = _em(B, X, Y, limites_celula)
        B2 = _em(B1, X, Y, limites_celula)
        r = B1 - B
        v = B2 - B1 - r
        nv = np.sqrt((v ** 2).sum())
        if nv > 0:
            a = -np.sqrt((r ** 2).sum()) / nv
            Bt = B - 2 * a * r + a * a * v
            # piso positivo: no EM uma célula exatamente zero não volta a crescer
            Bt = _passo_m(np.clip(Bt, 1e-9, None), limites_celula)
            Bt = _em(Bt, X, Y, limites_celula)
            llt = loglik(Bt, X, Y)
        else:
            llt = -np.inf
        ll2 = loglik(B2, X, Y)
        Bn, lln = (Bt, llt) if llt >= ll2 else (B2, ll2)
        ganho = lln - ll
        B, ll = Bn, lln
        pequenos = pequenos + 1 if abs(ganho) < tol * escala else 0
        if pequenos >= 5:
            convergiu = True
            break

    class _Res:
        success = convergiu
        nit = it + 1
    return B, ll, _Res()


def deviance(B, X, Y):
    N = Y.sum(1, keepdims=True)
    P = np.clip(X @ B, EPS, None)
    E = N * P
    with np.errstate(divide="ignore", invalid="ignore"):
        termo = np.where(Y > 0, Y * np.log(Y / E), 0.0)
    return float(2 * termo.sum())


def sobredispersao(B, X, Y):
    """φ de Pearson: Σ (y − Np)² / (Np) / gl."""
    N = Y.sum(1, keepdims=True)
    E = np.clip(N * (X @ B), EPS, None)
    gl = Y.size - Y.shape[0] - B.shape[0] * (B.shape[1] - 1)
    return float(((Y - E) ** 2 / E).sum() / max(gl, 1)), gl


def teste_restricao(dev_u, dev_r, phi, k, gl):
    """Teste F de quase-verossimilhança para k restrições."""
    F = max(dev_r - dev_u, 0) / (k * max(phi, 1e-12))
    return F, float(stats.f.sf(F, k, gl))


def bootstrap_conglomerados(X, Y, grupos, B_hat, n_boot, rng):
    """Reamostra conglomerados (municípios) com reposição; reajusta B."""
    ug, inv = np.unique(grupos, return_inverse=True)
    idx_por_g = [np.flatnonzero(inv == g) for g in range(len(ug))]
    saida = np.empty((n_boot,) + B_hat.shape)
    for b in range(n_boot):
        esc = rng.integers(0, len(ug), len(ug))
        idx = np.concatenate([idx_por_g[g] for g in esc])
        saida[b], _, _ = ajustar(X[idx], Y[idx], B0=B_hat)
    return saida
