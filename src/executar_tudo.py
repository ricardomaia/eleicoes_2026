"""Executa o pipeline completo, na ordem.

Uso (a partir de src/):
    python executar_tudo.py                 # tudo, inclusive downloads
    python executar_tudo.py --sem-download  # usa os arquivos já baixados
    python executar_tudo.py --so-auditoria  # só os scripts auditoria_*.py (exige as bases prontas)
    python executar_tudo.py --sem-download --com-auditoria   # análises + auditoria

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
# Auditoria metodológica (ver AUDITORIA_METODOLOGICA.md). Grava em resultados/auditoria/ e não
# altera os resultados originais. Tempo total aproximado com 20 núcleos: 3 a 4 horas (o Modelo B
# com cadeias longas é a parte lenta; as três priors podem rodar em paralelo).
ETAPAS_AUDITORIA = [
    ["auditoria_00_reproducao.py"],
    ["auditoria_01_identificacao.py"],
    ["auditoria_02_sintetico.py"],
    ["auditoria_03_estabilidade.py"],
    ["auditoria_04_bayes.py", "prior=neutra"],
    ["auditoria_04_bayes.py", "prior=fidelidade_alta"],
    ["auditoria_04_bayes.py", "prior=troca_alta"],
    ["auditoria_05_covariaveis.py"],
    ["auditoria_06_parte_todo.py"],
    ["auditoria_07_amapa.py"],
    ["auditoria_08_validacao_cruzada.py"],
    ["auditoria_09_legislativo_limites.py"],
    ["auditoria_10_figuras.py"],
]


def main():
    etapas = ETAPAS_ANALISE if "--sem-download" in sys.argv else ETAPAS_DOWNLOAD + ETAPAS_ANALISE
    if "--so-auditoria" in sys.argv:
        etapas = ETAPAS_AUDITORIA
    elif "--com-auditoria" in sys.argv:
        etapas = etapas + ETAPAS_AUDITORIA
    for e in etapas:
        print(">>>", " ".join(e), flush=True)
        subprocess.run([sys.executable, *e], check=True)
    subprocess.run([sys.executable, "-m", "pytest", "-q", "../tests"], check=True)


if __name__ == "__main__":
    main()
