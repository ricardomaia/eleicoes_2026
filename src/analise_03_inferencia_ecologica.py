"""Etapa 3 — Modelo A (inferência ecológica) e teste da seção 7 (migração direta).

Para cada ano (2026, 2022, 2018) e cada nível de unidade:
  "secao"     amostra aleatória de seções, estratificada por UF (10%, mín. 400).
              2026: as seções com BU baixado; 2022/2018: mesmo desenho, mesma semente.
  "municipio" todos os municípios (sensibilidade ao nível de agregação).

Estimativa por UF (ei.ajustar); fluxos nacionais = Σ_UF (total de cada origem
na UF, calculado com TODAS as seções) × B_UF. Intervalos: bootstrap por
conglomerado (municípios), 200 réplicas por UF.

Teste da seção 7: impõe em todas as UFs a restrição
taxa(finalista de direita no 1T → finalista do PT no 2T) ≤ c, c ∈ {0, 1%, 2%,
5%, 10%}, e mede o aumento da deviance (teste F de quase-verossimilhança com φ
estimado no modelo livre). Repete no sentido inverso. Nomes dos finalistas:
2026 Flávio Bolsonaro e Lula; 2022 Jair Bolsonaro e Lula; 2018 Jair Bolsonaro
e Haddad (hipóteses "direita_para_pt" e "pt_para_direita"). Registra os fluxos que os demais grupos precisam ter em cada
hipótese.
"""
from __future__ import annotations

import time

import numpy as np
import pandas as pd

from comum import INTERIM, REGIAO, SEMENTE, TABELAS, salvar_json
from ei import ajustar, bootstrap_conglomerados, deviance, preparar, sobredispersao, teste_restricao
from fluxos import ROTULO

NOMES = {2026: ("Lula", "Flávio"), 2022: ("Lula", "Jair Bolsonaro"), 2018: ("Haddad", "Jair Bolsonaro")}
NOMES_COMPLETOS = {2026: ("Lula", "Flávio Bolsonaro"), 2022: ("Lula", "Jair Bolsonaro"),
                   2018: ("Haddad", "Jair Bolsonaro")}
# Blocos calculados antes da troca de nomes guardam as chaves antigas.
CHAVES_ANTIGAS = {"flavio_para_lula": "direita_para_pt", "lula_para_flavio": "pt_para_direita"}


def nome_hipotese(h: str, ano: int) -> str:
    a, b = NOMES_COMPLETOS[ano]
    return f"{b} (1T) → {a} (2T)" if h == "direita_para_pt" else f"{a} (1T) → {b} (2T)"


def rotulo(cod: str, ano: int) -> str:
    a, b = NOMES[ano]
    return ROTULO.get(cod, cod).replace("Lula", a).replace("Flávio", b)

DEST = ["a_2", "b_2", "bn_2", "abst_2"]
ORIG_BASE = ["a_1", "b_1", "o_1", "bn_1", "abst_1"]
ORIG_DET = ["a_1", "b_1", "cury_1", "renan_1", "caiado_1", "demais_1", "bn_1", "abst_1"]
TETOS = [0.0, 0.01, 0.02, 0.05, 0.10]
N_BOOT = 200
MIN_UNIDADES = 20  # UF com menos unidades usa as unidades da sua região para estimar B


def amostra_historica(sec: pd.DataFrame, ano: int) -> pd.DataFrame:
    """Mesmo desenho da amostra de 2026 (10% por UF, mínimo 400, semente fixa)."""
    rng = np.random.default_rng(SEMENTE + ano)
    u = sec[(sec.instalada_2 != "Não")].sort_values(["uf", "cd_mun", "zona", "secao"])
    partes = []
    for uf, g in u.groupby("uf", sort=True):
        n = min(len(g), max(400, int(round(0.10 * len(g)))))
        partes.append(g.iloc[np.sort(rng.choice(len(g), n, replace=False))])
    return pd.concat(partes)


def unidades(ano: int):
    sec = pd.read_parquet(INTERIM / f"secoes_{ano}.parquet")
    mun = pd.read_parquet(INTERIM / f"municipios_{ano}.parquet")
    if ano == 2026:
        sec["demais_1"] = sec.zema_1 + sec.outros_peq_1
        mun["demais_1"] = mun.zema_1 + mun.outros_peq_1
        if sec.a_2.notna().mean() > 0.99:
            # votacao_secao do 2º turno publicado (26/10/2026, 17h42 UTC): todas as seções instaladas.
            # Os resultados com a amostra de 50.821 BUs ficam em resultados/versao_amostra_bu/.
            am = sec[sec.a_2.notna() & (sec.aptos_1 > 0) & (sec.instalada_2 != "Não")].copy()
        else:
            am = sec[sec.na_amostra_bu.fillna(False).astype(bool)].copy()
    else:
        am = amostra_historica(sec, ano)
    totais_uf = sec.groupby("uf")[[c for c in dict.fromkeys(ORIG_DET + ORIG_BASE) if c in sec]].sum()
    # ajuste de cadastro nos totais (mesma regra de ei.preparar)
    d = sec.groupby("uf").apply(lambda g: (g.aptos_2 - g.aptos_1).clip(lower=0).sum(), include_groups=False)
    totais_uf["abst_1"] = totais_uf["abst_1"] + d
    return {"secao": am, "municipio": mun}, totais_uf


def _estimar_uf(args):
    """Ajuste de uma UF (ou da sua região): matriz, bootstrap por município e testes de teto."""
    uf, fonte, g, origens, tot, n_boot, tetos, semente = args
    rng = np.random.default_rng(semente)
    R, C, N, ok = preparar(g, origens, DEST)
    X = R / N[:, None]
    grupos = g.cd_mun.to_numpy()[ok]
    B, ll, res = ajustar(X, C)
    phi, gl = sobredispersao(B, X, C)
    dev = deviance(B, X, C)
    bs = bootstrap_conglomerados(X, C, grupos, B, n_boot, rng) if n_boot else None
    linhas_uf, testes = [], []
    for r, o in enumerate(origens):
        for c, dd in enumerate(DEST):
            linhas_uf.append({"uf": uf, "origem": o, "destino": dd, "taxa": B[r, c],
                              "ic95_inf": np.percentile(bs[:, r, c], 2.5) if bs is not None else np.nan,
                              "ic95_sup": np.percentile(bs[:, r, c], 97.5) if bs is not None else np.nan,
                              "phi": phi, "unidades": len(g), "estimado_com": fonte,
                              "convergiu": bool(res.success)})
    if tetos:
        iF, iL = origens.index("b_1"), origens.index("a_1")
        for nome, (r, c) in {"direita_para_pt": (iF, 0), "pt_para_direita": (iL, 1)}.items():
            for t in TETOS:
                if B[r, c] <= t:
                    Bc, devc = B, dev
                else:
                    Bc, _, _ = ajustar(X, C, B0=B, limites_celula={(r, c): (0.0, t)})
                    devc = deviance(Bc, X, C)
                    if devc < dev:  # o modelo livre contém o restrito: corrige o ótimo livre
                        B, dev = Bc, devc
                F, p = teste_restricao(dev, devc, phi, 1, gl)
                testes.append({"uf": uf, "estimado_com": fonte, "hipotese": nome, "teto": t, "taxa_livre": B[r, c],
                               "dev_livre": dev, "dev_restrito": devc, "aumento_dev": devc - dev,
                               "phi": phi, "gl": gl, "F": F, "p": p,
                               **{f"fluxo_{o}_{d}": tot[i] * Bc[i, j]
                                  for i, o in enumerate(origens) for j, d in enumerate(DEST)}})
    return uf, B, bs, linhas_uf, testes


def estimar(df: pd.DataFrame, origens, totais_uf, rng, n_boot=N_BOOT, tetos=True, ano=2026, processos=8):
    """As UFs são ajustadas em paralelo (desde 27/10/2026, quando o nível "seção" passou a ter todas
    as 499 mil seções). Cada UF recebe uma semente própria sorteada, em ordem, do gerador recebido,
    o que mantém a reprodutibilidade; a sequência de números aleatórios difere da execução de 26/10
    (sequencial, um gerador para todas as UFs), cujos resultados estão em resultados/versao_amostra_bu/."""
    ufs = sorted(df.uf.unique())
    sementes = rng.integers(0, 2**31, size=len(ufs))
    tarefas = []
    for uf, sem in zip(ufs, sementes):
        g = df[df.uf == uf]
        fonte = uf
        if len(g) < MIN_UNIDADES:
            fonte = "região " + REGIAO[uf]
            g = df[df.uf.map(REGIAO) == REGIAO[uf]]
        tarefas.append((uf, fonte, g, origens, totais_uf.loc[uf, origens].to_numpy(float), n_boot, tetos, int(sem)))
    if processos > 1 and len(tarefas) > 1:
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(min(processos, len(tarefas))) as ex:
            res = list(ex.map(_estimar_uf, tarefas))
    else:
        res = [_estimar_uf(t) for t in tarefas]
    linhas_uf, boots_nac, testes = [], [], []
    fluxo_nac = np.zeros((len(origens), len(DEST)))
    for (uf, B, bs, lu, ts), t in zip(res, tarefas):
        tot = t[4]
        fluxo_nac += tot[:, None] * B
        boots_nac.append(tot[None, :, None] * bs if bs is not None else None)
        linhas_uf += lu
        testes += ts
    tot_or = totais_uf[origens].sum().to_numpy(float)
    taxa_nac = fluxo_nac / tot_or[:, None]
    nac = []
    if boots_nac[0] is not None:
        soma_boot = np.sum(boots_nac, axis=0)  # n_boot × R × C (contagens)
        taxa_boot = soma_boot / tot_or[None, :, None]
    for r, o in enumerate(origens):
        for c, d in enumerate(DEST):
            reg = {"origem": o, "destino": d, "rotulo_origem": rotulo(o, ano), "rotulo_destino": rotulo(d, ano),
                   "taxa": taxa_nac[r, c], "votos": fluxo_nac[r, c]}
            if boots_nac[0] is not None:
                reg.update({"taxa_ic95_inf": np.percentile(taxa_boot[:, r, c], 2.5),
                            "taxa_ic95_sup": np.percentile(taxa_boot[:, r, c], 97.5),
                            "votos_ic95_inf": np.percentile(soma_boot[:, r, c], 2.5),
                            "votos_ic95_sup": np.percentile(soma_boot[:, r, c], 97.5)})
            nac.append(reg)
    return pd.DataFrame(nac), pd.DataFrame(linhas_uf), pd.DataFrame(testes)


def resumir_testes(testes: pd.DataFrame, origens) -> pd.DataFrame:
    from scipy import stats
    out = []
    for (h, t), g in testes.groupby(["hipotese", "teto"]):
        # Soma dos aumentos de deviance escalados por φ de cada UF: ~ χ²(k) sob H0 (k = UFs restringidas)
        k = int((g.aumento_dev > 1e-9).sum())
        chi = float((g.aumento_dev / g.phi).sum())
        reg = {"hipotese": h, "teto": t, "ufs_com_restricao_ativa": k, "chi2_total": chi,
               "p_conjunto": float(stats.chi2.sf(chi, max(k, 1))) if k else 1.0,
               "ufs_rejeitadas_5pct": int((g.p < 0.05).sum()),
               "ufs_rejeitadas_bonferroni": int((g.p < 0.05 / len(g)).sum()),
               "ufs_maior_incompatibilidade": ", ".join(g.sort_values("F", ascending=False).uf.head(5)
                                                         + " (F=" + g.sort_values("F", ascending=False).F.head(5).round(1).astype(str) + ")")}
        for o in origens:
            for d in DEST:
                col = f"fluxo_{o}_{d}"
                if col in g:
                    reg[col] = g[col].sum()
        out.append(reg)
    return pd.DataFrame(out)


def main(anos=(2026, 2022, 2018), sufixo="") -> dict:
    rng = np.random.default_rng(SEMENTE)
    resumo = {}
    nacionais, por_uf, testes_all = [], [], []
    for ano in anos:
        niveis, totais_uf = unidades(ano)
        conjuntos = [("base", ORIG_BASE)] + ([("detalhada", ORIG_DET)] if ano == 2026 else [])
        for nivel, df in niveis.items():
            for nome_or, origens in conjuntos:
                t0 = time.time()
                nboot = N_BOOT if (nome_or == "base") else 100
                cache = INTERIM / f"ei_bloco_{ano}_{nivel}_{nome_or}.pkl"
                if cache.exists():  # bloco já calculado numa execução anterior
                    nac, uf, tst = pd.read_pickle(cache)
                else:
                    nac, uf, tst = estimar(df, origens, totais_uf, np.random.default_rng([SEMENTE, ano, len(nivel), len(nome_or)]),
                                           n_boot=nboot, tetos=(nome_or == "base"), ano=ano)
                    pd.to_pickle((nac, uf, tst), cache)
                # rótulos sempre recalculados com os nomes corretos de cada ano
                nac["rotulo_origem"] = nac.origem.map(lambda o: rotulo(o, ano))
                nac["rotulo_destino"] = nac.destino.map(lambda d: rotulo(d, ano))
                if len(tst):
                    tst = tst.assign(hipotese=tst.hipotese.replace(CHAVES_ANTIGAS))
                    tst["descricao_hipotese"] = tst.hipotese.map(lambda h: nome_hipotese(h, ano))
                tag = dict(ano=ano, nivel=nivel, origens=nome_or)
                nacionais.append(nac.assign(**tag))
                por_uf.append(uf.assign(**tag))
                if len(tst):
                    testes_all.append(tst.assign(**tag))
                    rt = resumir_testes(tst, origens).assign(**tag)
                    rt["descricao_hipotese"] = rt.hipotese.map(lambda h: nome_hipotese(h, ano))
                    rt.to_csv(TABELAS / f"03_teste_migracao_{ano}_{nivel}.csv", index=False)
                print(ano, nivel, nome_or, f"{time.time() - t0:.0f}s", flush=True)
                with pd.option_context("display.width", 250, "display.float_format", "{:,.4f}".format):
                    print(nac[["rotulo_origem", "rotulo_destino", "taxa"] +
                              [c for c in ("taxa_ic95_inf", "taxa_ic95_sup") if c in nac]].to_string())
                    if len(tst):
                        print(rt[["hipotese", "teto", "chi2_total", "p_conjunto", "ufs_rejeitadas_5pct",
                                  "ufs_maior_incompatibilidade"]].to_string())
    pd.concat(nacionais).to_csv(TABELAS / f"03_matriz_transicao_nacional{sufixo}.csv", index=False)
    pd.concat(por_uf).to_csv(TABELAS / f"03_matriz_transicao_por_uf{sufixo}.csv", index=False)
    pd.concat(testes_all).to_csv(TABELAS / f"03_testes_migracao_por_uf{sufixo}.csv", index=False)
    salvar_json({"n_boot": N_BOOT, "semente": SEMENTE, "tetos": TETOS}, TABELAS / "03_parametros.json")
    return resumo


if __name__ == "__main__":
    import sys
    anos = tuple(int(x) for x in sys.argv[1:]) or (2026, 2022, 2018)
    main(anos, sufixo="" if len(anos) == 3 else "_" + "_".join(map(str, anos)))
