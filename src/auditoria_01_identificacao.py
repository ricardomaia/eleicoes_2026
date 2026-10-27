"""Auditoria 1 — Identificabilidade da matriz de transição e conjuntos identificados.

Quatro análises, todas sobre a amostra de 50.821 seções com BU do 2º turno
(e, onde indicado, sobre os 5.757 municípios):

1. Condicionamento. Sob a hipótese de constância (mesma matriz B em todas as
   seções da UF), a esperança da composição do 2º turno é p_i = x_i·B. B é
   identificada se a matriz X (n×5) tiver posto 5; o condicionamento diz quão
   bem. Calcula-se a decomposição em valores singulares de X ponderada por
   √N por UF.

2. Regressão de Goodman sem restrições. Mínimos quadrados ponderados de
   y_ic/N_i sobre x_i (sem intercepto), com erro-padrão robusto a
   conglomerados (municípios). É o estimador clássico; sem as restrições
   B ≥ 0 e linhas = 1, mostra onde a informação dos dados realmente está e
   quanto do "0,2%" vem do piso em zero. A taxa nacional é a média das UFs
   ponderada pelos eleitores de Flávio no 1º turno; o erro-padrão nacional
   supõe UFs independentes.

3. Conjuntos identificados por programação linear, sem a hipótese de
   constância. Em cada unidade i a matriz de fluxos M_i (5×4, contagens) só
   precisa ter linhas = origens do 1T e colunas = destinos do 2T. Os limites
   de Fréchet (S0) são o caso sem hipótese nenhuma. Acrescentam-se conjuntos
   de hipóteses moderadas e defensáveis (S1–S4: fidelidade mínima, abstenção
   máxima entre quem votou nos finalistas, mobilização máxima de
   abstencionistas) e recalculam-se os limites mínimo e máximo de cada fluxo
   por programação linear, unidade a unidade. Unidades em que uma hipótese é
   impossível (ex.: Lula perdeu mais de 10% dos votos de 1T na seção) são
   contadas e, para elas, usa-se o limite de Fréchet.

4. Fronteira de heterogeneidade. Fixada uma taxa nacional c de Flávio→Lula,
   qual é a menor fração do eleitorado cujo comportamento precisa desviar de
   uma matriz comum à UF para que TODAS as seções sejam reproduzidas
   exatamente? É um único programa linear por UF e por c, com variáveis
   (B̄, M_1..M_n, D_1..D_n): minimizar Σ D /(2ΣN) sujeito a
   |M_i[r,c] − R_i[r]·B̄[r,c]| ≤ D_i[r,c], M_i nas margens da seção, B̄[F,L] = c.
   Se a fronteira for quase plana entre c = 0,2% e c = 5%, os dados não
   distinguem essas taxas sem a hipótese de constância; se subir muito, a
   distinção vem da variação entre seções. O ótimo com c livre é um
   estimador de desvio absoluto mínimo (robusto), comparável ao EM.
   Por custo, usa-se uma subamostra aleatória de até 600 seções por UF.

Saídas em resultados/auditoria/tabelas/01_*.csv e 01_resumo.json.
"""
from __future__ import annotations

import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd
import scipy.sparse as sp
from scipy.optimize import linprog

from auditoria_comum import (SUFIXO, DEST, ORIG, TAB, amostra_2026, iA, iBN, iF, iL, iO, jA, jBN, jF, jL,
                             matrizes_RC, municipios_2026, salvar_json, todas_secoes_2026, totais_por_uf)
from comum import SEMENTE

CONJUNTOS = {
    "S0_sem_hipoteses": {},
    "S1_fidelidade_90": {(iL, jL): (0.90, 1.0), (iF, jF): (0.90, 1.0)},
    "S2_fid90_abst_finalistas_10": {(iL, jL): (0.90, 1.0), (iF, jF): (0.90, 1.0),
                                    (iL, jA): (0.0, 0.10), (iF, jA): (0.0, 0.10)},
    "S3_S2_mais_abstencao_fica_70": {(iL, jL): (0.90, 1.0), (iF, jF): (0.90, 1.0),
                                     (iL, jA): (0.0, 0.10), (iF, jA): (0.0, 0.10), (iA, jA): (0.70, 1.0)},
    "S4_fidelidade_95": {(iL, jL): (0.95, 1.0), (iF, jF): (0.95, 1.0)},
}
CELULAS_SECAO = [(iF, jL), (iL, jF)]
CELULAS_MUN = [(iF, jL), (iL, jF), (iO, jL), (iBN, jL), (iA, jL), (iO, jF), (iBN, jF), (iA, jF)]
# Cada programa linear com n seções tem 40n + 20 variáveis e 48n restrições; com 1.500 seções leva
# cerca de 6 minutos, com 600 cerca de 1 minuto. A execução registrada usou 600 seções por UF.
TETOS_FRONTEIRA = [None, 0.0, 0.002, 0.02, 0.05, 0.10]
MAX_SECOES_FRONTEIRA = 600

_A_EQ = None


def _a_eq_secao():
    """Matriz de igualdades da unidade: 5 linhas (origens) + 3 colunas (destinos; a 4ª é redundante)."""
    global _A_EQ
    if _A_EQ is None:
        A = np.zeros((8, 20))
        for r in range(5):
            A[r, r * 4:(r + 1) * 4] = 1
        for c in range(3):
            A[5 + c, [r * 4 + c for r in range(5)]] = 1
        _A_EQ = A
    return _A_EQ


# ----------------------------------------------------------------------------- 1. condicionamento
def condicionamento(am: pd.DataFrame) -> pd.DataFrame:
    out = []
    for uf, g in am.groupby("uf"):
        R, C, N, _ = matrizes_RC(g)
        X = R / N[:, None]
        W = np.sqrt(N)[:, None] * X
        s = np.linalg.svd(W, compute_uv=False)
        corr = np.corrcoef(X.T)
        np.fill_diagonal(corr, 0)
        out.append({"uf": uf, "secoes": len(g), "posto": int((s > 1e-8 * s[0]).sum()), "sv_max": s[0], "sv_min": s[-1],
                    "numero_condicao": s[0] / s[-1], "max_corr_abs_entre_origens": float(np.abs(corr).max()),
                    "dp_share_flavio": float(X[:, iF].std()), "dp_share_abst": float(X[:, iA].std())})
    return pd.DataFrame(out)


# ----------------------------------------------------------------------------- 2. Goodman WLS
def goodman_wls(df: pd.DataFrame, grupo: str = "cd_mun") -> pd.DataFrame:
    import statsmodels.api as sm
    out = []
    for uf, g in df.groupby("uf"):
        R, C, N, ok = matrizes_RC(g)
        if len(R) < 10:  # DF no nível municipal tem uma única unidade: não há regressão possível
            continue
        X = R / N[:, None]
        cl = pd.factorize(g[grupo].to_numpy()[ok])[0]
        for j, d in enumerate(DEST):
            y = C[:, j] / N
            mod = sm.WLS(y, X, weights=N)
            fit = mod.fit(cov_type="cluster", cov_kwds={"groups": cl}) if len(np.unique(cl)) > 2 else mod.fit(cov_type="HC1")
            for i, o in enumerate(ORIG):
                out.append({"uf": uf, "origem": o, "destino": d, "coef": fit.params[i], "ep": fit.bse[i],
                            "unidades": len(y), "conglomerados": int(len(np.unique(cl)))})
    return pd.DataFrame(out)


def goodman_nacional(t: pd.DataFrame, totais: pd.DataFrame) -> pd.DataFrame:
    out = []
    for (o, d), g in t.groupby(["origem", "destino"]):
        g = g.set_index("uf")
        w = totais.loc[g.index, o].to_numpy(float)
        w = w / w.sum()
        coef = float((w * g.coef).sum())
        ep = float(np.sqrt((w ** 2 * g.ep ** 2).sum()))
        out.append({"origem": o, "destino": d, "coef_nacional": coef, "ep_nacional": ep,
                    "ic95_inf": coef - 1.96 * ep, "ic95_sup": coef + 1.96 * ep,
                    "ufs_coef_negativo": int((g.coef < 0).sum()),
                    "ufs_ic95_exclui_zero": int(((g.coef - 1.96 * g.ep > 0) | (g.coef + 1.96 * g.ep < 0)).sum())})
    return pd.DataFrame(out)


# ----------------------------------------------------------------------------- 3. limites por LP (unidade a unidade)
def _limites_unidade(args):
    R, C, celulas, conjuntos = args
    A = _a_eq_secao()
    b = np.concatenate([R, C[:3]])
    res = {}
    for nome, lim in conjuntos.items():
        bounds = [(0.0, R[r]) for r in range(5) for c in range(4)]
        for (r, c), (lo, hi) in lim.items():
            bounds[r * 4 + c] = (lo * R[r], hi * R[r])
        viavel = True
        for (r, c) in celulas:
            obj = np.zeros(20)
            obj[r * 4 + c] = 1.0
            lo = linprog(obj, A_eq=A, b_eq=b, bounds=bounds, method="highs")
            if lo.status != 0:
                viavel = False
                break
            hi = linprog(-obj, A_eq=A, b_eq=b, bounds=bounds, method="highs")
            res[(nome, r, c)] = (lo.fun, -hi.fun, True)
        if not viavel:
            for (r, c) in celulas:  # hipótese impossível nesta unidade: usa Fréchet
                N = R.sum()
                res[(nome, r, c)] = (max(0.0, R[r] + C[c] - N), min(R[r], C[c]), False)
    return res


def limites_lp(df: pd.DataFrame, celulas, nivel: str, totais: pd.DataFrame | None, workers: int) -> pd.DataFrame:
    R, C, N, ok = matrizes_RC(df)
    ufs = df.uf.to_numpy()[ok]
    tarefas = [(R[i], C[i], celulas, CONJUNTOS) for i in range(len(R))]
    t0 = time.time()
    with ProcessPoolExecutor(workers) as ex:
        res = list(ex.map(_limites_unidade, tarefas, chunksize=200))
    print(f"  {nivel}: {len(res)} unidades, {time.time() - t0:.0f}s", flush=True)
    linhas = []
    for nome in CONJUNTOS:
        for (r, c) in celulas:
            lo = np.array([x[(nome, r, c)][0] for x in res])
            hi = np.array([x[(nome, r, c)][1] for x in res])
            vi = np.array([x[(nome, r, c)][2] for x in res])
            reg = {"nivel": nivel, "conjunto": nome, "origem": ORIG[r], "destino": DEST[c],
                   "unidades": len(lo), "unidades_hipotese_impossivel": int((~vi).sum()),
                   "min_votos_soma": lo.sum(), "max_votos_soma": hi.sum(),
                   "min_taxa_soma": lo.sum() / R[:, r].sum(), "max_taxa_soma": hi.sum() / R[:, r].sum()}
            if totais is not None:  # expansão: taxa por UF × total da origem na UF (todas as seções)
                tmin = tmax = 0.0
                for uf in np.unique(ufs):
                    m = ufs == uf
                    tot = float(totais.loc[uf, ORIG[r]])
                    den = R[m, r].sum()
                    if den > 0:
                        tmin += tot * lo[m].sum() / den
                        tmax += tot * hi[m].sum() / den
                T = float(totais[ORIG[r]].sum())
                reg.update({"min_taxa_expandida": tmin / T, "max_taxa_expandida": tmax / T,
                            "min_votos_expandidos": tmin, "max_votos_expandidos": tmax})
            linhas.append(reg)
    return pd.DataFrame(linhas)


# ----------------------------------------------------------------------------- 4. fronteira de heterogeneidade
def _fronteira_uf(args):
    uf, R, C, c_fixo = args
    n = len(R)
    nB, nM = 20, 20 * n
    nv = nB + 2 * nM
    N_tot = R.sum()
    # igualdades: linhas de B̄ = 1 (5); linhas de M_i (5n); colunas de M_i (3n)
    rows, cols, vals, beq = [], [], [], []
    k = 0
    for r in range(5):
        for c in range(4):
            rows.append(k); cols.append(r * 4 + c); vals.append(1.0)
        beq.append(1.0); k += 1
    for i in range(n):
        base = nB + 20 * i
        for r in range(5):
            for c in range(4):
                rows.append(k); cols.append(base + r * 4 + c); vals.append(1.0)
            beq.append(R[i, r]); k += 1
        for c in range(3):
            for r in range(5):
                rows.append(k); cols.append(base + r * 4 + c); vals.append(1.0)
            beq.append(C[i, c]); k += 1
    A_eq = sp.csr_matrix((vals, (rows, cols)), shape=(k, nv))
    # desigualdades: M − R·B̄ − D ≤ 0 ; −M + R·B̄ − D ≤ 0
    rows, cols, vals = [], [], []
    k = 0
    for i in range(n):
        for r in range(5):
            for c in range(4):
                m = nB + 20 * i + r * 4 + c
                d = nB + nM + 20 * i + r * 4 + c
                b = r * 4 + c
                rows += [k, k, k]; cols += [m, b, d]; vals += [1.0, -R[i, r], -1.0]; k += 1
                rows += [k, k, k]; cols += [m, b, d]; vals += [-1.0, R[i, r], -1.0]; k += 1
    A_ub = sp.csr_matrix((vals, (rows, cols)), shape=(k, nv))
    b_ub = np.zeros(k)
    obj = np.zeros(nv)
    obj[nB + nM:] = 1.0 / (2 * N_tot)
    bounds = [(0.0, 1.0)] * nB
    if c_fixo is not None:
        bounds[iF * 4 + jL] = (c_fixo, c_fixo)
    for i in range(n):
        for r in range(5):
            bounds += [(0.0, R[i, r])] * 4
    bounds += [(0.0, None)] * nM
    t0 = time.time()
    res = linprog(obj, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=beq, bounds=bounds, method="highs")
    if res.status != 0:
        return {"uf": uf, "teto_FL": c_fixo, "status": res.status, "secoes": n, "tempo_s": time.time() - t0}
    B = res.x[:nB].reshape(5, 4)
    return {"uf": uf, "teto_FL": c_fixo, "status": 0, "secoes": n, "eleitores": N_tot,
            "fracao_minima_desviante": res.fun, "tempo_s": time.time() - t0,
            **{f"B_{ORIG[r]}_{DEST[c]}": B[r, c] for r in range(5) for c in range(4)}}


def fronteira(am: pd.DataFrame, workers: int) -> pd.DataFrame:
    rng = np.random.default_rng(SEMENTE + 101)
    tarefas = []
    for uf, g in am.groupby("uf"):
        if len(g) > MAX_SECOES_FRONTEIRA:
            g = g.iloc[np.sort(rng.choice(len(g), MAX_SECOES_FRONTEIRA, replace=False))]
        R, C, N, _ = matrizes_RC(g)
        for c in TETOS_FRONTEIRA:
            tarefas.append((uf, R, C, c))
    t0 = time.time()
    with ProcessPoolExecutor(workers) as ex:
        res = list(ex.map(_fronteira_uf, tarefas))
    print(f"  fronteira: {len(res)} programas lineares, {time.time() - t0:.0f}s", flush=True)
    return pd.DataFrame(res)


def resumo_fronteira(fr: pd.DataFrame, totais: pd.DataFrame) -> pd.DataFrame:
    """Fronteira nacional: média das UFs ponderada pelo eleitorado (todas as seções)."""
    w = totais.sum(1)
    out = []
    for c, g in fr[fr.status == 0].groupby("teto_FL", dropna=False):
        g = g.set_index("uf")
        ww = w.loc[g.index] / w.loc[g.index].sum()
        reg = {"teto_FL": c, "ufs": len(g), "fracao_minima_desviante_media_pond": float((ww * g.fracao_minima_desviante).sum()),
               "fracao_minima_desviante_max_uf": float(g.fracao_minima_desviante.max()),
               "uf_max": g.fracao_minima_desviante.idxmax()}
        for col in [k for k in g.columns if k.startswith("B_")]:
            tot = totais.loc[g.index, col.split("_")[1] + "_" + col.split("_")[2]]
            reg[col + "_nacional"] = float((tot * g[col]).sum() / tot.sum())
        out.append(reg)
    return pd.DataFrame(out)


# ----------------------------------------------------------------------------- 5. exemplo construtivo
def equivalentes_construtivos(am: pd.DataFrame, Bs_ref: dict) -> pd.DataFrame:
    """Família explícita de matrizes observacionalmente equivalentes à matriz da UF:
    B_i = B̂ + Δ_i com x_i·Δ_i = 0. Δ_i sobe Flávio→Lula em δ e desce Flávio→abstenção em δ;
    compensa na linha da abstenção do 1T: abst→Lula desce δ·x_F/x_A e abst→abst sobe o mesmo.
    A esperança de cada seção (x_i·B_i) é idêntica à do modelo ajustado, logo a
    verossimilhança é idêntica. Conta-se em quantas seções (e eleitores) a família
    cabe em [0, 1] para cada δ, sem usar nenhuma outra linha."""
    out = []
    for delta in (0.01, 0.02, 0.05, 0.10, 0.15):
        cabe_sec = cabe_ele = tot_sec = tot_ele = 0
        for uf, g in am.groupby("uf"):
            B = Bs_ref[uf]
            R, C, N, _ = matrizes_RC(g)
            X = R / N[:, None]
            with np.errstate(divide="ignore", invalid="ignore"):
                comp = np.where(X[:, iA] > 0, delta * X[:, iF] / X[:, iA], np.inf)
            ok = (B[iF, jA] - delta >= 0) & (B[iA, jL] - comp >= 0) & (B[iA, jA] + comp <= 1) & (B[iF, jL] + delta <= 1)
            cabe_sec += ok.sum(); cabe_ele += N[ok].sum(); tot_sec += len(ok); tot_ele += N.sum()
        out.append({"delta_FL_adicional": delta, "secoes_em_que_cabe": int(cabe_sec), "pct_secoes": 100 * cabe_sec / tot_sec,
                    "pct_eleitores": 100 * cabe_ele / tot_ele,
                    "observacao": "compensação só nas linhas Flávio e abstenção; com as linhas brancos/nulos e outros cabe em mais seções"})
    return pd.DataFrame(out)


def main(workers: int = 14, so_fronteira: bool = False):
    am = amostra_2026()
    am = am[am.uf != "ZZ"]
    sec = todas_secoes_2026()
    sec = sec[sec.uf != "ZZ"]
    mun = municipios_2026()
    mun = mun[(mun.uf != "ZZ") & (mun.aptos_1 > 0)]
    totais = totais_por_uf(sec)
    resumo = {"fronteira_max_secoes_por_uf": MAX_SECOES_FRONTEIRA, "fronteira_tetos": TETOS_FRONTEIRA}
    if so_fronteira:  # etapas 4 e 5 apenas (as etapas 1 a 3 já gravadas são mantidas)
        print("4. fronteira de heterogeneidade", flush=True)
        fr = fronteira(am, workers)
        fr.to_csv(TAB / f"01_fronteira_heterogeneidade_por_uf{SUFIXO}.csv", index=False)
        rf = resumo_fronteira(fr, totais)
        rf.to_csv(TAB / f"01_fronteira_heterogeneidade_nacional{SUFIXO}.csv", index=False)
        print("5. equivalentes construtivos", flush=True)
        from ei import ajustar
        Bs = {}
        for uf, g in am.groupby("uf"):
            R, C, N, _ = matrizes_RC(g)
            Bs[uf], _, _ = ajustar(R / N[:, None], C)
        eq = equivalentes_construtivos(am, Bs)
        eq.to_csv(TAB / f"01_equivalentes_construtivos{SUFIXO}.csv", index=False)
        salvar_json(resumo, TAB / f"01_resumo_fronteira{SUFIXO}.json")
        with pd.option_context("display.width", 250, "display.max_columns", 40, "display.float_format", "{:,.5f}".format):
            print(rf.to_string())
            print(eq.to_string())
        return

    print("1. condicionamento", flush=True)
    cond = condicionamento(am)
    cond.to_csv(TAB / f"01_condicionamento_por_uf{SUFIXO}.csv", index=False)
    resumo["posto_minimo"] = int(cond.posto.min())
    resumo["numero_condicao_max"] = float(cond.numero_condicao.max())

    print("2. Goodman WLS", flush=True)
    g_uf = goodman_wls(am)
    g_uf.to_csv(TAB / f"01_goodman_wls_por_uf_secao{SUFIXO}.csv", index=False)
    g_nac = goodman_nacional(g_uf, totais)
    g_nac["nivel"] = "secao (amostra)"
    gm_uf = goodman_wls(mun, grupo="cd_mun")
    gm_nac = goodman_nacional(gm_uf, totais)
    gm_nac["nivel"] = "municipio (todos)"
    pd.concat([g_nac, gm_nac]).to_csv(TAB / f"01_goodman_wls_nacional{SUFIXO}.csv", index=False)
    fl = g_nac[(g_nac.origem == "b_1") & (g_nac.destino == "a_2")].iloc[0]
    resumo["goodman_FL_secao"] = {"coef": float(fl.coef_nacional), "ep": float(fl.ep_nacional),
                                  "ic95": [float(fl.ic95_inf), float(fl.ic95_sup)]}

    print("3. limites por programação linear", flush=True)
    t_sec = limites_lp(am, CELULAS_SECAO, "secao (amostra)", totais, workers)
    t_mun = limites_lp(mun, CELULAS_MUN, "municipio (todos)", None, workers)
    lim = pd.concat([t_sec, t_mun], ignore_index=True)
    lim.to_csv(TAB / f"01_limites_lp_conjuntos_hipoteses{SUFIXO}.csv", index=False)

    print("4. fronteira de heterogeneidade", flush=True)
    fr = fronteira(am, workers)
    fr.to_csv(TAB / f"01_fronteira_heterogeneidade_por_uf{SUFIXO}.csv", index=False)
    rf = resumo_fronteira(fr, totais)
    rf.to_csv(TAB / f"01_fronteira_heterogeneidade_nacional{SUFIXO}.csv", index=False)

    print("5. equivalentes construtivos", flush=True)
    from ei import ajustar
    Bs = {}
    for uf, g in am.groupby("uf"):
        R, C, N, _ = matrizes_RC(g)
        Bs[uf], _, _ = ajustar(R / N[:, None], C)
    eq = equivalentes_construtivos(am, Bs)
    eq.to_csv(TAB / f"01_equivalentes_construtivos{SUFIXO}.csv", index=False)

    salvar_json(resumo, TAB / f"01_resumo{SUFIXO}.json")
    with pd.option_context("display.width", 250, "display.max_columns", 40, "display.float_format", "{:,.5f}".format):
        print(cond.to_string())
        print(pd.concat([g_nac, gm_nac]).to_string())
        print(lim[["nivel", "conjunto", "origem", "destino", "unidades_hipotese_impossivel", "min_taxa_soma", "max_taxa_soma"]
                  + [c for c in ("min_taxa_expandida", "max_taxa_expandida") if c in lim]].to_string())
        print(rf.to_string())
        print(eq.to_string())


if __name__ == "__main__":
    import sys
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    main(workers=int(args[0]) if args else 6, so_fronteira="--so-fronteira" in sys.argv)
