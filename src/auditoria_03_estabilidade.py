"""Auditoria 3 — Estabilidade numérica e inferencial do Modelo A; sensibilidade à agregação.

1. Inicializações. Para cada UF (amostra de seções), o EM é reiniciado de 20
   matrizes aleatórias (linhas ~ Dirichlet(1)); registram-se a dispersão da
   log-verossimilhança final e da taxa Flávio→Lula entre inícios. A
   verossimilhança é côncava em B, mas não estritamente; máximos locais
   distintos indicam não identificação.

2. Variância correta. O φ de Pearson de ei.py usa a variância multinomial
   p(1 − p)/N, que superestima a variância verdadeira quando as linhas de B
   são muito diferentes entre si (a variância correta, com transições
   individuais independentes, é Σ_r x_r B_rc (1 − B_rc)/N; ver
   auditoria_comum.variancia_transicao). Calcula-se φ com as duas variâncias.
   φ < 1 na escala multinomial não significa dados "regulares demais"; φ na
   escala correta é a sobredispersão real (heterogeneidade entre seções).

3. Bootstrap com 1.000 réplicas, por UF em paralelo: (a) por conglomerado de
   município (desenho da publicação, 200 réplicas lá); (b) por seção, ignorando
   os conglomerados, para medir o efeito do desenho. Intervalos percentílicos e
   básicos. Efeito de desenho = razão das variâncias (a)/(b) da taxa nacional.

4. Teste de teto com correção por conglomerado. O teste F da publicação usa φ
   de seção e trata as seções como independentes; seções do mesmo município
   são correlacionadas (pseudorreplicação), o que torna o p-valor pequeno
   demais. Correção aproximada: dividir o χ² somado pelo efeito de desenho do
   item 3. Alternativa exata sem restrições: teste de Wald unilateral da
   regressão de Goodman (01_goodman_wls_nacional.csv), com erro-padrão por
   conglomerado.

5. Agregação. Mesmo modelo e mesmo teste em: seção (amostra), zona (amostra
   agregada), município (amostra agregada) e município (todos, resultado
   oficial completo). Explica a divergência seção × município vista no
   relatório.

Saídas: resultados/auditoria/tabelas/03_*.csv
"""
from __future__ import annotations

import sys
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd
from scipy import stats

from auditoria_comum import (SUFIXO, DEST, ORIG, TAB, amostra_2026, iF, jL, matrizes_RC, municipios_2026, salvar_json,
                             todas_secoes_2026, totais_por_uf, variancia_transicao)
from comum import REGIAO, SEMENTE
from ei import ajustar, deviance, loglik, sobredispersao, teste_restricao

TETOS = [0.0, 0.01, 0.02, 0.05, 0.10]
N_BOOT = 1000
MIN_UNIDADES = 20


def _grupo_estimacao(df, uf):
    g = df[df.uf == uf]
    if len(g) < MIN_UNIDADES:
        g = df[df.uf.map(REGIAO) == REGIAO[uf]]
    return g


# --------------------------------------------------------------------------- 1. inicializações
def _multi_start(args):
    uf, R, C, n_inicios = args
    N = R.sum(1)
    X = R / N[:, None]
    rng = np.random.default_rng([SEMENTE, 3, hash(uf) % 10000])
    B_pad, ll_pad, _ = ajustar(X, C)
    lls, fls, its = [ll_pad], [B_pad[iF, jL]], []
    for _ in range(n_inicios):
        B0 = rng.dirichlet(np.ones(4), size=5)
        B, ll, res = ajustar(X, C, B0=B0)
        lls.append(ll); fls.append(B[iF, jL]); its.append(res.nit)
    return {"uf": uf, "secoes": len(R), "ll_padrao": ll_pad, "ll_max": max(lls), "ll_min": min(lls),
            "amplitude_ll": max(lls) - min(lls), "FL_padrao": fls[0], "FL_min": min(fls), "FL_max": max(fls),
            "amplitude_FL": max(fls) - min(fls), "iteracoes_media": float(np.mean(its))}


# --------------------------------------------------------------------------- 2. variância correta
def phis(am):
    out = []
    for uf in sorted(am.uf.unique()):
        g = _grupo_estimacao(am, uf)
        R, C, N, _ = matrizes_RC(g)
        X = R / N[:, None]
        B, _, _ = ajustar(X, C)
        P = X @ B
        v_mult = P * (1 - P) / N[:, None]
        v_prop = variancia_transicao(X, B, N)
        obs = C / N[:, None]
        e2 = (obs - P) ** 2
        gl = C.size - C.shape[0] - 15
        out.append({"uf": uf, "unidades": len(g), "phi_multinomial": float((e2 / np.clip(v_mult, 1e-12, None)).sum() / gl),
                    "phi_transicao_independente": float((e2 / np.clip(v_prop, 1e-12, None)).sum() / gl),
                    "razao_var_multinomial_sobre_correta_lula": float((v_mult[:, 0] / np.clip(v_prop[:, 0], 1e-12, None)).mean())})
    return pd.DataFrame(out)


# --------------------------------------------------------------------------- 3. bootstrap 1000
def _boot_uf(args):
    uf, R, C, grupos, tot, n_boot, por_secao = args
    N = R.sum(1)
    X = R / N[:, None]
    B, _, _ = ajustar(X, C)
    rng = np.random.default_rng([SEMENTE, 31 if por_secao else 30, hash(uf) % 10000])
    ug, inv = np.unique(grupos, return_inverse=True)
    idx_por_g = [np.flatnonzero(inv == g) for g in range(len(ug))]
    saida = np.empty((n_boot, 5, 4))
    for b in range(n_boot):
        if por_secao:
            idx = rng.integers(0, len(X), len(X))
        else:
            esc = rng.integers(0, len(ug), len(ug))
            idx = np.concatenate([idx_por_g[g] for g in esc])
        saida[b], _, _ = ajustar(X[idx], C[idx], B0=B)
    return uf, tot[:, None] * B, tot[None, :, None] * saida


def bootstrap(am, totais, workers, n_boot=N_BOOT):
    res = {}
    for por_secao in (False, True):
        tarefas = []
        for uf in sorted(am.uf.unique()):
            g = _grupo_estimacao(am, uf)
            R, C, N, ok = matrizes_RC(g)
            tarefas.append((uf, R, C, g.cd_mun.to_numpy()[ok], totais.loc[uf, ORIG].to_numpy(float), n_boot, por_secao))
        t0 = time.time()
        with ProcessPoolExecutor(workers) as ex:
            out = list(ex.map(_boot_uf, tarefas))
        print(f"  bootstrap por {'seção' if por_secao else 'município'}: {time.time() - t0:.0f}s", flush=True)
        fl = sum(o[1] for o in out)
        fb = sum(o[2] for o in out)
        tot = totais[ORIG].sum().to_numpy(float)
        res[por_secao] = (fl / tot[:, None], fb / tot[None, :, None])
    linhas = []
    for r, o in enumerate(ORIG):
        for c, d in enumerate(DEST):
            reg = {"origem": o, "destino": d, "taxa": res[False][0][r, c]}
            for por_secao, nome in ((False, "municipio"), (True, "secao")):
                v = res[por_secao][1][:, r, c]
                q = np.percentile(v, [2.5, 97.5])
                reg.update({f"ic95_percentil_inf_{nome}": q[0], f"ic95_percentil_sup_{nome}": q[1],
                            f"ic95_basico_inf_{nome}": max(0.0, 2 * reg["taxa"] - q[1]),
                            f"ic95_basico_sup_{nome}": 2 * reg["taxa"] - q[0],
                            f"ep_boot_{nome}": v.std(ddof=1)})
            reg["efeito_desenho"] = (reg["ep_boot_municipio"] / reg["ep_boot_secao"]) ** 2 if reg["ep_boot_secao"] > 0 else np.nan
            linhas.append(reg)
    return pd.DataFrame(linhas), res


# --------------------------------------------------------------------------- 4/5. teste de teto por nível
def testes_nivel(df, totais, nivel, grupo_cluster="cd_mun"):
    linhas = []
    fluxo = np.zeros((5, 4))
    for uf in sorted(df.uf.unique()):
        g = _grupo_estimacao(df, uf)
        if len(g) < 5:
            continue
        R, C, N, _ = matrizes_RC(g)
        X = R / N[:, None]
        B, _, _ = ajustar(X, C)
        phi, gl = sobredispersao(B, X, C)
        dev = deviance(B, X, C)
        fluxo += totais.loc[uf, ORIG].to_numpy(float)[:, None] * B
        for t in TETOS:
            if B[iF, jL] <= t:
                devc = dev
            else:
                Bc, _, _ = ajustar(X, C, B0=B, limites_celula={(iF, jL): (0.0, t)})
                devc = deviance(Bc, X, C)
                if devc < dev:
                    dev = devc
            F, p = teste_restricao(dev, devc, phi, 1, gl)
            linhas.append({"nivel": nivel, "uf": uf, "unidades": len(g), "teto": t, "taxa_FL_livre": B[iF, jL],
                           "aumento_dev": devc - dev, "phi": phi, "gl": gl, "F": F, "p": p})
    t = pd.DataFrame(linhas)
    taxa = fluxo / fluxo.sum(1, keepdims=True)
    conj = []
    for teto, g in t.groupby("teto"):
        k = int((g.aumento_dev > 1e-9).sum())
        chi = float((g.aumento_dev / g.phi).sum())
        conj.append({"nivel": nivel, "teto": teto, "unidades": int(g.unidades.sum()), "ufs_restricao_ativa": k, "chi2": chi,
                     "p_conjunto": float(stats.chi2.sf(chi, max(k, 1))) if k else 1.0,
                     "ufs_rejeitam_5pct": int((g.p < 0.05).sum()), "ufs_rejeitam_bonferroni": int((g.p < 0.05 / len(g)).sum()),
                     "taxa_FL_nacional": taxa[iF, jL], "taxa_BN_L": taxa[3, 0], "taxa_A_L": taxa[4, 0], "taxa_O_L": taxa[2, 0]})
    return pd.DataFrame(conj), t


def main(workers: int = 6, n_inicios: int = 20, n_boot: int = N_BOOT):
    am = amostra_2026()
    am = am[am.uf != "ZZ"]
    sec = todas_secoes_2026()
    sec = sec[sec.uf != "ZZ"]
    mun = municipios_2026()
    mun = mun[(mun.uf != "ZZ") & (mun.aptos_1 > 0)]
    totais = totais_por_uf(sec)
    resumo = {}

    print("1. inicializações", flush=True)
    tarefas = []
    for uf in sorted(am.uf.unique()):
        g = _grupo_estimacao(am, uf)
        R, C, N, _ = matrizes_RC(g)
        tarefas.append((uf, R, C, n_inicios))
    with ProcessPoolExecutor(workers) as ex:
        ms = pd.DataFrame(list(ex.map(_multi_start, tarefas)))
    ms.to_csv(TAB / f"03_multi_start_por_uf{SUFIXO}.csv", index=False)
    resumo["multi_start"] = {"amplitude_ll_max": float(ms.amplitude_ll.max()), "amplitude_FL_max": float(ms.amplitude_FL.max()),
                             "uf_amplitude_FL_max": ms.loc[ms.amplitude_FL.idxmax(), "uf"]}

    print("2. variância", flush=True)
    ph = phis(am)
    ph.to_csv(TAB / f"03_phi_duas_variancias{SUFIXO}.csv", index=False)
    resumo["phi"] = {"mediana_multinomial": float(ph.phi_multinomial.median()),
                     "mediana_transicao_independente": float(ph.phi_transicao_independente.median())}

    print("3. bootstrap", flush=True)
    bt, res = bootstrap(am, totais, workers, n_boot)
    bt.to_csv(TAB / f"03_bootstrap_1000{SUFIXO}.csv", index=False)
    np.save(TAB / f"03_bootstrap_1000_municipio_taxas{SUFIXO}.npy", res[False][1])
    fl = bt[(bt.origem == "b_1") & (bt.destino == "a_2")].iloc[0]
    resumo["bootstrap_FL"] = {k: float(fl[k]) for k in bt.columns if k not in ("origem", "destino")}

    print("4/5. testes por nível", flush=True)
    am_z = am.groupby(["uf", "cd_mun", "zona"], as_index=False).sum(numeric_only=True)
    am_m = am.groupby(["uf", "cd_mun"], as_index=False).sum(numeric_only=True)
    conj, det = [], []
    for nome, df in [("secao_amostra", am), ("zona_amostra_agregada", am_z), ("municipio_amostra_agregada", am_m),
                     ("municipio_todos", mun)]:
        c, d = testes_nivel(df, totais, nome)
        conj.append(c); det.append(d)
    conj = pd.concat(conj, ignore_index=True)
    deff = float(resumo["bootstrap_FL"]["efeito_desenho"])
    sec_rows = conj.nivel == "secao_amostra"
    conj.loc[sec_rows, "chi2_corrigido_efeito_desenho"] = conj.loc[sec_rows, "chi2"] / max(deff, 1.0)
    conj.loc[sec_rows, "p_conjunto_corrigido"] = [float(stats.chi2.sf(x, max(k, 1))) if k else 1.0
                                                  for x, k in zip(conj.loc[sec_rows, "chi2_corrigido_efeito_desenho"],
                                                                  conj.loc[sec_rows, "ufs_restricao_ativa"])]
    conj.to_csv(TAB / f"03_teste_teto_por_nivel{SUFIXO}.csv", index=False)
    pd.concat(det, ignore_index=True).to_csv(TAB / f"03_teste_teto_por_nivel_uf{SUFIXO}.csv", index=False)
    # teste de Wald unilateral com a regressão de Goodman (01)
    try:
        gw = pd.read_csv(TAB / f"01_goodman_wls_nacional{SUFIXO}.csv")
        gw = gw[(gw.origem == "b_1") & (gw.destino == "a_2")]
        wald = []
        for _, r in gw.iterrows():
            for t in TETOS:
                z = (r.coef_nacional - t) / r.ep_nacional
                wald.append({"nivel": r.nivel, "teto": t, "coef": r.coef_nacional, "ep": r.ep_nacional, "z": z,
                             "p_unilateral_coef_maior_que_teto": float(stats.norm.sf(z))})
        pd.DataFrame(wald).to_csv(TAB / f"03_teste_teto_wald_goodman{SUFIXO}.csv", index=False)
    except FileNotFoundError:
        pass
    salvar_json(resumo, TAB / f"03_resumo{SUFIXO}.json")
    with pd.option_context("display.width", 250, "display.max_columns", 40, "display.float_format", "{:,.5f}".format):
        print(ms.to_string()); print(ph.to_string()); print(bt.to_string()); print(conj.to_string())


if __name__ == "__main__":
    main(workers=int(sys.argv[1]) if len(sys.argv) > 1 else 6)
