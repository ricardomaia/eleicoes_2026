"""Testes automatizados de consistência.

Dois grupos:
  - testes de método (rodam sempre): leitor de BU, limites de Fréchet,
    estimador de inferência ecológica em dados sintéticos com matriz conhecida;
  - testes dos dados (rodam se as bases de interim/ existirem): totais
    oficiais, identidades contábeis em cada seção e em cada município,
    conferência entre fontes independentes do TSE.
Execução: pytest -q tests/   (a partir da pasta do projeto)
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from boletim_urna import ler_bu  # noqa: E402
from comum import INTERIM  # noqa: E402
from ei import ajustar, deviance, sobredispersao  # noqa: E402
from ei import teste_restricao as f_quase_verossimilhanca  # noqa: E402
from fluxos import limites_frechet  # noqa: E402

DADOS_TESTE = Path(__file__).parent / "dados"


# ---------------------------------------------------------------- método
def test_leitor_bu_urna_eletronica():
    r = ler_bu((DADOS_TESTE / "01074-0004-0001.bu").read_bytes())
    assert (r["municipio"], r["zona"], r["secao"]) == (1074, 4, 1)
    assert r["aptos"] == 262 and r["comparecimento"] == 202
    assert r["votos"] == {13: 68, 22: 127}
    assert (r["brancos"], r["nulos"]) == (3, 4)
    assert sum(r["votos"].values()) + r["brancos"] + r["nulos"] == r["comparecimento"]


def test_leitor_bu_sistema_apuracao_exterior():
    r = ler_bu((DADOS_TESTE / "29254-0001-0001.bu").read_bytes())
    assert (r["municipio"], r["zona"], r["secao"]) == (29254, 1, 1)
    assert r["aptos"] == 91 and r["comparecimento"] == 53
    assert r["votos"] == {13: 31, 22: 22}


def test_limites_frechet():
    R = np.array([[60.0, 40.0]])   # linhas: 60 e 40
    C = np.array([[70.0, 30.0]])   # colunas: 70 e 30
    lo, hi = limites_frechet(R, C)
    assert lo[0, 0] == 30 and hi[0, 0] == 60   # max(0, 60+70−100), min(60, 70)
    assert lo[1, 1] == 0 and hi[1, 1] == 30
    # soma em unidades: limite agregado é a soma dos limites
    lo2, hi2 = limites_frechet(np.vstack([R, R]), np.vstack([C, C]))
    assert lo2[0, 0] == 60 and hi2[0, 0] == 120


def _sintetico(seed=3, n=3000):
    rng = np.random.default_rng(seed)
    B = np.array([[.93, .02, .02, .03], [.03, .92, .02, .03], [.45, .35, .1, .1],
                  [.25, .15, .4, .2], [.08, .05, .02, .85]])
    X = rng.dirichlet([8, 8, 1.5, 0.6, 3], size=n)
    N = rng.integers(150, 400, n)
    Y = np.array([rng.multinomial(N[i], X[i] @ B) for i in range(n)], float)
    return X, Y, B


def test_ei_recupera_matriz_conhecida():
    X, Y, B = _sintetico()
    Bh, _, res = ajustar(X, Y)
    assert res.success
    assert np.allclose(Bh.sum(1), 1) and (Bh >= 0).all()
    assert np.abs(Bh - B).max() < 0.03


def test_ei_restricao_exata_e_teste_detecta_teto_falso():
    X, Y, B = _sintetico()
    Bh, _, _ = ajustar(X, Y)
    d0 = deviance(Bh, X, Y)
    phi, gl = sobredispersao(Bh, X, Y)
    Bc, _, _ = ajustar(X, Y, B0=Bh, limites_celula={(1, 0): (0.0, 0.0)})
    assert Bc[1, 0] == 0.0 and np.allclose(Bc.sum(1), 1)
    dc = deviance(Bc, X, Y)
    assert dc >= d0 - 1e-6
    F, p = f_quase_verossimilhanca(d0, dc, phi, 1, gl)
    assert p < 1e-6           # taxa verdadeira 3%: teto de 0% deve ser rejeitado
    Bc5, _, _ = ajustar(X, Y, B0=Bh, limites_celula={(1, 0): (0.0, 0.05)})
    F5, p5 = f_quase_verossimilhanca(d0, deviance(Bc5, X, Y), phi, 1, gl)
    assert p5 > 0.05          # teto de 5% é compatível


# ---------------------------------------------------------------- dados
def _carregar(nome):
    p = INTERIM / nome
    if not p.exists():
        pytest.skip(f"{nome} não encontrado (rode montar_base.py)")
    return pd.read_parquet(p)


def test_totais_oficiais_2026():
    s = _carregar("secoes_2026.parquet")
    assert s.aptos_1.sum() == 158_745_502 == s.aptos_2.sum()
    assert s.comp_1.sum() == 125_275_835
    assert s.validos_1.sum() == 119_300_788
    assert s.a_1.sum() == 53_879_538 and s.b_1.sum() == 56_104_503
    assert s.brancos_1.sum() == 2_300_798 and s.bn_1.sum() - s.brancos_1.sum() == 3_674_249
    assert s.comp_2.sum() == 128_236_074 and s.validos_2.sum() == 124_082_273
    m = _carregar("municipios_2026.parquet")
    assert m.a_2.sum() == 64_256_232 and m.b_2.sum() == 59_826_041


@pytest.mark.parametrize("ano", [2026, 2022, 2018])
def test_identidades_por_secao(ano):
    s = _carregar(f"secoes_{ano}.parquet")
    for t in (1, 2):
        assert (s[f"comp_{t}"] == s[f"validos_{t}"] + s[f"bn_{t}"]).all()
        assert (s[f"aptos_{t}"] == s[f"comp_{t}"] + s[f"abst_{t}"]).all()
        assert (s[f"comp_{t}"] <= s[f"aptos_{t}"]).all()
    assert (s.a_1 + s.b_1 + s.o_1 == s.validos_1).all()
    assert not s.duplicated(["uf", "cd_mun", "zona", "secao"]).any()
    if ano != 2026:
        assert (s.a_2 + s.b_2 == s.validos_2).all()


def test_bu_amostra_confere_detalhe_secao():
    s = _carregar("secoes_2026.parquet")
    a = s[s.na_amostra_bu.fillna(False).astype(bool)]
    assert len(a) > 40_000
    assert (a.bu_aptos == a.aptos_2).all()
    assert (a.bu_comp == a.comp_2).all()
    assert (a.bu_brancos == a.brancos_2).all() and (a.bu_nulos == a.nulos_2).all()
    assert (a.a_2 + a.b_2 == a.validos_2).all()


def test_divulgacao_municipal_confere_detalhe_secao():
    m = _carregar("municipios_2026.parquet")
    for x, y in [("json_aptos", "aptos_2"), ("json_comp", "comp_2"), ("json_validos", "validos_2"),
                 ("json_brancos", "brancos_2"), ("json_nulos", "nulos_2")]:
        assert (m[x] == m[y]).all(), x
    assert (m.a_2 + m.b_2 == m.validos_2).all()
