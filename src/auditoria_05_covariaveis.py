"""Auditoria 5 — Taxas de transição dependentes do contexto (modelos M1 e M2 de ei_cov.py).

Pergunta: as taxas de conversão de brancos/nulos (≈ 61% para Lula) e de
abstencionistas (≈ 10%) e a migração Flávio→Lula (≈ 0,2%) mudam quando se
abandona a hipótese de constância dentro da UF e se permite que as taxas
dependam (M1) da margem municipal do 1º turno ou (M2) da preferência latente
local dos não votantes?

Para cada UF (amostra de seções): ajuste de M0 (constância, EM), M1 e M2;
deviance, φ (variância correta), AIC quase-verossimilhança; taxas nacionais
calculadas com TODAS as seções (as covariáveis existem para todas). Intervalos
por bootstrap de municípios (100 réplicas) para M1 e M2. Também se registra,
para M1, como a taxa Flávio→Lula e brancos/nulos→Lula variam ao longo da
margem (previsão nos quantis 10/50/90 da margem municipal).

Saídas: resultados/auditoria/tabelas/05_*.csv
"""
from __future__ import annotations

import sys
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

from auditoria_comum import SUFIXO, TODAS_SECOES, DEST, ORIG, TAB, amostra_2026, matrizes_RC, municipios_2026, salvar_json, todas_secoes_2026
from comum import INTERIM, REGIAO, SEMENTE
from ei import ajustar, deviance
from ei_cov import B_M1, B_M2, ajustar_M1, ajustar_M2, deviance_unidades, pi_latente

N_BOOT = 100
MIN_UNIDADES = 20
CHECK = INTERIM / "auditoria"
CHECK.mkdir(parents=True, exist_ok=True)


def preparar_z(sec, mun):
    m = mun[["uf", "cd_mun", "a_1", "b_1", "validos_1"]].copy()
    m["marg"] = (m.a_1 - m.b_1) / m.validos_1.where(m.validos_1 > 0)
    mu, sd = m.marg.mean(), m.marg.std()
    m["z"] = ((m.marg - mu) / sd).fillna(0.0)
    s = sec.merge(m[["uf", "cd_mun", "z"]], on=["uf", "cd_mun"], how="left")
    s["z"] = s.z.fillna(0.0)
    s["pi"] = pi_latente(s)
    return s, (mu, sd)


def _ajustar_uf(args):
    uf, R, C, z, pi, Rt, zt, pit, grupos, n_boot = args
    N = R.sum(1)
    X = R / N[:, None]
    t0 = time.time()
    B0, _, _ = ajustar(X, C)
    a1, b1, ll1, r1 = ajustar_M1(X, C, z, B0=B0)
    p2, ll2, r2 = ajustar_M2(X, C, pi, B0=B0)
    P0 = X @ B0
    P1 = np.einsum("ir,irc->ic", X, B_M1(a1, b1, z))
    P2 = np.einsum("ir,irc->ic", X, B_M2(p2, pi))
    out = {"uf": uf, "secoes": len(R), "dev_M0": deviance(B0, X, C), "dev_M1": deviance_unidades(P1, C),
           "dev_M2": deviance_unidades(P2, C), "ll_M0": float((C * np.log(np.clip(P0, 1e-12, None))).sum()),
           "ll_M1": ll1, "ll_M2": ll2, "conv_M1": bool(r1.success), "conv_M2": bool(r2.success),
           "beta_M1": b1, "tempo_s": time.time() - t0}
    # fluxos com todas as seções da UF
    fl0 = Rt.sum(0)[:, None] * B0
    fl1 = (Rt[:, :, None] * B_M1(a1, b1, zt)).sum(0)
    fl2 = (Rt[:, :, None] * B_M2(p2, pit)).sum(0)
    out.update({"fluxo_M0": fl0, "fluxo_M1": fl1, "fluxo_M2": fl2})
    # previsão de M1 nos quantis da margem
    qs = np.quantile(zt, [0.1, 0.5, 0.9])
    out["M1_quantis"] = B_M1(a1, b1, qs)
    # bootstrap por município; progresso gravado a cada 10 réplicas em interim/auditoria
    # (uma nova execução retoma de onde parou e reproduz os mesmos sorteios)
    rng = np.random.default_rng([SEMENTE, 5, _semente_uf(uf)])
    ug, inv = np.unique(grupos, return_inverse=True)
    idx_por_g = [np.flatnonzero(inv == g) for g in range(len(ug))]
    arq = CHECK / f"05_boot_{uf}{SUFIXO}.npz"
    b1s, b2s = [], []
    if n_boot and arq.exists():
        d = np.load(arq)
        b1s, b2s = list(d["M1"]), list(d["M2"])
        for _ in range(len(b1s)):
            rng.integers(0, len(ug), len(ug))
    for b in range(len(b1s), n_boot):
        esc = rng.integers(0, len(ug), len(ug))
        idx = np.concatenate([idx_por_g[g] for g in esc])
        a, bb, _, _ = ajustar_M1(X[idx], C[idx], z[idx], B0=B0, beta0=b1)
        b1s.append((Rt[:, :, None] * B_M1(a, bb, zt)).sum(0))
        p, _, _ = ajustar_M2(X[idx], C[idx], pi[idx], B0=B0)
        b2s.append((Rt[:, :, None] * B_M2(p, pit)).sum(0))
        if (b + 1) % 10 == 0 or b + 1 == n_boot:
            np.savez(arq, M1=np.array(b1s), M2=np.array(b2s))
            print(f"{uf}: {b + 1}/{n_boot} réplicas, {time.time() - t0:.0f}s", flush=True)
    out["boot_M1"] = np.array(b1s)
    out["boot_M2"] = np.array(b2s)
    return out


def _semente_uf(uf: str) -> int:
    """Inteiro determinístico por UF (hash() de str muda entre processos)."""
    return sum(ord(c) * 256 ** i for i, c in enumerate(uf))


def main(workers: int = 6, n_boot: int = N_BOOT):
    sec = todas_secoes_2026()
    sec = sec[sec.uf != "ZZ"]
    mun = municipios_2026()
    sec, (mu, sd) = preparar_z(sec, mun)
    if TODAS_SECOES:  # AUDITORIA_TODAS_SECOES=1: todas as seções com votação do 2T
        am = sec[sec.a_2.notna() & (sec.aptos_1 > 0) & (sec.instalada_2 != "Não")]
    else:
        am = sec[sec.na_amostra_bu.fillna(False).astype(bool)]
    tarefas = []
    for uf in sorted(am.uf.unique()):
        g = am[am.uf == uf]
        if len(g) < MIN_UNIDADES:
            g = am[am.uf.map(REGIAO) == REGIAO[uf]]
        R, C, N, ok = matrizes_RC(g)
        t = sec[sec.uf == uf]
        Rt, _, _, okt = matrizes_RC(t)
        tarefas.append((uf, R, C, g.z.to_numpy()[ok], g.pi.to_numpy()[ok], Rt, t.z.to_numpy()[okt], t.pi.to_numpy()[okt],
                        g.cd_mun.to_numpy()[ok], n_boot))
    tarefas.sort(key=lambda t: -len(t[1]))  # UFs maiores primeiro: SP e MG dominam o tempo
    t0 = time.time()
    with ProcessPoolExecutor(workers) as ex:
        res = list(ex.map(_ajustar_uf, tarefas))
    res.sort(key=lambda r: r["uf"])
    if n_boot:
        n_min = min(len(r["boot_M1"]) for r in res)
        if n_min < n_boot:
            print(f"aviso: só {n_min} réplicas completas em todas as UFs; os intervalos usam as {n_min} primeiras", flush=True)
            for r in res:
                r["boot_M1"], r["boot_M2"] = r["boot_M1"][:n_min], r["boot_M2"][:n_min]
            n_boot = n_min
    print(f"ajustes: {time.time() - t0:.0f}s", flush=True)
    ajuste = pd.DataFrame([{k: v for k, v in r.items() if not isinstance(v, np.ndarray)} for r in res])
    ajuste["dev_M1_menos_M0"] = ajuste.dev_M1 - ajuste.dev_M0
    ajuste["dev_M2_menos_M0"] = ajuste.dev_M2 - ajuste.dev_M0
    ajuste.to_csv(TAB / f"05_ajuste_por_uf{SUFIXO}.csv", index=False)
    fl = {m: sum(r[f"fluxo_{m}"] for r in res) for m in ("M0", "M1", "M2")}
    boot = {m: sum(r[f"boot_{m}"] for r in res) for m in ("M1", "M2")} if n_boot else {}
    sufixo = "" if n_boot else "_sem_bootstrap"
    linhas = []
    for m in ("M0", "M1", "M2"):
        taxa = fl[m] / fl[m].sum(1, keepdims=True)
        for r, o in enumerate(ORIG):
            for c, d in enumerate(DEST):
                reg = {"modelo": m, "origem": o, "destino": d, "taxa": taxa[r, c], "votos": fl[m][r, c]}
                if m in boot:
                    tb = boot[m] / boot[m].sum(2, keepdims=True)
                    reg.update({"ic95_inf": np.percentile(tb[:, r, c], 2.5), "ic95_sup": np.percentile(tb[:, r, c], 97.5)})
                linhas.append(reg)
    nac = pd.DataFrame(linhas)
    nac.to_csv(TAB / f"05_taxas_nacionais_por_modelo{sufixo}{SUFIXO}.csv", index=False)
    # M1: taxas nos quantis da margem, nacional (média ponderada pelos totais de origem da UF)
    qrows = []
    for r in res:
        tot = r["fluxo_M0"].sum(1)
        for q, nome in enumerate(("margem_q10", "margem_q50", "margem_q90")):
            for i, o in enumerate(ORIG):
                for j, d in enumerate(DEST):
                    qrows.append({"uf": r["uf"], "quantil": nome, "origem": o, "destino": d, "taxa": r["M1_quantis"][q, i, j], "peso": tot[i]})
    qd = pd.DataFrame(qrows)
    qn = qd.assign(w=qd.taxa * qd.peso).groupby(["quantil", "origem", "destino"]).apply(
        lambda g: g.w.sum() / g.peso.sum(), include_groups=False).rename("taxa").reset_index()
    qn.to_csv(TAB / f"05_M1_taxas_por_quantil_margem{SUFIXO}.csv", index=False)
    resumo = {"modelos": {"M0": "constância (EM)", "M1": "softmax(α + β·margem municipal padronizada)",
                          "M2": "preferência latente π_i = Lula1/(Lula1+Flávio1) nas linhas brancos/nulos e abstenção"},
              "dev_total": {m: float(ajuste[f"dev_{m}"].sum()) for m in ("M0", "M1", "M2")},
              "parametros_por_uf": {"M0": 15, "M1": 30, "M2": 15}, "n_boot": n_boot,
              "margem_media": float(mu), "margem_dp": float(sd), "tempo_s": time.time() - t0}
    salvar_json(resumo, TAB / f"05_resumo{SUFIXO}.json")
    with pd.option_context("display.width", 250, "display.max_columns", 30, "display.float_format", "{:,.5f}".format):
        print(ajuste[["uf", "secoes", "dev_M0", "dev_M1", "dev_M2", "conv_M1", "conv_M2"]].to_string())
        print(nac.pivot(index=["origem", "destino"], columns="modelo", values="taxa").to_string())
        print(nac[nac.modelo != "M0"].to_string())
        print(qn.pivot(index=["origem", "destino"], columns="quantil", values="taxa").to_string())


if __name__ == "__main__":
    # uso: python auditoria_05_covariaveis.py [processos] [n_boot]   (n_boot=0: só estimativas pontuais)
    main(workers=int(sys.argv[1]) if len(sys.argv) > 1 else 6,
         n_boot=int(sys.argv[2]) if len(sys.argv) > 2 else N_BOOT)
