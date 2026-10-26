"""Etapa 5 — Modelo C: simulação de Monte Carlo por famílias de cenários.

Cada família define uma distribuição de probabilidade para a matriz de
transição B (linhas = origem no 1T: Lula, Flávio, outros, brancos/nulos,
abstenção; colunas = destino no 2T: Lula, Flávio, brancos/nulos, abstenção).
Cada linha de B é sorteada de uma Dirichlet com média m_r e concentração k_r.

Etapas para cada sorteio:
  1. Sorteio "bruto": B ~ família. Mede-se o erro na previsão dos totais
     nacionais do 2º turno (quanto o cenário, sem ajuste, erra a aritmética).
  2. Calibração aritmética: a matriz de fluxos nacionais diag(R)·B é ajustada
     por raking (ajuste proporcional iterativo) para reproduzir exatamente os
     totais oficiais do 1º turno (linhas) e do 2º turno (colunas). O raking
     preserva as razões internas do sorteio o máximo possível (mínima
     divergência de Kullback-Leibler). Na família 4 o raking é feito por região.
  3. Ajuste territorial: a matriz calibrada é aplicada à composição do 1º
     turno de cada município; mede-se a distância entre o previsto e o
     observado no 2º turno (deviance multinomial por eleitor e RMSE da
     participação de Lula e de Flávio nos aptos, ponderados pelos aptos).

O que a simulação mostra: quais famílias, depois de obrigadas a respeitar a
aritmética nacional, reproduzem bem a distribuição territorial dos votos. A
fração de sorteios com bom ajuste NÃO é a probabilidade de a família ser
verdadeira: depende da largura arbitrária de cada família.

Estabilidade numérica: os sorteios são feitos em 4 lotes independentes; para
cada métrica relatam-se média e quantis por lote e o erro-padrão de Monte
Carlo; R-hat entre lotes próximo de 1 indica estabilidade.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from comum import INTERIM, REGIAO, SEMENTE, TABELAS, salvar_json

ORIG = ["a_1", "b_1", "o_1", "bn_1", "abst_1"]
DEST = ["a_2", "b_2", "bn_2", "abst_2"]
N_POR_LOTE, N_LOTES = 5000, 4

# (média da linha, concentração). Concentração alta = linha quase fixa.
FAMILIAS = {
    "C1_fidelidade_alta_transf_outros": {
        "descricao": "Fidelidade ~95% aos finalistas; trocas diretas ~1%; outros candidatos repartidos livremente; brancos/nulos e abstenção com pouca mobilização",
        "linhas": [([.95, .01, .01, .03], 400), ([.01, .95, .01, .03], 400), ([.40, .40, .10, .10], 4),
                   ([.10, .10, .70, .10], 50), ([.02, .02, .01, .95], 300)]},
    "C2_fidelidade_alta_mobilizacao": {
        "descricao": "Fidelidade ~95%; trocas diretas ~1%; outros repartidos livremente; mobilização de brancos/nulos e de abstencionistas com divisão livre entre os finalistas",
        "linhas": [([.95, .01, .01, .03], 400), ([.01, .95, .01, .03], 400), ([.40, .40, .10, .10], 4),
                   ([.25, .25, .35, .15], 4), ([.06, .06, .01, .87], 20)]},
    "C3_transferencias_moderadas": {
        "descricao": "Trocas diretas moderadas (~6%) nos dois sentidos; demais linhas largas",
        "linhas": [([.86, .06, .02, .06], 100), ([.06, .86, .02, .06], 100), ([.40, .40, .10, .10], 4),
                   ([.25, .25, .35, .15], 4), ([.06, .06, .01, .87], 20)]},
    "C4_heterogeneidade_regional": {
        "descricao": "Média nacional como em C3 com trocas diretas incertas (0–15%); cada região sorteia sua própria matriz em torno dela (concentração 30)",
        "linhas": [([.88, .05, .02, .05], 20), ([.05, .88, .02, .05], 20), ([.40, .40, .10, .10], 4),
                   ([.25, .25, .35, .15], 4), ([.06, .06, .01, .87], 20)],
        "regional_conc": 30},
}


def sortear_B(rng, linhas, n):
    B = np.empty((n, len(linhas), 4))
    for r, (m, k) in enumerate(linhas):
        B[:, r, :] = rng.dirichlet(np.asarray(m) * k, size=n)
    return B


def raking(F, linhas_alvo, colunas_alvo, it=200, tol=1e-10):
    """Ajuste proporcional iterativo (vetorizado em lote: F tem forma n×R×C)."""
    F = F.copy()
    for _ in range(it):
        F *= (linhas_alvo / np.clip(F.sum(-1), 1e-300, None))[..., None]
        F *= (colunas_alvo / np.clip(F.sum(-2), 1e-300, None))[..., None, :]
        if np.abs(F.sum(-1) - linhas_alvo).max() < tol * linhas_alvo.max():
            break
    return F


def metricas(B_unid, X, Y, N):
    """B_unid: n_sorteios × n_unid × R × C (ou n×R×C broadcast); devolve métricas por sorteio."""
    P = np.einsum("ur,surc->suc", X, B_unid) if B_unid.ndim == 4 else np.einsum("ur,src->suc", X, B_unid)
    P = np.clip(P, 1e-12, None)
    E = N[None, :, None] * P
    with np.errstate(divide="ignore", invalid="ignore"):
        dev = 2 * np.where(Y[None] > 0, Y[None] * np.log(Y[None] / E), 0).sum((1, 2))
    w = N / N.sum()
    obsL, obsF = Y[:, 0] / N, Y[:, 1] / N
    rmseL = np.sqrt((w[None] * (P[:, :, 0] - obsL[None]) ** 2).sum(1))
    rmseF = np.sqrt((w[None] * (P[:, :, 1] - obsF[None]) ** 2).sum(1))
    return dev / N.sum(), rmseL, rmseF


def rhat_lotes(v):
    """R-hat simples entre lotes (Gelman-Rubin) para a média de uma métrica."""
    m = v.shape[1]
    medias = v.mean(1)
    W = v.var(1, ddof=1).mean()
    Bv = m * medias.var(ddof=1)
    return float(np.sqrt(((m - 1) / m * W + Bv / m) / W))


def main() -> dict:
    mun = pd.read_parquet(INTERIM / "municipios_2026.parquet")
    R = mun[ORIG].to_numpy(float, copy=True)
    Y = mun[DEST].to_numpy(float, copy=True)
    d = Y.sum(1) - R.sum(1)
    R[:, -1] += np.clip(d, 0, None)
    Y[:, -1] += np.clip(-d, 0, None)
    N = R.sum(1)
    X = R / N[:, None]
    reg = mun.uf.map(REGIAO).to_numpy()
    regioes = sorted(set(reg))
    ridx = np.array([regioes.index(x) for x in reg])
    Rtot, Ytot = R.sum(0), Y.sum(0)
    Rreg = np.array([R[ridx == k].sum(0) for k in range(len(regioes))])
    Yreg = np.array([Y[ridx == k].sum(0) for k in range(len(regioes))])

    rng_mestre = np.random.default_rng(SEMENTE)
    sementes_lote = rng_mestre.integers(0, 2**31, size=(len(FAMILIAS), N_LOTES))
    resultados, sorteios_guardados, estab = [], {}, []
    for f_i, (nome, fam) in enumerate(FAMILIAS.items()):
        lotes = []
        for lote in range(N_LOTES):
            rng = np.random.default_rng(sementes_lote[f_i, lote])
            Bn = sortear_B(rng, fam["linhas"], N_POR_LOTE)
            # 1. erro bruto nos totais nacionais (pontos percentuais dos aptos)
            prev = np.einsum("r,src->sc", Rtot, Bn)
            erro_bruto = 100 * (prev - Ytot[None]) / Ytot.sum()
            if "regional_conc" in fam:
                k = fam["regional_conc"]
                Breg = np.empty((N_POR_LOTE, len(regioes), 5, 4))
                for g in range(len(regioes)):
                    for r in range(5):
                        Breg[:, g, r, :] = np.array([rng.dirichlet(np.clip(Bn[s, r] * k, 1e-3, None))
                                                     for s in range(N_POR_LOTE)])
                Fl = raking(Rreg[None, :, :, None] * Breg, Rreg[None], Yreg[None])
                Bcal_reg = Fl / Rreg[None, :, :, None]
                Bcal_nac = Fl.sum(1) / Rtot[None, :, None]
                Bunid = Bcal_reg[:, ridx]
                dev, rL, rF = [], [], []
                for s0 in range(0, N_POR_LOTE, 250):
                    a, b, c = metricas(Bunid[s0:s0 + 250], X, Y, N)
                    dev.append(a); rL.append(b); rF.append(c)
                dev, rL, rF = map(np.concatenate, (dev, rL, rF))
            else:
                Fl = raking(Rtot[None, :, None] * Bn, Rtot[None], Ytot[None])
                Bcal_nac = Fl / Rtot[None, :, None]
                dev, rL, rF = [], [], []
                for s0 in range(0, N_POR_LOTE, 500):
                    a, b, c = metricas(Bcal_nac[s0:s0 + 500], X, Y, N)
                    dev.append(a); rL.append(b); rF.append(c)
                dev, rL, rF = map(np.concatenate, (dev, rL, rF))
            df = pd.DataFrame({
                "familia": nome, "lote": lote,
                "erro_bruto_lula_pp": erro_bruto[:, 0], "erro_bruto_flavio_pp": erro_bruto[:, 1],
                "erro_bruto_max_abs_pp": np.abs(erro_bruto).max(1),
                "bruto_FL": Bn[:, 1, 0], "bruto_LF": Bn[:, 0, 1],
                "cal_LL": Bcal_nac[:, 0, 0], "cal_LF": Bcal_nac[:, 0, 1],
                "cal_FL": Bcal_nac[:, 1, 0], "cal_FF": Bcal_nac[:, 1, 1],
                "cal_OL": Bcal_nac[:, 2, 0], "cal_OF": Bcal_nac[:, 2, 1],
                "cal_BNL": Bcal_nac[:, 3, 0], "cal_BNF": Bcal_nac[:, 3, 1],
                "cal_AL": Bcal_nac[:, 4, 0], "cal_AF": Bcal_nac[:, 4, 1],
                "dev_por_eleitor": dev, "rmse_lula": rL, "rmse_flavio": rF,
            })
            lotes.append(df)
        df = pd.concat(lotes, ignore_index=True)
        resultados.append(df)
        for met in ["dev_por_eleitor", "rmse_lula", "rmse_flavio", "cal_FL", "cal_LF"]:
            v = df.pivot(columns="lote", values=met).apply(lambda c: c.dropna().to_numpy()).T.to_numpy()
            v = np.stack([df[df.lote == l][met].to_numpy() for l in range(N_LOTES)])
            estab.append({"familia": nome, "metrica": met, "media": v.mean(),
                          "mcse_media": v.mean(1).std(ddof=1) / np.sqrt(N_LOTES),
                          "q05_por_lote": np.round(np.quantile(v, .05, axis=1), 6).tolist(),
                          "q50_por_lote": np.round(np.quantile(v, .5, axis=1), 6).tolist(),
                          "rhat_lotes": rhat_lotes(v)})
        print(nome, "ok", flush=True)

    todos = pd.concat(resultados, ignore_index=True)
    todos.to_parquet(INTERIM / "monte_carlo_sorteios.parquet", index=False)
    # Referência: melhor ajuste possível com matriz nacional única (Modelo A, nível município, sem UF)
    from ei import ajustar, deviance
    Bref, _, _ = ajustar(X, Y)
    dev_ref = deviance(Bref, X, Y) / N.sum()
    lim = dev_ref * 1.10  # sorteios a até 10% da deviance mínima com matriz nacional única
    resumo = []
    for nome, g in todos.groupby("familia", sort=False):
        bons = g[g.dev_por_eleitor <= lim]
        resumo.append({
            "familia": nome, "descricao": FAMILIAS[nome]["descricao"], "sorteios": len(g),
            "erro_bruto_lula_pp_mediana": g.erro_bruto_lula_pp.median(),
            "frac_bruto_dentro_1pp_todos_destinos": (g.erro_bruto_max_abs_pp <= 1).mean(),
            "dev_por_eleitor_min": g.dev_por_eleitor.min(), "dev_por_eleitor_mediana": g.dev_por_eleitor.median(),
            "rmse_lula_mediana": g.rmse_lula.median(), "rmse_lula_min": g.rmse_lula.min(),
            "rmse_flavio_mediana": g.rmse_flavio.median(),
            "frac_ajuste_ate_10pct_acima_do_minimo": len(bons) / len(g),
            "cal_FL_mediana": g.cal_FL.median(), "cal_FL_q05": g.cal_FL.quantile(.05), "cal_FL_q95": g.cal_FL.quantile(.95),
            "cal_LF_mediana": g.cal_LF.median(),
            "cal_FL_mediana_bons": bons.cal_FL.median() if len(bons) else np.nan,
            "cal_FL_q05_bons": bons.cal_FL.quantile(.05) if len(bons) else np.nan,
            "cal_FL_q95_bons": bons.cal_FL.quantile(.95) if len(bons) else np.nan,
            "cal_AL_mediana_bons": bons.cal_AL.median() if len(bons) else np.nan,
            "cal_BNL_mediana_bons": bons.cal_BNL.median() if len(bons) else np.nan,
            "cal_OL_mediana_bons": bons.cal_OL.median() if len(bons) else np.nan,
        })
    rs = pd.DataFrame(resumo)
    rs.to_csv(TABELAS / "05_monte_carlo_resumo.csv", index=False)
    pd.DataFrame(estab).to_csv(TABELAS / "05_monte_carlo_estabilidade.csv", index=False)
    salvar_json({"n_por_lote": N_POR_LOTE, "n_lotes": N_LOTES, "semente": SEMENTE,
                 "dev_ref_matriz_nacional_unica": dev_ref, "limiar_bom_ajuste": lim,
                 "B_ref": Bref.round(5).tolist(),
                 "familias": {k: {"descricao": v["descricao"], "linhas": v["linhas"],
                                  "regional_conc": v.get("regional_conc")} for k, v in FAMILIAS.items()}},
                TABELAS / "05_monte_carlo_parametros.json")
    with pd.option_context("display.width", 250, "display.max_columns", 40, "display.float_format", "{:,.4f}".format):
        print("deviance de referência:", dev_ref)
        print(rs.drop(columns="descricao").T)
        print(pd.DataFrame(estab)[["familia", "metrica", "media", "mcse_media", "rhat_lotes"]])
    return rs.to_dict()


if __name__ == "__main__":
    main()
