"""Baixa indicadores municipais do IBGE (API SIDRA v3) e monta uma tabela única.

Indicadores (Censo Demográfico 2022, salvo indicação):
  pop_2022          tabela 4709, variável 93   População residente
  pct_urbana        tabela 9923, variável 1000093, situação = Urbana
  alfabetizacao_15  tabela 9543, variável 2513 (total de sexo, cor e idade)
  renda_pc_media    tabela 10295, variável 13431 (R$; totais das classificações)
  renda_pc_mediana  tabela 10295, variável 13534
  pct_preta_parda   tabela 9605, variável 1000093, cor ou raça = Preta + Parda
  pib_2021_mil      tabela 5938, variável 37 (PIB a preços correntes, 2021)

Saída: dados_derivados/ibge_municipios.csv (código IBGE de 7 dígitos).
"""
from __future__ import annotations

import json

import pandas as pd

from comum import DERIVADOS, RAW, baixar

API = "https://servicodados.ibge.gov.br/api/v3/agregados"

CONSULTAS = {
    "pop_2022": ("4709", "2022", "93", ""),
    "pct_urbana": ("9923", "2022", "1000093", "&classificacao=1[1]"),
    "alfabetizacao_15": ("9543", "2022", "2513",
                         "&classificacao=2[6794]|86[95251]|287[100362]"),
    "renda_pc_media": ("10295", "2022", "13431",
                       "&classificacao=2[6794]|86[95251]|58[95253]"),
    "renda_pc_mediana": ("10295", "2022", "13534",
                         "&classificacao=2[6794]|86[95251]|58[95253]"),
    "pct_preta": ("9605", "2022", "1000093", "&classificacao=86[2777]"),
    "pct_parda": ("9605", "2022", "1000093", "&classificacao=86[2779]"),
    "pib_2021_mil": ("5938", "2021", "37", ""),
}


def ler_sidra(caminho) -> pd.Series:
    d = json.loads(caminho.read_text(encoding="utf-8"))
    serie = d[0]["resultados"][0]["series"]
    out = {}
    for s in serie:
        cod = s["localidade"]["id"]
        v = list(s["serie"].values())[0]
        try:
            out[cod] = float(v)
        except (TypeError, ValueError):
            out[cod] = float("nan")  # "-", "...", "X" = sem dado / sigilo
    return pd.Series(out)


def main() -> None:
    colunas = {}
    for nome, (tab, per, var, cls) in CONSULTAS.items():
        url = f"{API}/{tab}/periodos/{per}/variaveis/{var}?localidades=N6[all]{cls}"
        destino = RAW / "ibge" / f"sidra_{tab}_{var}_{nome}.json"
        baixar(url, destino, tentativas=6, timeout=300)
        colunas[nome] = ler_sidra(destino)
        print(nome, len(colunas[nome]))
    df = pd.DataFrame(colunas)
    df.index.name = "cd_ibge"
    df["pct_preta_parda"] = df.pop("pct_preta") + df.pop("pct_parda")
    df["pib_pc_2021"] = df["pib_2021_mil"] * 1000 / df["pop_2022"]
    df.reset_index().to_csv(DERIVADOS / "ibge_municipios.csv", index=False)
    print(df.describe().T)


if __name__ == "__main__":
    main()
