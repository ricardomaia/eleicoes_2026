"""Auditoria 8 — Validação preditiva espacialmente agrupada (fora da amostra).

Em cada UF (amostra de seções), os municípios são divididos em 5 grupos
(GroupKFold por município: nenhuma seção de um município de teste entra no
treino). Modelos: M0 (constância), M1 (margem municipal), M2 (preferência
latente). Métricas nas seções de teste, ponderadas pelos eleitores:
  - log-verossimilhança multinomial preditiva por eleitor;
  - erro absoluto e quadrático médios da participação de Lula nos aptos;
  - calibração: participação observada × prevista por decil da prevista;
  - cobertura do intervalo preditivo de 95% (variância de transição
    independente × φ do treino);
  - por região.
Separação entre duas capacidades: os mesmos modelos são avaliados em dados
sintéticos dos cenários A e B2_10 (auditoria_02), que têm esperanças
idênticas por seção e transições verdadeiras diferentes — a qualidade
preditiva não diz nada sobre qual é a verdadeira.

Saídas: resultados/auditoria/tabelas/08_*.csv
"""
from __future__ import annotations

import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd
from scipy import stats

from auditoria_02_sintetico import cenarios, gerar
from auditoria_05_covariaveis import preparar_z
from auditoria_comum import SUFIXO, TODAS_SECOES, TAB, jL, matrizes_RC, municipios_2026, salvar_json, todas_secoes_2026, variancia_transicao
from comum import REGIAO, SEMENTE
from ei import ajustar
from ei_cov import B_M1, B_M2, ajustar_M1, ajustar_M2

K = 5


def _folds(grupos, k, rng):
    ug = np.unique(grupos)
    perm = rng.permutation(len(ug))
    fold_de = {ug[i]: perm_i % k for perm_i, i in enumerate(perm)}
    return np.array([fold_de[g] for g in grupos])


def _avaliar_uf(args):
    uf, R, C, z, pi, grupos, regiao = args
    N = R.sum(1)
    X = R / N[:, None]
    rng = np.random.default_rng([SEMENTE, 8, hash(uf) % 10000])
    fold = _folds(grupos, K, rng)
    out = []
    pred = {m: np.full((len(X), 4), np.nan) for m in ("M0", "M1", "M2")}
    var = {m: np.full((len(X), 4), np.nan) for m in ("M0", "M1", "M2")}
    for f in range(K):
        tr, te = fold != f, fold == f
        if te.sum() == 0 or tr.sum() < 20:
            continue
        B0, _, _ = ajustar(X[tr], C[tr])
        P0tr = X[tr] @ B0
        phi0 = float((((C[tr] / N[tr, None] - P0tr) ** 2) / np.clip(variancia_transicao(X[tr], B0, N[tr]), 1e-12, None)).mean())
        pred["M0"][te] = X[te] @ B0
        var["M0"][te] = variancia_transicao(X[te], B0, N[te]) * max(phi0, 1.0)
        a1, b1, _, _ = ajustar_M1(X[tr], C[tr], z[tr], B0=B0)
        B1te = B_M1(a1, b1, z[te])
        pred["M1"][te] = np.einsum("ir,irc->ic", X[te], B1te)
        v = (X[te][:, :, None] * (B1te * (1 - B1te))).sum(1) / N[te, None]
        var["M1"][te] = v * max(phi0, 1.0)
        p2, _, _ = ajustar_M2(X[tr], C[tr], pi[tr], B0=B0)
        B2te = B_M2(p2, pi[te])
        pred["M2"][te] = np.einsum("ir,irc->ic", X[te], B2te)
        v = (X[te][:, :, None] * (B2te * (1 - B2te))).sum(1) / N[te, None]
        var["M2"][te] = v * max(phi0, 1.0)
    obs = C / N[:, None]
    for m in pred:
        P = np.clip(pred[m], 1e-12, None)
        ok = np.isfinite(P[:, 0])
        if ok.sum() < 10:
            continue
        ll = (C[ok] * np.log(P[ok])).sum() / N[ok].sum()
        e = obs[ok, jL] - P[ok, jL]
        w = N[ok] / N[ok].sum()
        sd = np.sqrt(var[m][ok, jL])
        cob = np.mean(np.abs(e) <= 1.96 * sd)
        dec = pd.qcut(P[ok, jL], 10, labels=False, duplicates="drop")
        cal = pd.DataFrame({"dec": dec, "obs": obs[ok, jL], "prev": P[ok, jL], "w": N[ok]}).groupby("dec").apply(
            lambda g: pd.Series({"obs": np.average(g.obs, weights=g.w), "prev": np.average(g.prev, weights=g.w)}), include_groups=False)
        out.append({"uf": uf, "regiao": regiao, "modelo": m, "secoes_teste": int(ok.sum()), "eleitores": float(N[ok].sum()),
                    "ll_pred_por_eleitor": ll, "mae_lula": float((w * np.abs(e)).sum()), "rmse_lula": float(np.sqrt((w * e ** 2).sum())),
                    "cobertura_95": float(cob), "calib_max_abs_dif_decil": float((cal.obs - cal.prev).abs().max()),
                    "calib_inclinacao": float(np.polyfit(cal.prev, cal.obs, 1)[0]) if len(cal) > 2 else np.nan})
    return out


def real(workers):
    sec = todas_secoes_2026()
    sec = sec[sec.uf != "ZZ"]
    mun = municipios_2026()
    sec, _ = preparar_z(sec, mun)
    if TODAS_SECOES:  # AUDITORIA_TODAS_SECOES=1: todas as seções com votação do 2T
        am = sec[sec.a_2.notna() & (sec.aptos_1 > 0) & (sec.instalada_2 != "Não")]
    else:
        am = sec[sec.na_amostra_bu.fillna(False).astype(bool)]
    tarefas = []
    for uf in sorted(am.uf.unique()):
        g = am[am.uf == uf]
        if len(g) < 20:
            g = am[am.uf.map(REGIAO) == REGIAO[uf]]
        R, C, N, ok = matrizes_RC(g)
        # grupos da partição: município; no DF (um só município) a zona eleitoral
        grupos = g.cd_mun if g.cd_mun.nunique() >= 5 else g.cd_mun.astype(str) + "-" + g.zona.astype(str)
        tarefas.append((uf, R, C, g.z.to_numpy()[ok], g.pi.to_numpy()[ok], grupos.to_numpy()[ok], REGIAO[uf]))
    with ProcessPoolExecutor(workers) as ex:
        res = [x for r in ex.map(_avaliar_uf, tarefas) for x in r]
    t = pd.DataFrame(res)
    t.to_csv(TAB / f"08_validacao_cruzada_por_uf{SUFIXO}.csv", index=False)
    agg = t.assign(w=t.eleitores).groupby(["modelo"]).apply(
        lambda g: pd.Series({c: np.average(g[c], weights=g.w) for c in ("ll_pred_por_eleitor", "mae_lula", "rmse_lula", "cobertura_95",
                                                                        "calib_max_abs_dif_decil", "calib_inclinacao")}), include_groups=False)
    agg_reg = t.assign(w=t.eleitores).groupby(["regiao", "modelo"]).apply(
        lambda g: pd.Series({c: np.average(g[c], weights=g.w) for c in ("ll_pred_por_eleitor", "mae_lula", "rmse_lula", "cobertura_95")}),
        include_groups=False)
    agg.to_csv(TAB / f"08_validacao_cruzada_nacional{SUFIXO}.csv")
    agg_reg.to_csv(TAB / f"08_validacao_cruzada_por_regiao{SUFIXO}.csv")
    return agg, agg_reg


def sintetico():
    """Cenários A e B2_10 com a mesma semente: esperanças idênticas, verdades distintas."""
    out = []
    cz = cenarios()
    for nome in ("A", "B2_10"):
        d = gerar(cz[nome], 10000, SEMENTE + 77)
        R, C, N = d["R"], d["Y"], d["N"]
        X = R / N[:, None]
        z = (X[:, 0] - X[:, 0].mean()) / X[:, 0].std()
        pi = np.where(X[:, 0] + X[:, 1] > 0, X[:, 0] / np.clip(X[:, 0] + X[:, 1], 1e-9, None), 0.5)
        for uf in np.unique(d["uf"]):
            m = d["uf"] == uf
            res = _avaliar_uf((f"{nome}-{uf}", R[m], C[m], z[m], pi[m], d["mun"][m], nome))
            for r in res:
                r.update({"cenario": nome, "verdade_FL": d["verdade"][1, 0]})
                out.append(r)
    t = pd.DataFrame(out)
    agg = t.assign(w=t.eleitores).groupby(["cenario", "modelo"]).apply(
        lambda g: pd.Series({**{c: np.average(g[c], weights=g.w) for c in ("ll_pred_por_eleitor", "mae_lula", "rmse_lula", "cobertura_95")},
                             "verdade_FL": g.verdade_FL.iloc[0]}), include_groups=False)
    agg.to_csv(TAB / f"08_validacao_cruzada_sintetica_A_vs_B2{SUFIXO}.csv")
    return agg


def main(workers=6):
    agg, agg_reg = real(workers)
    s = sintetico()
    salvar_json({"k_folds": K, "agrupamento": "município"}, TAB / f"08_resumo{SUFIXO}.json")
    with pd.option_context("display.width", 200, "display.float_format", "{:,.5f}".format):
        print(agg.to_string()); print(agg_reg.to_string()); print(s.to_string())


if __name__ == "__main__":
    main(workers=int(sys.argv[1]) if len(sys.argv) > 1 else 6)
