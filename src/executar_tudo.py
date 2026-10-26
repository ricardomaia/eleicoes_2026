"""Executa o pipeline completo, na ordem.

Uso (a partir de src/):
    python executar_tudo.py                 # tudo, inclusive downloads
    python executar_tudo.py --sem-download  # usa os arquivos já baixados

Tempo aproximado num computador de 20 núcleos: downloads ~1 h (a amostra de
BUs é a parte lenta), bases ~10 min, inferência ecológica ~1 h, Modelo B
~2–3 h, demais etapas ~20 min.
"""
from __future__ import annotations

import subprocess
import sys

ETAPAS_DOWNLOAD = [
    ["baixar_dados_abertos.py"],
    ["baixar_dados_abertos.py", "--anos", "2026", "--secao-uf"],
    ["baixar_ibge.py"],
    ["baixar_t2_divulgacao.py"],
    ["processar_t2.py"],
    ["baixar_bu_t2_amostra.py"],
    ["baixar_bu_t2_uf_completa.py", "AP"],
]
ETAPAS_ANALISE = [
    ["montar_base.py"],
    ["analise_01_reconciliacao.py"],
    ["analise_02_mobilizacao.py"],
    ["analise_03_inferencia_ecologica.py", "2026"],
    ["analise_03_inferencia_ecologica.py", "2022", "2018"],
    ["analise_03b_sensibilidade.py"],
    ["analise_03c_amapa.py"],
    ["analise_04_bayes.py", "n_max=4000", "tune=600", "draws=400"],
    ["analise_05_monte_carlo.py"],
    ["analise_06_legislativo.py"],
    ["analise_07_anomalias.py"],
    ["analise_08_figuras.py"],
    ["analise_09_historico.py"],
    ["analise_10_dashboard.py"],
]


def main():
    etapas = ETAPAS_ANALISE if "--sem-download" in sys.argv else ETAPAS_DOWNLOAD + ETAPAS_ANALISE
    for e in etapas:
        print(">>>", " ".join(e), flush=True)
        subprocess.run([sys.executable, *e], check=True)
    subprocess.run([sys.executable, "-m", "pytest", "-q", "../tests"], check=True)


if __name__ == "__main__":
    main()
