"""Auditoria 2 — Experimentos adversariais com eleições sintéticas de dois turnos.

Gerador: eleitorado em n_uf "estados", municípios dentro dos estados e seções
dentro dos municípios. Cada seção i tem uma ideologia latente θ_i (efeito do
estado + município + seção, o que produz comportamentos correlacionados
dentro das unidades), que determina a composição do 1º turno x_i e, nos
cenários em que se pede, as taxas de transição B_i. As transições são
individuais: cada eleitor de origem r muda para o destino c com probabilidade
B_i[r, c], sorteio multinomial por linha. A matriz de fluxos verdadeira M_i é
guardada, de modo que as taxas nacionais verdadeiras são conhecidas.

Controles do gerador (classe Cenario): matriz-base; heterogeneidade por
estado e por município (escala logit, por célula); dependência das taxas na
ideologia latente (β, escala logit por célula; γ para termo quadrático);
migração adicional Flávio→Lula com compensação exata por seção (cenário B2);
sobredispersão (linhas de B_i sorteadas de uma Dirichlet); tamanho das seções.

Cenários:
  A      fidelidade elevada; matriz ≈ estimada pelo Modelo A; heterogeneidade pequena.
  B1_δ   migração Flávio→Lula = δ (5, 10, 15%) com compensação CONSTANTE: os
         demais grupos dão menos votos a Lula e mais a Flávio, de modo que os
         totais nacionais são os mesmos de A. A matriz continua constante
         dentro de cada estado.
  B2_δ   migração δ com compensação EXATA POR SEÇÃO: B_i = B_A + Δ_i com
         x_i·Δ_i = 0. A esperança de cada seção é idêntica à do cenário A; os
         dados são observacionalmente equivalentes a A por construção.
  C      abstenção diferencial sem migração: a abstenção de eleitores de cada
         finalista e a mobilização dos abstencionistas dependem de θ_i.
  D      forte heterogeneidade regional (estado e município), média ≈ A.
  E      mistura: migração 3% (compensação constante) + dependência em θ +
         heterogeneidade municipal.
  F      má especificação: taxas dependem de θ e de θ² em várias células,
         linhas sorteadas de Dirichlet (sobredispersão) e composição fortemente
         ligada a θ; não existe matriz constante em nenhum estrato.
  Hσ     sensibilidade à heterogeneidade: cenário A com σ_mun crescente, com
         migração verdadeira 0 e 5%.

Modelo avaliado: Modelo A (ei.ajustar por estado; taxas nacionais pelos
totais; bootstrap por município para IC 95%; testes de teto 0/1/2/5/10% com o
teste F de quase-verossimilhança e o χ² somado, como em analise_03). O modelo
não recebe nenhuma informação sobre as transições verdadeiras.

Métricas por célula: viés, RMSE, MAE, cobertura do IC 95%, frequência de
estimativas no limite (taxa < 0,01%), e para os testes de teto: taxa de
falsos positivos (rejeita o teto c quando a taxa verdadeira ≤ c) e de falsos
negativos (não rejeita quando a verdadeira > c). Incerteza Monte Carlo:
erro-padrão entre repetições.

Saídas: resultados/auditoria/tabelas/02_sintetico_*.csv
"""
from __future__ import annotations

import sys
import time
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from scipy import stats

from auditoria_comum import DEST, ORIG, TAB, iA, iBN, iF, iL, iO, jA, jBN, jF, jL, salvar_json
from comum import SEMENTE
from ei import ajustar, bootstrap_conglomerados, deviance, sobredispersao, teste_restricao

B_A = np.array([[.985, .002, .003, .010],
                [.002, .984, .005, .009],
                [.42, .39, .13, .06],
                [.60, .02, .37, .01],
                [.10, .03, .01, .86]])
B_A = B_A / B_A.sum(1, keepdims=True)
TETOS = [0.0, 0.01, 0.02, 0.05, 0.10]


def logistic(z):
    return 1 / (1 + np.exp(-z))


def logit(p):
    return np.log(p / (1 - p))


def softmax_rows(eta):
    e = np.exp(eta - eta.max(-1, keepdims=True))
    return e / e.sum(-1, keepdims=True)


def compensacao_constante(B, delta, comp):
    """Flávio→Lula = B[F,L] + δ; Flávio→Flávio cai δ; linhas O, BN, A dão menos a Lula e mais a
    Flávio, proporcionalmente, de modo que os totais nacionais de Lula e Flávio não mudam.
    comp = composição nacional do 1T (5 proporções)."""
    B = B.copy()
    B[iF, jL] += delta
    B[iF, jF] -= delta
    S = sum(comp[r] * B[r, jL] for r in (iO, iBN, iA))
    rho = delta * comp[iF] / S
    assert rho < 1, "compensação impossível"
    for r in (iO, iBN, iA):
        mv = rho * B[r, jL]
        B[r, jL] -= mv
        B[r, jF] += mv
    return B


@dataclass
class Cenario:
    nome: str
    B: np.ndarray = field(default_factory=lambda: B_A.copy())
    sigma_uf: float = 0.15
    sigma_mun: float = 0.15
    beta: np.ndarray = field(default_factory=lambda: np.zeros((5, 4)))
    gamma: np.ndarray = field(default_factory=lambda: np.zeros((5, 4)))
    delta_exata: float = 0.0          # B2: migração extra com compensação exata por seção
    conc_dirichlet: float | None = None  # sobredispersão das linhas
    theta_comp: float = 1.0           # força da ligação entre θ e a composição do 1T
    descricao: str = ""


def cenarios() -> dict[str, Cenario]:
    comp = np.array([.339, .353, .059, .038, .211])
    c = {}
    c["A"] = Cenario("A", descricao="fidelidade elevada, matriz constante (≈ estimada), heterogeneidade pequena")
    for d in (0.05, 0.10, 0.15):
        c[f"B1_{int(d*100)}"] = Cenario(f"B1_{int(d*100)}", B=compensacao_constante(B_A, d, comp),
                                       descricao=f"migração F→L {d:.0%} com compensação constante (mesmos totais nacionais de A)")
        c[f"B2_{int(d*100)}"] = Cenario(f"B2_{int(d*100)}", delta_exata=d,
                                       descricao=f"migração F→L {d:.0%} com compensação exata por seção (equivalente a A)")
    beta_c = np.zeros((5, 4))
    beta_c[iL, jA], beta_c[iF, jA] = -1.0, 1.0     # Lula abstém mais onde Flávio é forte (θ<0) e vice-versa
    beta_c[iA, jL], beta_c[iA, jF] = 1.0, -1.0     # abstencionista do 1T vota em Lula mais onde Lula é forte
    beta_c[iBN, jL], beta_c[iBN, jF] = 0.8, -0.8
    c["C"] = Cenario("C", beta=beta_c, descricao="abstenção diferencial e mobilização dependentes da preferência local; migração 0")
    c["D"] = Cenario("D", sigma_uf=0.8, sigma_mun=0.5, descricao="forte heterogeneidade por estado e município; média ≈ A")
    c["E"] = Cenario("E", B=compensacao_constante(B_A, 0.03, comp), beta=0.6 * beta_c, sigma_mun=0.3,
                     descricao="mistura: migração 3% (compensação constante) + dependência em θ + heterogeneidade")
    beta_f = 0.7 * beta_c
    beta_f[iO, jL], beta_f[iO, jF] = 1.2, -1.2
    gamma_f = np.zeros((5, 4))
    gamma_f[iA, jL], gamma_f[iBN, jL], gamma_f[iF, jL], gamma_f[iL, jF] = 0.5, 0.5, 0.4, 0.4
    c["F"] = Cenario("F", beta=beta_f, gamma=gamma_f, conc_dirichlet=40.0, sigma_mun=0.3, theta_comp=1.5,
                     descricao="má especificação: taxas em θ e θ², linhas sorteadas (sobredispersão), sem matriz constante")
    for s in (0.0, 0.3, 0.6, 1.0):
        c[f"H0_sig{s}"] = Cenario(f"H0_sig{s}", sigma_uf=0.0, sigma_mun=s, descricao=f"A com σ_mun={s}, migração 0,2%")
        c[f"H5_sig{s}"] = Cenario(f"H5_sig{s}", B=compensacao_constante(B_A, 0.05, comp), sigma_uf=0.0, sigma_mun=s,
                                  descricao=f"migração 5% (compensação constante) com σ_mun={s}")
    return c


def gerar(cen: Cenario, n_sec: int, seed: int, n_uf: int = 5, sec_por_mun: int = 8):
    rng = np.random.default_rng(seed)
    n_mun = max(n_uf, n_sec // sec_por_mun)
    mun_uf = rng.integers(0, n_uf, n_mun)
    sec_mun = rng.integers(0, n_mun, n_sec)
    sec_uf = mun_uf[sec_mun]
    th_uf = rng.normal(0, 0.5, n_uf)
    th_mun = th_uf[mun_uf] + rng.normal(0, 0.6, n_mun)
    th = th_mun[sec_mun] + rng.normal(0, 0.3, n_sec)
    N = rng.integers(150, 451, n_sec)
    # composição do 1T
    pL = logistic(cen.theta_comp * th)
    abst = logistic(logit(0.21) + 0.15 * th + rng.normal(0, 0.25, n_sec))
    bn = logistic(logit(0.038) + rng.normal(0, 0.3, n_sec)) * (1 - abst)
    o = logistic(logit(0.059) + rng.normal(0, 0.3, n_sec)) * (1 - abst - bn)
    v = 1 - abst - bn - o
    comp = np.column_stack([pL * v, (1 - pL) * v, o, bn, abst])
    R = np.array([rng.multinomial(N[i], comp[i]) for i in range(n_sec)], float)
    # taxas por seção
    eta0 = np.log(np.clip(cen.B, 1e-9, None))
    u_uf = rng.normal(0, cen.sigma_uf, (n_uf, 5, 4)) if cen.sigma_uf > 0 else np.zeros((n_uf, 5, 4))
    u_mun = rng.normal(0, cen.sigma_mun, (n_mun, 5, 4)) if cen.sigma_mun > 0 else np.zeros((n_mun, 5, 4))
    eta = eta0[None] + u_uf[sec_uf] + u_mun[sec_mun] + cen.beta[None] * th[:, None, None] + cen.gamma[None] * (th ** 2)[:, None, None]
    Bi = softmax_rows(eta)
    delta_real = np.zeros(n_sec)
    if cen.delta_exata > 0:
        X = R / N[:, None]
        S = (X[:, [iO, iBN, iA]] * Bi[:, [iO, iBN, iA], jL]).sum(1)
        with np.errstate(divide="ignore", invalid="ignore"):
            dmax = np.where(X[:, iF] > 0, S / X[:, iF], np.inf)
        d = np.minimum(cen.delta_exata, 0.999 * np.minimum(dmax, Bi[:, iF, jF]))
        d = np.clip(d, 0, None)
        for i in range(n_sec):
            if d[i] <= 0:
                continue
            Bi[i, iF, jL] += d[i]
            Bi[i, iF, jF] -= d[i]
            for r in (iO, iBN, iA):
                mv = d[i] * X[i, iF] * Bi[i, r, jL] / S[i] if S[i] > 0 else 0.0
                Bi[i, r, jL] -= mv
                Bi[i, r, jF] += mv
        delta_real = d
    if cen.conc_dirichlet:
        for r in range(5):
            Bi[:, r, :] = np.array([rng.dirichlet(np.clip(Bi[i, r] * cen.conc_dirichlet, 1e-3, None)) for i in range(n_sec)])
    # transições individuais
    M = np.zeros((n_sec, 5, 4))
    for i in range(n_sec):
        for r in range(5):
            if R[i, r] > 0:
                M[i, r] = rng.multinomial(int(R[i, r]), Bi[i, r])
    Y = M.sum(1)
    tot = R.sum(0)
    verdade = M.sum(0) / tot[:, None]
    return {"R": R, "Y": Y, "N": N.astype(float), "uf": sec_uf, "mun": sec_mun, "M": M, "Bi": Bi,
            "verdade": verdade, "esperada": (R[:, :, None] * Bi).sum(0) / tot[:, None], "delta_real_media": float((R[:, iF] * delta_real).sum() / tot[iF])}


def modelo_A(dados, rng, n_boot=40):
    R, Y, N, uf, mun = dados["R"], dados["Y"], dados["N"], dados["uf"], dados["mun"]
    X = R / N[:, None]
    tot_nac = R.sum(0)
    fluxo = np.zeros((5, 4))
    boots = []
    testes = []
    dev_tot = 0.0
    phis = []
    for s in np.unique(uf):
        m = uf == s
        B, ll, res = ajustar(X[m], Y[m])
        tot = R[m].sum(0)
        fluxo += tot[:, None] * B
        phi, gl = sobredispersao(B, X[m], Y[m])
        dev = deviance(B, X[m], Y[m])
        dev_tot += dev
        phis.append(phi)
        bs = bootstrap_conglomerados(X[m], Y[m], mun[m], B, n_boot, rng)
        boots.append(tot[None, :, None] * bs)
        for t in TETOS:
            if B[iF, jL] <= t:
                devc = dev
            else:
                Bc, _, _ = ajustar(X[m], Y[m], B0=B, limites_celula={(iF, jL): (0.0, t)})
                devc = deviance(Bc, X[m], Y[m])
                if devc < dev:
                    dev = devc
            F, p = teste_restricao(dev, devc, phi, 1, gl)
            testes.append({"uf": s, "teto": t, "aumento_dev": devc - dev, "phi": phi, "p": p})
    taxa = fluxo / tot_nac[:, None]
    sb = np.sum(boots, axis=0) / tot_nac[None, :, None]
    ic = np.percentile(sb, [2.5, 97.5], axis=0)
    tt = pd.DataFrame(testes)
    conj = {}
    for t, g in tt.groupby("teto"):
        k = int((g.aumento_dev > 1e-9).sum())
        chi = float((g.aumento_dev / g.phi).sum())
        conj[t] = float(stats.chi2.sf(chi, max(k, 1))) if k else 1.0
    return taxa, ic, conj, dev_tot / N.sum(), float(np.median(phis))


def rodar(args):
    nome, n_sec, seed, n_boot = args
    cen = cenarios()[nome]
    t0 = time.time()
    d = gerar(cen, n_sec, seed)
    rng = np.random.default_rng(seed + 7)
    taxa, ic, conj, dev, phi = modelo_A(d, rng, n_boot)
    linhas = []
    for r in range(5):
        for c in range(4):
            linhas.append({"cenario": nome, "n_sec": n_sec, "seed": seed, "origem": ORIG[r], "destino": DEST[c],
                           "verdade": d["verdade"][r, c], "esperada": d["esperada"][r, c], "estimada": taxa[r, c],
                           "ic_inf": ic[0, r, c], "ic_sup": ic[1, r, c],
                           "cobre": bool(ic[0, r, c] <= d["verdade"][r, c] <= ic[1, r, c]),
                           "no_limite": bool(taxa[r, c] < 1e-4), "dev_por_eleitor": dev, "phi_mediano": phi,
                           "delta_real_B2": d["delta_real_media"], "tempo_s": time.time() - t0})
    testes = [{"cenario": nome, "n_sec": n_sec, "seed": seed, "teto": t, "p_conjunto": p, "rejeita": p < 0.05,
               "verdade_FL": d["verdade"][iF, jL], "verdade_acima_teto": d["verdade"][iF, jL] > t + 1e-9}
              for t, p in conj.items()]
    return linhas, testes


def resumir(cel: pd.DataFrame, tst: pd.DataFrame):
    out = []
    for (cen, n, o, dd), g in cel.groupby(["cenario", "n_sec", "origem", "destino"]):
        e = g.estimada - g.verdade
        k = len(g)
        out.append({"cenario": cen, "n_sec": n, "origem": o, "destino": dd, "repeticoes": k,
                    "verdade_media": g.verdade.mean(), "estimada_media": g.estimada.mean(),
                    "vies": e.mean(), "vies_ep_mc": e.std(ddof=1) / np.sqrt(k) if k > 1 else np.nan,
                    "rmse": np.sqrt((e ** 2).mean()), "mae": e.abs().mean(),
                    "cobertura_ic95": g.cobre.mean(), "cobertura_ep_mc": np.sqrt(g.cobre.mean() * (1 - g.cobre.mean()) / k),
                    "frac_no_limite": g.no_limite.mean(), "largura_ic_media": (g.ic_sup - g.ic_inf).mean(),
                    "dev_por_eleitor_media": g.dev_por_eleitor.mean(), "phi_mediano_medio": g.phi_mediano.mean()})
    res_cel = pd.DataFrame(out)
    out = []
    for (cen, n, t), g in tst.groupby(["cenario", "n_sec", "teto"]):
        acima = g[g.verdade_acima_teto]
        abaixo = g[~g.verdade_acima_teto]
        out.append({"cenario": cen, "n_sec": n, "teto": t, "repeticoes": len(g), "verdade_FL_media": g.verdade_FL.mean(),
                    "frac_rejeita": g.rejeita.mean(),
                    "falso_positivo": abaixo.rejeita.mean() if len(abaixo) else np.nan, "n_verdade_abaixo": len(abaixo),
                    "falso_negativo": (~acima.rejeita).mean() if len(acima) else np.nan, "n_verdade_acima": len(acima)})
    return res_cel, pd.DataFrame(out)


def main(workers: int = 8, seeds_2k: int = 20, seeds_10k: int = 12, seeds_50k: int = 4, n_boot: int = 40):
    cens = cenarios()
    tarefas = []
    for nome in cens:
        for s in range(seeds_2k):
            tarefas.append((nome, 2000, SEMENTE + 1000 + s, n_boot))
        for s in range(seeds_10k):
            tarefas.append((nome, 10000, SEMENTE + 2000 + s, n_boot))
    for nome in ("A", "B1_10", "B2_10", "C", "F"):
        for s in range(seeds_50k):
            tarefas.append((nome, 50000, SEMENTE + 3000 + s, 20))
    # retomada: execuções já gravadas (cenário, n_sec, seed) não são refeitas
    arq_cel, arq_tst = TAB / "02_sintetico_execucoes_celulas.csv", TAB / "02_sintetico_execucoes_testes.csv"
    feitas = set()
    if arq_cel.exists() and arq_tst.exists():
        prev = pd.read_csv(arq_cel)
        feitas = set(zip(prev.cenario, prev.n_sec, prev.seed))
        tarefas = [t for t in tarefas if (t[0], t[1], t[2]) not in feitas]
    print(len(tarefas), "execuções a fazer;", len(feitas), "já gravadas", flush=True)
    t0 = time.time()
    with ProcessPoolExecutor(workers) as ex:
        for k, (a, b) in enumerate(ex.map(rodar, tarefas, chunksize=1), 1):
            pd.DataFrame(a).to_csv(arq_cel, mode="a", header=not arq_cel.exists(), index=False)
            pd.DataFrame(b).to_csv(arq_tst, mode="a", header=not arq_tst.exists(), index=False)
            if k % 25 == 0:
                print(f"{k}/{len(tarefas)} {time.time() - t0:.0f}s", flush=True)
    cel = pd.read_csv(arq_cel)
    tst = pd.read_csv(arq_tst)
    res_cel, res_tst = resumir(cel, tst)
    res_cel.to_csv(TAB / "02_sintetico_resumo_celulas.csv", index=False)
    res_tst.to_csv(TAB / "02_sintetico_resumo_testes.csv", index=False)
    salvar_json({"cenarios": {k: {"descricao": v.descricao, "B": v.B.round(4).tolist(), "sigma_uf": v.sigma_uf,
                                  "sigma_mun": v.sigma_mun, "delta_exata": v.delta_exata,
                                  "beta": v.beta.round(3).tolist(), "gamma": v.gamma.round(3).tolist(),
                                  "conc_dirichlet": v.conc_dirichlet} for k, v in cens.items()},
                 "B_A": B_A.round(4).tolist(), "tetos": TETOS, "n_boot": n_boot, "semente": SEMENTE,
                 "tempo_s": time.time() - t0}, TAB / "02_sintetico_parametros.json")
    chave = res_cel[(res_cel.origem == "b_1") & (res_cel.destino == "a_2")]
    with pd.option_context("display.width", 250, "display.max_columns", 30, "display.float_format", "{:,.4f}".format):
        print(chave[["cenario", "n_sec", "repeticoes", "verdade_media", "estimada_media", "vies", "rmse", "cobertura_ic95",
                     "frac_no_limite", "phi_mediano_medio"]].to_string())
        print(res_tst.to_string())


if __name__ == "__main__":
    w = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    main(workers=w)
