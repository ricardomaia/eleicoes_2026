"""Etapa 3b — Sensibilidade do Modelo A à definição dos estratos.

O Modelo A supõe que, dentro de cada UF, as taxas de transição são iguais em
todas as seções. Se elas variarem junto com a composição do 1º turno (por
exemplo, se eleitores que votaram em branco ou nulo se comportam de forma
diferente onde Lula é forte), a estimativa estadual mistura esses efeitos
(viés de agregação). Aqui o mesmo estimador é aplicado com estratos mais
finos, e comparam-se as taxas nacionais resultantes:

  E0  UF (especificação principal)
  E1  região × faixa de margem do 1º turno no município (Flávio ≥ +10 pp,
      equilibrado, Lula ≥ +10 pp)
  E2  UF × tercil de urbanização do município (Censo 2022)
  E3  município com ≥ 60 seções na amostra; demais seções agrupadas por UF

Unidades: amostra de BUs do 2º turno (2026) e, para comparação, a amostra de
mesmo desenho de 2022. Fluxos nacionais = Σ_estrato totais de origem do
estrato (todas as seções) × B_estrato.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from analise_03_inferencia_ecologica import NOMES, amostra_historica
from comum import DERIVADOS, INTERIM, REGIAO, TABELAS
from ei import ajustar, preparar

ORIG = ["a_1", "b_1", "o_1", "bn_1", "abst_1"]
DEST = ["a_2", "b_2", "bn_2", "abst_2"]


def estratos(sec: pd.DataFrame, mun: pd.DataFrame, cov: pd.DataFrame) -> pd.DataFrame:
    m = mun[["uf", "cd_mun", "a_1", "b_1", "validos_1"]].copy()
    m["marg"] = (m.a_1 - m.b_1) / m.validos_1
    m["faixa"] = pd.cut(m.marg, [-1.01, -0.10, 0.10, 1.01], labels=["flavio+10", "equilibrado", "lula+10"])
    m = m.merge(cov[["uf", "cd_mun", "pct_urbana"]], on=["uf", "cd_mun"], how="left")
    m["urb_t"] = pd.qcut(m.pct_urbana.fillna(100), 3, labels=["urb_baixa", "urb_media", "urb_alta"])
    s = sec.merge(m[["uf", "cd_mun", "faixa", "urb_t"]], on=["uf", "cd_mun"], how="left")
    s["E0"] = s.uf
    s["E1"] = s.uf.map(REGIAO) + "|" + s.faixa.astype(str)
    s["E2"] = s.uf + "|" + s.urb_t.astype(str)
    return s


def _totais(t):
    tr = t[ORIG].sum().to_numpy(float, copy=True)
    tr[-1] += (t.aptos_2 - t.aptos_1).clip(lower=0).sum()
    return tr


def _matriz(g):
    R, C, N, ok = preparar(g, ORIG, DEST)
    B, _, _ = ajustar(R / N[:, None], C)
    return B


def nacional(todas, amostra, col, B_uf, min_unid=30):
    """Estratos com menos de min_unid seções na amostra usam a matriz da UF."""
    fl = np.zeros((5, 4))
    usados = 0
    for e, t in todas.groupby(col):
        g = amostra[amostra[col] == e]
        if len(g) >= min_unid:
            fl += _totais(t)[:, None] * _matriz(g)
            usados += 1
        else:
            for uf, tu in t.groupby("uf"):
                fl += _totais(tu)[:, None] * B_uf[uf]
    return fl, usados


def main():
    from analise_02_mobilizacao import covariaveis
    cov = covariaveis()
    linhas = []
    for ano in (2026, 2022):
        sec = pd.read_parquet(INTERIM / f"secoes_{ano}.parquet")
        mun = pd.read_parquet(INTERIM / f"municipios_{ano}.parquet")
        sec = sec[sec.uf != "ZZ"]
        if ano == 2026:
            am = sec[sec.na_amostra_bu.fillna(False).astype(bool)]
        else:
            am = amostra_historica(sec, ano)
        todas = estratos(sec, mun, cov)
        am = estratos(am, mun, cov)
        # E3: municípios grandes na amostra têm matriz própria
        n_mun = am.groupby(["uf", "cd_mun"]).size()
        grandes = set(n_mun[n_mun >= 60].index)
        for d in (todas, am):
            chave = list(zip(d.uf, d.cd_mun))
            d["E3"] = [f"{u}|{c}" if (u, c) in grandes else u for u, c in chave]
        B_uf = {uf: _matriz(g) for uf, g in am.groupby("uf")}
        for col, nome in [("E0", "UF"), ("E1", "região × faixa de margem"), ("E2", "UF × tercil de urbanização"),
                          ("E3", "município grande ou UF")]:
            fl, usados = nacional(todas, am, col, B_uf)
            tot = fl.sum(1, keepdims=True)
            B = fl / tot
            a, b = NOMES[ano]
            for i, o in enumerate(ORIG):
                for j, dd in enumerate(DEST):
                    linhas.append({"ano": ano, "estratificacao": nome, "estratos_usados": usados,
                                   "origem": o, "destino": dd, "taxa": B[i, j],
                                   "finalista_PT": a, "finalista_direita": b})
            print(ano, nome, usados, "F→PT %.4f  BN→PT %.4f  A→PT %.4f  O→PT %.4f" %
                  (B[1, 0], B[3, 0], B[4, 0], B[2, 0]), flush=True)
    t = pd.DataFrame(linhas)
    t.to_csv(TABELAS / "03b_sensibilidade_estratos.csv", index=False)
    piv = t.pivot_table(index=["ano", "origem", "destino"], columns="estratificacao", values="taxa")
    with pd.option_context("display.width", 250, "display.float_format", "{:,.4f}".format):
        print(piv.to_string())


if __name__ == "__main__":
    main()
