"""Auditoria 7 — Amapá: sensibilidade da migração Flávio→Lula estimada em Macapá e Santana.

Dados: todas as 1.914 seções do AP com BU do 2º turno (como em analise_03c).

Análises (cada uma para "AP todas", "Macapá e Santana" e "interior"):
 1. M0 (constância): taxa livre, intervalos por bootstrap de seção, de zona e de
    município (16 municípios; 1.301 seções em duas cidades → o conglomerado
    relevante é a zona ou o local de votação).
 2. Regressão de Goodman sem restrições com erro-padrão por zona.
 3. M1 (taxas dependentes da composição da própria seção, z = participação de
    Lula no 1T padronizada) e M2 (preferência latente): taxa Flávio→Lula e
    Lula→abstenção, deviance.
 4. Perfil de troca: fixando Flávio→Lula em c ∈ {0, 2, 4, 6, 8, 10%}, qual é a
    abstenção de eleitores de Lula, a mobilização de abstencionistas e a
    deviance do melhor ajuste? Mostra o que o modelo troca por migração.
 5. Influência: excluir um município por vez; excluir uma zona por vez; excluir
    seções com |Δcomparecimento| > 10 p.p. ou com mudança de aptos.
 6. Fronteira de heterogeneidade (programa linear de auditoria_01) para o AP:
    fração mínima de eleitores com comportamento fora da matriz comum para
    reproduzir todas as seções com c imposto.
 7. Múltiplas comparações: o AP foi a UF de maior F entre 27 UFs × 2 sentidos ×
    5 tetos; o relatório já aplica Bonferroni, registra-se o p ajustado.

Saídas: resultados/auditoria/tabelas/07_amapa_*.csv
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.api as sm

from auditoria_01_identificacao import _fronteira_uf
from auditoria_comum import DEST, ORIG, TAB, iA, iF, iL, jA, jL, matrizes_RC, salvar_json
from comum import INTERIM, SEMENTE
from ei import ajustar, deviance, sobredispersao, teste_restricao
from ei_cov import B_M1, B_M2, ajustar_M1, ajustar_M2, deviance_unidades, pi_latente


def carregar():
    bu = pd.read_parquet(INTERIM / "bu_t2_completo_AP.parquet").rename(columns={"mun": "cd_mun"})
    bu = bu[bu.erro == ""]
    sec = pd.read_parquet(INTERIM / "secoes_2026.parquet")
    s = sec[sec.uf == "AP"].drop(columns=["a_2", "b_2"]).merge(
        bu[["uf", "cd_mun", "zona", "secao", "v13", "v22"]], on=["uf", "cd_mun", "zona", "secao"])
    s["a_2"], s["b_2"] = s.v13.fillna(0), s.v22.fillna(0)
    s["grupo"] = np.where(s.nm_municipio.isin(["MACAPÁ", "SANTANA"]), "Macapá e Santana", "interior")
    s["dcomp_pp"] = 100 * (s.comp_2 / s.aptos_2 - s.comp_1 / s.aptos_1)
    s["pi"] = pi_latente(s)
    sh = s.a_1 / s.validos_1.where(s.validos_1 > 0)
    s["z"] = ((sh - sh.mean()) / sh.std()).fillna(0.0)
    return s


def m0(g):
    R, C, N, ok = matrizes_RC(g)
    X = R / N[:, None]
    B, ll, _ = ajustar(X, C)
    phi, gl = sobredispersao(B, X, C)
    return X, C, N, ok, B, deviance(B, X, C), phi, gl


def boot(X, C, B, grupos, n, rng):
    ug, inv = np.unique(grupos, return_inverse=True)
    idx_g = [np.flatnonzero(inv == g) for g in range(len(ug))]
    v = []
    for _ in range(n):
        esc = rng.integers(0, len(ug), len(ug))
        idx = np.concatenate([idx_g[g] for g in esc])
        Bb, _, _ = ajustar(X[idx], C[idx], B0=B)
        v.append(Bb[iF, jL])
    return np.percentile(v, [2.5, 97.5])


def main(n_boot=300):
    s = carregar()
    rng = np.random.default_rng(SEMENTE)
    conjuntos = [("AP todas", s)] + [(k, g) for k, g in s.groupby("grupo")]
    principal, perfil, infl, goodman, fronteira = [], [], [], [], []
    for nome, g in conjuntos:
        X, C, N, ok, B, dev, phi, gl = m0(g)
        gg = g[ok]
        reg = {"conjunto": nome, "secoes": len(X), "M0_FL": B[iF, jL], "M0_L_abst": B[iL, jA], "M0_F_abst": B[iF, jA],
               "M0_A_L": B[iA, jL], "M0_dev": dev, "M0_phi": phi}
        for cl, nome_cl in [(gg.index.to_numpy(), "secao"), (gg.zona.to_numpy(), "zona"), (gg.cd_mun.to_numpy(), "municipio"),
                            ((gg.cd_mun.astype(str) + "-" + gg.zona.astype(str) + "-" + gg.nr_local.astype(str)).to_numpy(), "local")]:
            if len(np.unique(cl)) >= 3:
                lo, hi = boot(X, C, B, cl, n_boot, rng)
                reg[f"M0_FL_ic95_inf_boot_{nome_cl}"], reg[f"M0_FL_ic95_sup_boot_{nome_cl}"] = lo, hi
        # Goodman por zona
        y = C[:, jL] / N
        fit = sm.WLS(y, X, weights=N).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(gg.zona.to_numpy())[0]})
        goodman.append({"conjunto": nome, "coef_FL": fit.params[iF], "ep_FL_cluster_zona": fit.bse[iF],
                        "coef_L_abst_implicito": np.nan, "coef_LL": fit.params[iL], "coef_AL": fit.params[iA],
                        "ic95_FL": [fit.params[iF] - 1.96 * fit.bse[iF], fit.params[iF] + 1.96 * fit.bse[iF]]})
        # M1 e M2
        z, pi = gg.z.to_numpy(), gg.pi.to_numpy()
        a1, b1, ll1, r1 = ajustar_M1(X, C, z, B0=B)
        B1 = B_M1(a1, b1, z)
        fl1 = (X[:, :, None] * N[:, None, None] * B1).sum(0)
        t1 = fl1 / fl1.sum(1, keepdims=True)
        p2, ll2, r2 = ajustar_M2(X, C, pi, B0=B)
        B2 = B_M2(p2, pi)
        fl2 = (X[:, :, None] * N[:, None, None] * B2).sum(0)
        t2 = fl2 / fl2.sum(1, keepdims=True)
        reg.update({"M1_FL": t1[iF, jL], "M1_L_abst": t1[iL, jA], "M1_A_L": t1[iA, jL],
                    "M1_dev": deviance_unidades(np.einsum("ir,irc->ic", X, B1), C),
                    "M2_FL": t2[iF, jL], "M2_L_abst": t2[iL, jA], "M2_A_L": t2[iA, jL],
                    "M2_dev": deviance_unidades(np.einsum("ir,irc->ic", X, B2), C)})
        # teste de teto (M0) e Bonferroni sobre 27 UFs × 2 sentidos
        for t in (0.0, 0.01, 0.02, 0.05):
            Bc, _, _ = ajustar(X, C, B0=B, limites_celula={(iF, jL): (0.0, t)}) if B[iF, jL] > t else (B, 0, 0)
            F, p = teste_restricao(dev, deviance(Bc, X, C), phi, 1, gl)
            reg[f"p_teto_{t}"] = p
            reg[f"p_teto_{t}_bonferroni_54"] = min(1.0, 54 * p)
        principal.append(reg)
        # perfil de troca
        for c in (0.0, 0.02, 0.04, 0.06, 0.08, 0.10):
            Bc, _, _ = ajustar(X, C, B0=B, limites_celula={(iF, jL): (c, c)})
            perfil.append({"conjunto": nome, "FL_fixo": c, "L_abst": Bc[iL, jA], "F_abst": Bc[iF, jA], "A_L": Bc[iA, jL],
                           "BN_L": Bc[3, jL], "O_L": Bc[2, jL], "dev": deviance(Bc, X, C), "dev_menos_livre": deviance(Bc, X, C) - dev,
                           "dev_escalada_phi": (deviance(Bc, X, C) - dev) / phi})
        # influência
        for mun_ex, _ in gg.groupby("cd_mun"):
            h = gg[gg.cd_mun != mun_ex]
            if len(h) > 30:
                _, _, _, _, Bh, _, _, _ = m0(h)
                infl.append({"conjunto": nome, "excluido": f"municipio {mun_ex} ({gg[gg.cd_mun == mun_ex].nm_municipio.iloc[0]})",
                             "secoes_restantes": len(h), "FL": Bh[iF, jL]})
        for zona_ex, _ in gg.groupby("zona"):
            h = gg[gg.zona != zona_ex]
            _, _, _, _, Bh, _, _, _ = m0(h)
            infl.append({"conjunto": nome, "excluido": f"zona {zona_ex}", "secoes_restantes": len(h), "FL": Bh[iF, jL]})
        for rot, mask in [("|Δcomparecimento| > 10 pp", gg.dcomp_pp.abs() > 10), ("aptos mudaram entre turnos", gg.aptos_1 != gg.aptos_2),
                          ("|Δcomparecimento| > 5 pp", gg.dcomp_pp.abs() > 5)]:
            h = gg[~mask]
            _, _, _, _, Bh, _, _, _ = m0(h)
            infl.append({"conjunto": nome, "excluido": rot, "secoes_restantes": len(h), "FL": Bh[iF, jL]})
        # fronteira LP
        R_ = X * N[:, None]
        for c in (None, 0.0, 0.02, 0.05, 0.08, 0.10):
            fronteira.append({"conjunto": nome, **_fronteira_uf((nome, R_, C, c))})
    pd.DataFrame(principal).to_csv(TAB / "07_amapa_principal.csv", index=False)
    pd.DataFrame(perfil).to_csv(TAB / "07_amapa_perfil_troca.csv", index=False)
    pd.DataFrame(infl).to_csv(TAB / "07_amapa_influencia.csv", index=False)
    pd.DataFrame(goodman).to_csv(TAB / "07_amapa_goodman.csv", index=False)
    pd.DataFrame(fronteira).to_csv(TAB / "07_amapa_fronteira.csv", index=False)
    with pd.option_context("display.width", 250, "display.max_columns", 40, "display.float_format", "{:,.4f}".format):
        print(pd.DataFrame(principal).T.to_string())
        print(pd.DataFrame(perfil).to_string())
        print(pd.DataFrame(infl).to_string())
        print(pd.DataFrame(goodman).to_string())
        print(pd.DataFrame(fronteira)[["conjunto", "teto_FL", "status", "fracao_minima_desviante"]].to_string())


if __name__ == "__main__":
    main()
