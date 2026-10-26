"""Etapa 4 — Modelo B: inferência ecológica bayesiana hierárquica (PyMC).

Unidades: seções da amostra de BUs do 2º turno (2026). Origens (1T): Lula,
Flávio, outros, brancos/nulos, abstenção. Destinos (2T): Lula, Flávio,
brancos/nulos, abstenção.

Estrutura (para a seção i, na UF s, no município m):
  η[i, r, c] = μ[r, c] + τ[r, c]·z[s, r, c] + γ[r, c]·urb[m] + δ[r, c]·marg[m]
  β[i, r, ·] = softmax(η[i, r, ·])   (destino "abstenção 2T" é a referência, η = 0)
  p[i]       = Σ_r x[i, r]·β[i, r, ·]           x = composição do 1T sobre aptos
  y[i]       ~ DirichletMultinomial(N[i], κ·p[i])

  urb  = % da população urbana do município (Censo 2022), padronizado
  marg = margem Lula − Flávio no 1º turno no município, padronizada
  z ~ Normal(0, 1) (parametrização não centrada); κ = concentração (sobredispersão)

Três conjuntos de priors (sensibilidade, seção 6 do prompt):
  "neutra"            μ ~ N(0, 1,5); nenhuma preferência por fidelidade
  "fidelidade_alta"   μ centrado em taxas de fidelidade de ~90% para Lula→Lula
                      e Flávio→Flávio e ~2% nas trocas diretas (DP 0,5)
  "troca_alta"        μ centrado em ~15% de troca Flávio→Lula e Lula→Flávio (DP 0,5)
Se a posterior da taxa Flávio→Lula mudar muito entre priors, os dados não a
identificam bem; se convergir, os dados dominam.

Fluxos nacionais: para cada sorteio da posterior, β é calculado para cada
município (covariáveis do município, efeito da UF) e multiplicado pelos totais
de origem do município (todas as seções). Verificação preditiva posterior:
simula-se y para as seções da amostra e compara-se com o observado.
"""
from __future__ import annotations

import json
import sys
import time

import arviz as az
import numpy as np
import pandas as pd
import pymc as pm
import pytensor.tensor as pt

from comum import DERIVADOS, INTERIM, SEMENTE, TABELAS, salvar_json

ORIG = ["a_1", "b_1", "o_1", "bn_1", "abst_1"]
DEST = ["a_2", "b_2", "bn_2", "abst_2"]
NR, NC = len(ORIG), len(DEST)


def logit_ref(probs):
    p = np.asarray(probs, float)
    return np.log(p[:-1] / p[-1])


# Médias a priori de μ (logitos em relação ao destino "abstenção 2T").
PRIORS = {
    "neutra": {"centro": np.zeros((NR, NC - 1)), "dp": 1.5},
    "fidelidade_alta": {"centro": np.array([
        logit_ref([0.90, 0.02, 0.02, 0.06]),   # Lula 1T
        logit_ref([0.02, 0.90, 0.02, 0.06]),   # Flávio 1T
        logit_ref([0.40, 0.40, 0.10, 0.10]),   # outros 1T
        logit_ref([0.20, 0.20, 0.40, 0.20]),   # brancos/nulos 1T
        logit_ref([0.05, 0.05, 0.02, 0.88]),   # abstenção 1T
    ]), "dp": 0.5},
    "troca_alta": {"centro": np.array([
        logit_ref([0.77, 0.15, 0.02, 0.06]),
        logit_ref([0.15, 0.77, 0.02, 0.06]),
        logit_ref([0.40, 0.40, 0.10, 0.10]),
        logit_ref([0.20, 0.20, 0.40, 0.20]),
        logit_ref([0.05, 0.05, 0.02, 0.88]),
    ]), "dp": 0.5},
}


def dados(n_max: int | None = None):
    sec = pd.read_parquet(INTERIM / "secoes_2026.parquet")
    mun = pd.read_parquet(INTERIM / "municipios_2026.parquet")
    ibge = pd.read_csv(DERIVADOS / "ibge_municipios.csv", dtype={"cd_ibge": str})
    mun = mun.merge(ibge[["cd_ibge", "pct_urbana"]], on="cd_ibge", how="left")
    mun["pct_urbana"] = mun.pct_urbana.fillna(100.0)  # exterior e município novo: urbano
    mun["marg"] = (mun.a_1 - mun.b_1) / mun.validos_1
    mu_u, sd_u = mun.pct_urbana.mean(), mun.pct_urbana.std()
    mu_m, sd_m = mun.marg.mean(), mun.marg.std()
    # 41 cidades do exterior sem votos válidos no 1T: margem indefinida → valor médio (z = 0)
    mun["marg"] = mun.marg.fillna(mu_m)
    mun["urb_z"] = (mun.pct_urbana - mu_u) / sd_u
    mun["marg_z"] = (mun.marg - mu_m) / sd_m
    am = sec[sec.na_amostra_bu.fillna(False).astype(bool)].merge(
        mun[["uf", "cd_mun", "urb_z", "marg_z"]], on=["uf", "cd_mun"], how="left")
    if n_max and len(am) > n_max:
        am = am.sample(n_max, random_state=SEMENTE)
    ufs = sorted(mun.uf.unique())
    return am, mun, ufs


def matrizes(df):
    R = df[ORIG].to_numpy(float, copy=True)
    C = df[DEST].to_numpy(float, copy=True)
    d = C.sum(1) - R.sum(1)
    R[:, -1] += np.clip(d, 0, None)
    C[:, -1] += np.clip(-d, 0, None)
    return R, C


def modelo(am, ufs, prior):
    R, Y = matrizes(am)
    N = Y.sum(1).astype("int64")
    X = R / R.sum(1, keepdims=True)
    s_idx = am.uf.map({u: k for k, u in enumerate(ufs)}).to_numpy()
    coords = {"uf": ufs, "origem": ORIG, "destino_livre": DEST[:-1], "unidade": np.arange(len(am)),
              "destino": DEST}
    with pm.Model(coords=coords) as m:
        mu = pm.Normal("mu", prior["centro"], prior["dp"], dims=("origem", "destino_livre"))
        tau = pm.HalfNormal("tau", 0.5, dims=("origem", "destino_livre"))
        z = pm.Normal("z", 0, 1, dims=("uf", "origem", "destino_livre"))
        gam = pm.Normal("gamma_urb", 0, 0.5, dims=("origem", "destino_livre"))
        dlt = pm.Normal("delta_marg", 0, 0.5, dims=("origem", "destino_livre"))
        kappa = pm.LogNormal("kappa", np.log(200), 1.0)
        urb = pm.Data("urb", am.urb_z.to_numpy(float))
        mrg = pm.Data("marg", am.marg_z.to_numpy(float))
        eta_s = mu[None] + tau[None] * z                                  # uf × R × (C−1)
        eta = (eta_s[s_idx] + gam[None] * urb[:, None, None] + dlt[None] * mrg[:, None, None])
        eta = pt.concatenate([eta, pt.zeros((eta.shape[0], NR, 1))], axis=2)
        beta = pt.special.softmax(eta, axis=2)                            # i × R × C
        p = pt.sum(pt.as_tensor(X)[:, :, None] * beta, axis=1)
        pm.DirichletMultinomial("y", n=N, a=kappa * p, observed=Y.astype("int64"), dims=("unidade", "destino"))
    return m


def fluxos_nacionais(idata, mun, ufs, n_sorteios=400, rng=None):
    """Fluxos nacionais por sorteio: β por município × totais de origem do município."""
    post = idata.posterior
    mu = post["mu"].stack(s=("chain", "draw")).transpose("s", ...).values
    tau = post["tau"].stack(s=("chain", "draw")).transpose("s", ...).values
    z = post["z"].stack(s=("chain", "draw")).transpose("s", ...).values
    gam = post["gamma_urb"].stack(s=("chain", "draw")).transpose("s", ...).values
    dlt = post["delta_marg"].stack(s=("chain", "draw")).transpose("s", ...).values
    sel = rng.choice(mu.shape[0], min(n_sorteios, mu.shape[0]), replace=False)
    R, _ = matrizes(mun)
    s_idx = mun.uf.map({u: k for k, u in enumerate(ufs)}).to_numpy()
    urb, mrg = mun.urb_z.to_numpy(), mun.marg_z.to_numpy()
    tot = R.sum(0)
    out = np.empty((len(sel), NR, NC))
    for k, d in enumerate(sel):
        eta = mu[d][None] + tau[d][None] * z[d][s_idx] + gam[d][None] * urb[:, None, None] + dlt[d][None] * mrg[:, None, None]
        eta = np.concatenate([eta, np.zeros((len(mun), NR, 1))], axis=2)
        eta -= eta.max(2, keepdims=True)
        b = np.exp(eta)
        b /= b.sum(2, keepdims=True)
        out[k] = (R[:, :, None] * b).sum(0) / tot[:, None]
    return out


def verificacao_preditiva(idata, m, am, rng, n_sorteios=200):
    with m:
        pp = pm.sample_posterior_predictive(idata.sel(draw=slice(None, None, max(1, idata.posterior.sizes["draw"] // 50))),
                                            random_seed=rng, progressbar=False)
    yrep = pp.posterior_predictive["y"].stack(s=("chain", "draw")).transpose("s", ...).values
    _, Y = matrizes(am)
    N = Y.sum(1)
    obs_l = Y[:, 0] / N
    rep_l = yrep[:, :, 0] / N[None]
    lo, hi = np.percentile(rep_l, [5, 95], axis=0)
    cobertura90 = float(np.mean((obs_l >= lo) & (obs_l <= hi)))
    tot_obs = Y.sum(0)
    tot_rep = yrep.sum(1)
    p_tot = [float(np.mean(tot_rep[:, c] >= tot_obs[c])) for c in range(NC)]
    dp_obs = float(np.std(obs_l))
    dp_rep = np.std(rep_l, axis=1)
    return {"cobertura_intervalo_90_lula_share": cobertura90,
            "p_preditivo_totais_amostra": dict(zip(DEST, p_tot)),
            "dp_lula_share_obs": dp_obs, "dp_lula_share_rep_media": float(dp_rep.mean()),
            "p_preditivo_dp": float(np.mean(dp_rep >= dp_obs))}, (obs_l, rep_l)


def main(n_max=None, draws=1000, tune=1000, chains=4, priors=("neutra", "fidelidade_alta", "troca_alta")):
    rng = np.random.default_rng(SEMENTE)
    am, mun, ufs = dados(n_max)
    print("unidades:", len(am), flush=True)
    linhas, diag = [], {}
    for nome in priors:
        t0 = time.time()
        m = modelo(am, ufs, PRIORS[nome])
        with m:
            idata = pm.sample(draws=draws, tune=tune, chains=chains, cores=chains, target_accept=0.9, max_treedepth=9,
                              random_seed=SEMENTE, progressbar=False, idata_kwargs={"log_likelihood": False})
        tempo = time.time() - t0
        sumario = az.summary(idata, var_names=["mu", "tau", "gamma_urb", "delta_marg", "kappa"])
        sumario.to_csv(TABELAS / f"04_bayes_sumario_{nome}.csv")
        div = int(idata.sample_stats["diverging"].sum())
        ppc, _ = verificacao_preditiva(idata, m, am, rng)
        fl = fluxos_nacionais(idata, mun, ufs, rng=rng)
        for r, o in enumerate(ORIG):
            for c, d in enumerate(DEST):
                v = fl[:, r, c]
                linhas.append({"prior": nome, "origem": o, "destino": d, "media": v.mean(),
                               "ic95_inf": np.percentile(v, 2.5), "ic95_sup": np.percentile(v, 97.5)})
        diag[nome] = {"tempo_s": tempo, "divergencias": div,
                      "rhat_max": float(sumario.r_hat.max()), "ess_bulk_min": float(sumario.ess_bulk.min()),
                      "verificacao_preditiva": ppc}
        try:
            idata.to_netcdf(INTERIM / f"bayes_{nome}.nc")
        except Exception as e:  # falha ao gravar a posterior não invalida as tabelas
            print("aviso: posterior não gravada:", repr(e)[:200], flush=True)
        # grava as tabelas a cada prior concluída
        pd.DataFrame(linhas).to_csv(TABELAS / "04_bayes_matriz_nacional.csv", index=False)
        salvar_json({"diagnosticos": diag, "unidades": len(am), "draws": draws, "tune": tune,
                     "chains": chains, "semente": SEMENTE}, TABELAS / "04_bayes_diagnosticos.json")
        print(nome, json.dumps(diag[nome], indent=1, default=float), flush=True)
        print(pd.DataFrame(linhas).query("prior == @nome").round(4).to_string(), flush=True)
    pd.DataFrame(linhas).to_csv(TABELAS / "04_bayes_matriz_nacional.csv", index=False)
    salvar_json({"diagnosticos": diag, "unidades": len(am), "draws": draws, "tune": tune,
                 "chains": chains, "semente": SEMENTE}, TABELAS / "04_bayes_diagnosticos.json")


def recalcular_fluxos(priors=("neutra", "fidelidade_alta", "troca_alta")):
    """Recalcula os fluxos nacionais a partir das posteriores gravadas (sem novo MCMC)."""
    rng = np.random.default_rng(SEMENTE)
    _, mun, ufs = dados(None)
    linhas = []
    for nome in priors:
        arq = INTERIM / f"bayes_{nome}.nc"
        if not arq.exists():
            continue
        idata = az.from_netcdf(arq)
        fl = fluxos_nacionais(idata, mun, ufs, rng=rng)
        for r, o in enumerate(ORIG):
            for c, d in enumerate(DEST):
                v = fl[:, r, c]
                linhas.append({"prior": nome, "origem": o, "destino": d, "media": v.mean(),
                               "ic95_inf": np.percentile(v, 2.5), "ic95_sup": np.percentile(v, 97.5)})
    t = pd.DataFrame(linhas)
    t.to_csv(TABELAS / "04_bayes_matriz_nacional.csv", index=False)
    print(t.round(4).to_string())


if __name__ == "__main__":
    if sys.argv[1:] == ["recalcular"]:
        recalcular_fluxos()
        sys.exit()
    args = dict(a.split("=") for a in sys.argv[1:])
    main(n_max=int(args["n_max"]) if "n_max" in args else None,
         draws=int(args.get("draws", 1000)), tune=int(args.get("tune", 1000)),
         chains=int(args.get("chains", 4)),
         priors=tuple(args["priors"].split(",")) if "priors" in args else ("neutra", "fidelidade_alta", "troca_alta"))
