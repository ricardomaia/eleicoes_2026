"""Auditoria 4 — Modelo B com cadeias mais longas e diagnósticos ampliados.

Mesmo modelo de analise_04_bayes.py (importado daqui, sem alteração), mas:
  - tune e draws maiores (padrão 1000 + 1000, 4 cadeias), para R-hat e ESS
    confiáveis; o Modelo B original rodou com 600 + 400 e teve R-hat 1,042 na
    prior "troca alta";
  - os sorteios dos fluxos nacionais são gravados, para medir as correlações
    posteriores entre taxas (ex.: Flávio→Lula × Lula→abstenção), que mostram
    quais combinações de parâmetros os dados não separam;
  - diagnósticos por parâmetro (R-hat, ESS bulk/tail) gravados por completo.
As saídas vão para resultados/auditoria/ e interim/auditoria/, sem tocar nos
resultados originais.

Uso: python auditoria_04_bayes.py prior=neutra [n_max=4000 draws=1000 tune=1000 chains=4]
"""
from __future__ import annotations

import json
import sys
import time

import arviz as az
import numpy as np
import pandas as pd
import pymc as pm

import analise_04_bayes as a4
from auditoria_comum import TAB, salvar_json
from comum import INTERIM, SEMENTE

INTERIM_AUD = INTERIM / "auditoria"
INTERIM_AUD.mkdir(exist_ok=True)


def main(prior: str, n_max=4000, draws=1000, tune=1000, chains=4):
    rng = np.random.default_rng(SEMENTE)
    am, mun, ufs = a4.dados(n_max)
    t0 = time.time()
    m = a4.modelo(am, ufs, a4.PRIORS[prior])
    with m:
        idata = pm.sample(draws=draws, tune=tune, chains=chains, cores=chains, target_accept=0.9, max_treedepth=9,
                          random_seed=SEMENTE, progressbar=False, idata_kwargs={"log_likelihood": False})
    tempo = time.time() - t0
    sumario = az.summary(idata, var_names=["mu", "tau", "gamma_urb", "delta_marg", "kappa"])
    sumario.to_csv(TAB / f"04_bayes_sumario_{prior}.csv")
    div = int(idata.sample_stats["diverging"].sum())
    ppc, _ = a4.verificacao_preditiva(idata, m, am, rng)
    fl = a4.fluxos_nacionais(idata, mun, ufs, n_sorteios=1000, rng=rng)
    np.save(INTERIM_AUD / f"bayes_fluxos_{prior}.npy", fl)
    linhas = []
    for r, o in enumerate(a4.ORIG):
        for c, d in enumerate(a4.DEST):
            v = fl[:, r, c]
            linhas.append({"prior": prior, "origem": o, "destino": d, "media": v.mean(), "mediana": np.median(v),
                           "ic95_inf": np.percentile(v, 2.5), "ic95_sup": np.percentile(v, 97.5)})
    pd.DataFrame(linhas).to_csv(TAB / f"04_bayes_matriz_nacional_{prior}.csv", index=False)
    # correlações posteriores entre taxas nacionais (quais trocas os dados não separam)
    nomes = [f"{o}->{d}" for o in a4.ORIG for d in a4.DEST]
    flat = fl.reshape(len(fl), -1)
    corr = pd.DataFrame(np.corrcoef(flat.T), index=nomes, columns=nomes)
    corr.to_csv(TAB / f"04_bayes_correlacoes_posteriores_{prior}.csv")
    diag = {"prior": prior, "tempo_s": tempo, "divergencias": div, "draws": draws, "tune": tune, "chains": chains,
            "unidades": int(len(am)),
            "rhat_max": float(sumario.r_hat.max()), "n_param_rhat_gt_1_01": int((sumario.r_hat > 1.01).sum()),
            "ess_bulk_min": float(sumario.ess_bulk.min()), "ess_tail_min": float(sumario.ess_tail.min()),
            "verificacao_preditiva": ppc,
            "corr_FL_x_L_abst": float(corr.loc["b_1->a_2", "a_1->abst_2"]),
            "corr_FL_x_A_L": float(corr.loc["b_1->a_2", "abst_1->a_2"]),
            "corr_FL_x_BN_L": float(corr.loc["b_1->a_2", "bn_1->a_2"]),
            "corr_FL_x_F_abst": float(corr.loc["b_1->a_2", "b_1->abst_2"]),
            "corr_BN_L_x_A_L": float(corr.loc["bn_1->a_2", "abst_1->a_2"])}
    salvar_json(diag, TAB / f"04_bayes_diagnosticos_{prior}.json")
    try:
        idata.to_netcdf(INTERIM_AUD / f"bayes_{prior}.nc")
    except Exception as e:
        print("aviso: posterior não gravada:", repr(e)[:200], flush=True)
    print(json.dumps(diag, indent=1, default=float), flush=True)
    print(pd.DataFrame(linhas).round(4).to_string(), flush=True)


if __name__ == "__main__":
    args = dict(a.split("=") for a in sys.argv[1:])
    main(args.get("prior", "neutra"), n_max=int(args.get("n_max", 4000)), draws=int(args.get("draws", 1000)),
         tune=int(args.get("tune", 1000)), chains=int(args.get("chains", 4)))
