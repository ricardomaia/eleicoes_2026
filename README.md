# Auditoria estatística da transferência de votos — eleição presidencial de 2026

Código, dados derivados e relatório da investigação descrita em [`prompt.txt`](prompt.txt).

- **Painel interativo** (para o público geral): <https://ricardomaia.github.io/eleicoes_2026/>
- **Relatório técnico**: [`RELATORIO.md`](RELATORIO.md)
- **Auditoria metodológica** (revisão estatística, experimentos adversariais,
  identificabilidade): [`AUDITORIA_METODOLOGICA.md`](AUDITORIA_METODOLOGICA.md)

Análise estatística independente, sem vínculo com o TSE ou com partidos.

## Estrutura

| Pasta / arquivo | Conteúdo |
|---|---|
| `src/` | código Python, um script por etapa (ver ordem abaixo) |
| `tests/` | testes automatizados (`pytest`) e dois boletins de urna de exemplo |
| `resultados/tabelas/` | todas as tabelas geradas (CSV e JSON) |
| `resultados/figuras/` | mapas e gráficos (PNG) |
| `resultados/auditoria/` | tabelas e figuras da auditoria metodológica (`src/auditoria_*.py`); os resultados originais acima não são alterados |
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

### Auditoria metodológica

`python executar_tudo.py --so-auditoria` roda os scripts abaixo (exige as
bases de `interim/` prontas). Cada um grava em `resultados/auditoria/tabelas/`
com o prefixo do seu número. O documento [`AUDITORIA_METODOLOGICA.md`](AUDITORIA_METODOLOGICA.md)
explica o que cada um testa e o que mudou nas conclusões.

| Script | O que faz |
|---|---|
| `auditoria_00_reproducao.py` | recalcula o bloco principal do Modelo A sem o cache e compara com a tabela publicada |
| `auditoria_01_identificacao.py` | condicionamento, regressão de Goodman sem restrições (erro-padrão por município), conjuntos identificados por programação linear sob hipóteses S0–S4, fronteira de heterogeneidade |
| `auditoria_02_sintetico.py` | gerador de eleições sintéticas com transições individuais conhecidas; cenários A–F e Hσ; viés, RMSE, cobertura, falsos positivos/negativos do Modelo A |
| `auditoria_03_estabilidade.py` | múltiplas inicializações do EM, variância correta (φ), bootstrap de 1.000 réplicas por município e por seção, teste de teto em quatro granularidades |
| `auditoria_04_bayes.py` | Modelo B com 1.000 + 1.000 iterações por cadeia, correlações posteriores entre taxas |
| `auditoria_05_covariaveis.py` | modelos M1 (taxas dependentes da margem municipal) e M2 (preferência latente dos não votantes), com `ei_cov.py`; `python auditoria_05_covariaveis.py 10 100` ajusta por UF e faz o bootstrap de municípios (100 réplicas, 31 min com 10 processos; progresso gravado por UF em `interim/auditoria/` e retomado numa nova execução); com `0` no segundo argumento grava só as estimativas pontuais (`05_taxas_nacionais_por_modelo_sem_bootstrap.csv`, 1 min) |
| `auditoria_06_parte_todo.py` | correlação parte-todo entre Δválidos e ΔLula contra uma distribuição nula aritmética |
| `auditoria_07_amapa.py` | Amapá com todas as seções: bootstrap por conglomerado, M1/M2, perfil de troca migração × abstenção, influência, fronteira |
| `auditoria_08_validacao_cruzada.py` | validação cruzada agrupada por município (M0, M1, M2) e o mesmo em dados sintéticos equivalentes |
| `auditoria_09_legislativo_limites.py` | limites de Fréchet para o voto cruzado deputado federal × presidente |
| `auditoria_10_figuras.py` | figuras comparativas em `resultados/auditoria/figuras/` |

Testes dos métodos da auditoria: `tests/test_auditoria.py` (rodam sem os dados do TSE).

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

## Situação dos dados

- 1º turno (04/10/2026): completo por seção no Portal de Dados Abertos.
- 2º turno (25/10/2026): em 26/10 o arquivo `votacao_secao_2026_BR.zip` ainda
  estava na versão de 06/10 (só 1º turno). A primeira execução completa
  (26/10) usou, por município, o resultado oficial do sistema de divulgação e,
  por seção, uma amostra de 50.821 boletins de urna (10% por UF). Esses
  resultados estão preservados em `resultados/versao_amostra_bu/`.
- Em 27/10/2026 (00h50 em Brasília) o CDN do TSE passou a servir a versão de
  26/10 17h42 UTC do mesmo arquivo (241.891.087 bytes, SHA-256
  `c928321f63f2d095706fca73d4607c048d2ada23bda6876455d6911aaf1bc9c1`), com a
  votação por candidato nas 499.205 seções do 2º turno. Para obtê-la foi
  preciso pedir ao servidor sem cache (`Cache-Control: no-cache`): o pedido
  normal ainda devolvia a versão antiga. `montar_base.py` passou a usá-la, e
  a amostra de BUs ficou como conferência independente: zero divergências em
  aptos, comparecimento, brancos, nulos, Lula e Flávio nas 50.821 seções; a
  soma por município confere com o JSON de divulgação nos 5.757 municípios.
  Os resultados em `resultados/tabelas/` e no painel passaram a usar todas as
  seções. A versão antiga do arquivo fica guardada como
  `raw/2026/votacao_secao_2026_BR_versao_2026-10-06.zip`.
- Para as análises da auditoria por seção, a variável de ambiente
  `AUDITORIA_TODAS_SECOES=1` usa todas as seções (saídas com sufixo `_todas`);
  sem ela, a amostra de BUs (saídas sem sufixo, as citadas em
  `AUDITORIA_METODOLOGICA.md`).

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
