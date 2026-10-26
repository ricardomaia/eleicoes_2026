"""Baixa os arquivos do Portal de Dados Abertos do TSE (cdn.tse.jus.br) e do IBGE.

Uso:
    python baixar_dados_abertos.py            # conjunto principal
    python baixar_dados_abertos.py --secao-uf # também votação por seção de
                                              # todos os cargos, por UF (H4)

Cada arquivo é registrado em integridade/manifesto_downloads.csv com URL,
data de acesso, tamanho, SHA-256, Last-Modified e ETag do servidor.
O CDN do TSE aplica limite de requisições (HTTP 429); o download é
sequencial e espera quando recebe 429.
"""
from __future__ import annotations

import argparse
import time

from comum import CDN, RAW, UFS, baixar

PRINCIPAIS = {
    2026: [
        "votacao_secao/votacao_secao_2026_BR.zip",
        "detalhe_votacao_secao/detalhe_votacao_secao_2026.zip",
        "detalhe_votacao_munzona/detalhe_votacao_munzona_2026.zip",
        "votacao_partido_munzona/votacao_partido_munzona_2026.zip",
        "votacao_candidato_munzona/votacao_candidato_munzona_2026.zip",
        "relatorio_resultado_totalizacao/Relatorio_Resultado_Totalizacao_2026_BR.zip",
    ],
    2022: [
        "votacao_secao/votacao_secao_2022_BR.zip",
        "detalhe_votacao_secao/detalhe_votacao_secao_2022.zip",
        "detalhe_votacao_munzona/detalhe_votacao_munzona_2022.zip",
        "votacao_partido_munzona/votacao_partido_munzona_2022.zip",
    ],
    2018: [
        "votacao_secao/votacao_secao_2018_BR.zip",
        "detalhe_votacao_secao/detalhe_votacao_secao_2018.zip",
        "detalhe_votacao_munzona/detalhe_votacao_munzona_2018.zip",
        "votacao_partido_munzona/votacao_partido_munzona_2018.zip",
    ],
}

IBGE = {
    # Malha municipal (GeoJSON, qualidade mínima) — mapas e vizinhança espacial.
    "malha_municipios_BR.geojson":
        "https://servicodados.ibge.gov.br/api/v3/malhas/paises/BR"
        "?formato=application/vnd.geo+json&qualidade=minima&intrarregiao=municipio",
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--secao-uf", action="store_true",
                    help="baixa votacao_secao_2026_<UF>.zip (todos os cargos)")
    ap.add_argument("--anos", default="2026,2022,2018")
    a = ap.parse_args()

    for ano in [int(x) for x in a.anos.split(",")]:
        for rel in PRINCIPAIS[ano]:
            url = f"{CDN}/{rel}"
            destino = RAW / str(ano) / rel.rsplit("/", 1)[1]
            print("baixando", url, flush=True)
            baixar(url, destino, tentativas=40,
                   sobrescrever=(ano == 2026 and "relatorio" in rel))
            time.sleep(2)

    for nome, url in IBGE.items():
        print("baixando", url, flush=True)
        baixar(url, RAW / "ibge" / nome, tentativas=10)

    if a.secao_uf:
        for uf in UFS:
            url = f"{CDN}/votacao_secao/votacao_secao_2026_{uf}.zip"
            print("baixando", url, flush=True)
            baixar(url, RAW / "2026" / "votacao_secao_uf" / f"votacao_secao_2026_{uf}.zip",
                   tentativas=40)
            time.sleep(2)


if __name__ == "__main__":
    main()
