# Auditoria estatística da transferência de votos — eleição presidencial de 2026

Código, dados derivados e relatório da investigação descrita em [`prompt.txt`](prompt.txt).

- **Painel interativo** (para o público geral): <https://ricardomaia.github.io/eleicoes_2026/>
- **Relatório técnico**: [`RELATORIO.md`](RELATORIO.md)

Análise estatística independente, sem vínculo com o TSE ou com partidos.

## Estrutura

| Pasta / arquivo | Conteúdo |
|---|---|
| `src/` | código Python, um script por etapa (ver ordem abaixo) |
| `tests/` | testes automatizados (`pytest`) e dois boletins de urna de exemplo |
| `resultados/tabelas/` | todas as tabelas geradas (CSV e JSON) |
| `resultados/figuras/` | mapas e gráficos (PNG) |
| `docs/` | painel interativo (GitHub Pages): `index.html`, `app.js`, `estilo.css`, e os dados `dados.js` e `mapa.js` gerados por `src/analise_10_dashboard.py` |
| `dados_derivados/` | bases municipais consolidadas (CSV) e indicadores do IBGE |
| `integridade/` | manifesto dos downloads (URL, data, tamanho, SHA-256) e verificações das bases |
| `requirements.txt` | versões exatas das bibliotecas usadas |

Os dados brutos (≈ 8 GB) **não** ficam nesta pasta, para não sincronizar
gigabytes com o Google Drive. Eles ficam em `~/dados-tse` (no Windows,
`C:\Users\<usuário>\dados-tse`), ou no diretório indicado pela variável de
ambiente `AUDITORIA_DADOS`. Subpastas: `raw/` (arquivos como baixados),
`interim/` (bases intermediárias em Parquet).

## Reprodução integral

```bash
python -m venv venv
venv/Scripts/python -m pip install -r requirements.txt   # Linux/macOS: venv/bin/python
cd src
../venv/Scripts/python executar_tudo.py                  # baixa tudo e roda tudo
../venv/Scripts/python executar_tudo.py --sem-download   # só as análises
```

`executar_tudo.py` termina rodando os testes. Para rodar só os testes:
`python -m pytest -q tests/` a partir da pasta do projeto.

### Ordem das etapas

| Script | O que faz |
|---|---|
| `baixar_dados_abertos.py` | arquivos do Portal de Dados Abertos do TSE (2026, 2022, 2018) e malha municipal do IBGE |
| `baixar_ibge.py` | indicadores municipais do Censo 2022 (API SIDRA) |
| `baixar_t2_divulgacao.py`, `processar_t2.py` | 2º turno de 2026 por município, do sistema de divulgação do TSE |
| `baixar_bu_t2_amostra.py` | boletins de urna do 2º turno de uma amostra de 50.821 seções (10% por UF) |
| `baixar_bu_t2_uf_completa.py AP` | boletins de todas as 1.914 seções do Amapá (ver relatório, seção IV) |
| `montar_base.py` | bases por seção e por município, com verificações de integridade |
| `analise_01_reconciliacao.py` | tabela nacional, conferência com documentos oficiais, limites aritméticos |
| `analise_02_mobilizacao.py` | comparecimento, válidos, brancos e nulos (Pergunta A, H3) |
| `analise_03_inferencia_ecologica.py` | Modelo A e teste de migração mínima (seção 7) |
| `analise_03b_sensibilidade.py` | Modelo A com quatro estratificações diferentes |
| `analise_03c_amapa.py` | Amapá com todas as seções (capital e interior) |
| `analise_04_bayes.py` | Modelo B (bayesiano hierárquico) com três priors |
| `analise_05_monte_carlo.py` | Modelo C (quatro famílias de cenários) |
| `analise_06_legislativo.py` | H4: Câmara e Senado × presidente |
| `analise_07_anomalias.py` | Modelo D: resíduos, I de Moran, modelo de urna |
| `analise_08_figuras.py` | mapas e gráficos |
| `analise_09_historico.py` | comparação normalizada 2018 × 2022 × 2026 |
| `analise_10_dashboard.py` | dados do painel interativo (`docs/`) |

### Resultados intermediários reaproveitados

`analise_03_inferencia_ecologica.py` grava cada bloco já calculado em
`interim/ei_bloco_<ano>_<nível>_<origens>.pkl` e o reaproveita numa nova
execução. Para recalcular tudo do zero, apague esses arquivos. As posteriores
do Modelo B ficam em `interim/bayes_<prior>.nc`; `python analise_04_bayes.py
recalcular` refaz os fluxos nacionais a partir delas sem novo MCMC.

### Sementes e parâmetros

Semente global `20261025` (`src/comum.py`); cada etapa deriva dela as suas.
Parâmetros de cada modelo ficam registrados em `resultados/tabelas/*parametros*.json`
e `04_bayes_diagnosticos.json`.

## Situação dos dados na data da execução (26/10/2026)

- 1º turno (04/10/2026): completo por seção no Portal de Dados Abertos.
- 2º turno (25/10/2026): aptos, comparecimento, brancos, nulos e válidos por
  seção já estavam no arquivo `detalhe_votacao_secao_2026` (atualizado em
  26/10, 12h35). A votação **por candidato** por seção ainda não estava em
  `votacao_secao_2026_BR.zip` (versão de 06/10). Por isso:
  - por município, usa-se o resultado oficial do sistema de divulgação do TSE
    (completo, conferido contra o detalhe por seção: zero divergências);
  - por seção, usa-se a amostra de 50.821 boletins de urna (conferidos contra
    o detalhe por seção: zero divergências).
  Quando o TSE publicar a votação por seção do 2º turno, `montar_base.py`
  passa a usá-la automaticamente (basta baixar de novo o arquivo e rodar
  `executar_tudo.py --sem-download`).

## Licença

Este repositório (relatório, código, tabelas, figuras e painel) está sob a
licença [Creative Commons Atribuição 4.0 Internacional (CC BY 4.0)](LICENSE):
qualquer pessoa pode copiar, adaptar e redistribuir o material, inclusive
para fins comerciais, desde que dê crédito ao autor, indique o link para este
repositório e informe se fez alterações.

Sugestão de citação: Maia, R. *Auditoria estatística da transferência de votos
entre os turnos da eleição presidencial de 2026*. 2026.
<https://github.com/ricardomaia/eleicoes_2026>.

Os dados de origem são do TSE (Portal de Dados Abertos, CC BY) e do IBGE.
