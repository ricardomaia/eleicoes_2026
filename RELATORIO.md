# Transferência de votos entre os turnos da eleição presidencial de 2026

**Relatório de auditoria estatística — versão de 26/10/2026**

Investigação pedida em [`prompt.txt`](prompt.txt). Painel interativo para o público geral: <https://ricardomaia.github.io/eleicoes_2026/>. Dados oficiais do TSE e do IBGE; código
e dados derivados nesta pasta (ver `README.md` para reprodução). Nenhum número
deste relatório foi estimado sem identificação: cada tabela diz se mostra
**dado oficial**, **estimativa** (com o modelo usado) ou **simulação**.

---

## I — Resumo executivo

**Resultado oficial.** No 1º turno (04/10) Flávio Bolsonaro teve 56.104.503
votos (47,04% dos válidos) e Lula 53.879.538 (45,16%). No 2º turno (25/10)
Lula teve 64.256.232 (51,78%) e Flávio 59.826.041 (48,22%). Lula ganhou
10.376.694 votos entre os turnos; Flávio ganhou 3.721.538.

**Integridade dos dados.** Todos os totais calculados a partir dos arquivos
por seção coincidem exatamente com os documentos oficiais (16 de 16
indicadores). Três publicações independentes do TSE — o detalhe por seção, o
resultado municipal do sistema de divulgação e 50.821 boletins de urna (BU)
individuais — coincidem entre si sem nenhuma divergência em aptos,
comparecimento, brancos, nulos e válidos. Nenhuma inconsistência verificável
foi encontrada.

**O que a aritmética, sozinha, determina.**
- O crescimento de Lula (10,38 milhões) é **maior** que todos os votos dos
  candidatos eliminados juntos (9,32 milhões). Mesmo que Lula tivesse
  recebido todos eles, pelo menos 1,06 milhão de votos dele no 2º turno
  vieram de outras origens: eleitores de Flávio, eleitores que votaram em
  branco ou nulo, ou eleitores que se abstiveram no 1º turno. Somando
  município por município, esse mínimo sobe para 1,84 milhão.
- Pelo menos 5,04 milhões de votos válidos do 2º turno vieram de pessoas que
  não deram voto válido no 1º turno (5,29 milhões somando seção por seção).
- A aritmética **não** obriga nenhuma migração direta de eleitores de Flávio
  para Lula: uma migração zero é aritmeticamente possível em todos os
  municípios e em 50.819 das 50.821 seções da amostra (nas outras duas, o
  mínimo obrigatório soma 4 eleitores). Os limites aritméticos da taxa
  Flávio→Lula vão de 0% a 81% — largos demais para decidir a questão.

**O que os modelos estatísticos estimam** (inferência ecológica; ver
limitações). Taxas nacionais, Modelo A, amostra de seções, intervalo de 95%:

| Origem no 1º turno | → Lula | → Flávio | → branco/nulo | → abstenção |
|---|---:|---:|---:|---:|
| Lula | 98,5% | 0,0% | 0,3% | 1,1% |
| Flávio | **0,20%** (0,12–0,32) | 98,4% | 0,5% | 0,9% |
| Outros candidatos | 42,4% | 38,9% | 13,5% | 5,2% |
| Brancos e nulos | **60,8%** (57,1–61,3) | 1,5% | 37,1% | 0,6% |
| Abstenção | **10,2%** (9,8–10,6) | 2,7% | 0,7% | 86,4% |

Em votos: dos 64,26 milhões de Lula no 2º turno, o modelo atribui 53,09
milhões a quem já votava nele, 3,95 milhões a eleitores dos demais
candidatos, 3,63 milhões a quem votou em branco ou nulo, 3,41 milhões a quem
se absteve e 0,11 milhão (intervalo 0,07–0,18) a eleitores de Flávio.

**Conclusões principais.**
1. O resultado é explicável **sem migração relevante de eleitores de Flávio
   para Lula** (taxa estimada entre 0,02% e 0,8% em todos os modelos, priors e
   estratificações testados), desde que se aceite que eleitores que votaram
   em branco ou nulo ou se abstiveram no 1º turno se mobilizaram muito mais
   a favor de Lula do que de Flávio.
2. Essa **mobilização assimétrica é a característica estatística mais
   incomum de 2026** em relação a 2018 e 2022: os votos válidos cresceram 3,0
   por 100 aptos entre os turnos (2022: +0,2; 2018: −1,5) e os brancos e nulos
   caíram em todo o país (no total nacional de 2022 e 2018 subiram). Ela é compatível com
   explicações comportamentais (ver seção VII), mas os dados agregados não
   identificam quem mudou de comportamento.
3. A única incompatibilidade estatística localizada com a hipótese "migração
   zero" está em **Macapá e Santana (AP)**: com todas as 1.914 seções do
   estado, o modelo estima 7,9% de migração Flávio→Lula nessas duas cidades
   (cerca de 12,7 mil votos; a margem nacional de Lula foi de 4,43 milhões). O
   mesmo ajuste estima 18% de abstenção entre eleitores de Lula e 0% entre os
   de Flávio, o que indica que o modelo está trocando migração por abstenção
   diferencial; as duas explicações não são distinguíveis com dados
   agregados.
4. A distribuição dos resíduos, a autocorrelação espacial e a ausência de
   efeito do modelo de urna estão dentro do observado em 2018 e 2022.

**Nível de confiança.** Alto para os resultados aritméticos e de integridade
(não dependem de modelo). Moderado para as taxas de transição: os quatro
modelos concordam, mas todos dependem de hipóteses de inferência ecológica
que não podem ser verificadas com dados agregados (seção VIII).

---

## II — Reconciliação dos votos

### Tabela nacional reconciliada (dado oficial)

| Indicador | 1º turno | 2º turno | Diferença |
|---|---:|---:|---:|
| Lula | 53.879.538 | 64.256.232 | +10.376.694 |
| Flávio Bolsonaro | 56.104.503 | 59.826.041 | +3.721.538 |
| Outros candidatos | 9.316.747 | — | −9.316.747 |
| Votos válidos | 119.300.788 | 124.082.273 | +4.781.485 |
| Votos brancos | 2.300.798 | 1.430.496 | −870.302 |
| Votos nulos¹ | 3.674.249 | 2.723.305 | −950.944 |
| Abstenções² | 33.469.667 | 30.509.428 | −2.960.239 |
| Comparecimento | 125.275.835 | 128.236.074 | +2.960.239 |
| Eleitores aptos³ | 158.745.502 | 158.745.502 | 0 |

¹ Inclui 5.246 nulos técnicos do 1º turno (votos ao nº 28, candidatura não
validada), como no relatório oficial.
² Calculadas como aptos − comparecimento. O relatório do TSE informa
33.469.244 no 1º turno porque exclui os 423 aptos das 41 seções não
instaladas; a diferença é exatamente essa.
³ Inclui 39 registros duplicados por transferência temporária, conforme nota
do TSE no conjunto de dados (eleitorado efetivo: 158.745.463).

Fontes: 1º turno — `votacao_secao_2026_BR.csv` e `detalhe_votacao_secao_2026_BR.csv`,
conferidos com o Relatório Resultado da Totalização (SISTOT, 07/10/2026). 2º
turno — `detalhe_votacao_secao_2026` (atualizado em 26/10, 12h35) e JSON do
sistema de divulgação (`br-c0001-e006258-u.json`, totalização final de
25/10, 23h26). O relatório PDF do 2º turno ainda não estava publicado.
Tabelas: `01_reconciliacao_nacional.csv`, `01_conferencia_oficial.csv`.

### Identidades verificadas (todas exatas)

- Lula + Flávio + outros = válidos (1º turno); Lula + Flávio = válidos (2º).
- Válidos + brancos + nulos = comparecimento; comparecimento + abstenção = aptos
  (nos dois turnos, em cada uma das 499.248 seções).
- **ΔLula + ΔFlávio = votos dos eliminados + Δválidos**:
  14.098.232 = 9.316.747 + 4.781.485.
- Δválidos = −Δ(brancos+nulos) − Δabstenção: 4.781.485 = 1.821.246 + 2.960.239.

### Limites aritméticos (antes de qualquer modelo)

Para cada unidade territorial, o número de eleitores que foi de uma origem *r*
(1º turno) para um destino *c* (2º turno) fica entre máx(0, R + C − N) e
mín(R, C), onde R e C são os totais da origem e do destino e N o eleitorado
(limites de Fréchet / Duncan-Davis). Somando unidade por unidade:

| Quantidade obrigada pela aritmética | Nacional | Por UF | Por município | Por seção |
|---|---:|---:|---:|---:|
| Votos de Lula no 2T que não vêm de Lula(1T) nem dos eliminados | 1.059.947 | 1.643.269 | 1.837.161 | (amostra) |
| Idem para Flávio | 0 | 0 | 8.085 | (amostra) |
| Válidos do 2T sem origem em válidos do 1T | 4.781.485 | 4.953.208 | 5.040.414 | 5.287.816 |
| Comparecimento do 2T sem origem no comparecimento do 1T | 2.960.239 | 3.231.747 | 3.339.994 | 3.622.948 |
| Migração mínima Flávio(1T)→Lula(2T) | 0 | 0 | 0 | 4 eleitores (amostra) |
| Migração mínima Lula(1T)→Flávio(2T) | 0 | 0 | 0 | 0 |

Intervalos de identificação das taxas de troca direta (limites de Fréchet
somados por município): Flávio→Lula entre 0% e 80,6%; Lula→Flávio entre 0% e
76,5%. **Conclusão imposta pela aritmética:** os eliminados não bastam para o
crescimento de Lula; houve entrada líquida de pelo menos 5 milhões de novos
votos válidos; a migração direta entre finalistas não é determinada.
Tabelas: `01_limites_*.csv`, `01_quantidades_minimas.csv`.

---

## III — Mobilização eleitoral (Pergunta A, H3)

### Onde mudaram comparecimento e votos válidos (dado oficial)

O comparecimento subiu 1,86 ponto percentual (78,92% → 80,78%) e os válidos
3,0 por 100 aptos. O aumento foi geral, com exceções no Norte:

| UFs com maior aumento do comparecimento | p.p. | | UFs com queda | p.p. |
|---|---:|---|---|---:|
| BA | +3,26 | | AP | −8,06 |
| PE | +2,98 | | RR | −6,02 |
| SP | +2,73 | | AC | −5,65 |
| MS | +2,63 | | AM | −1,52 |
| PR | +2,53 | | PA | −1,22 |

Ranking completo: `02_ranking_uf_comparecimento_validos.csv`, figura
`ranking_uf_comparecimento_validos.png`. Só AC, DF e TO tiveram 2º turno para
governador; no AP e em RR não havia disputa local no 2º turno, o que é um
fator conhecido de queda de comparecimento.

### Os novos válidos concentraram-se onde Lula já liderava?

Seções agrupadas pela margem Lula − Flávio no 1º turno (dado oficial; 499 mil
seções):

| Faixa (margem no 1T) | % dos aptos | % do aumento nacional de válidos | Δválidos por 100 aptos | Δcomparecimento por 100 aptos | Δ(brancos+nulos) por 100 aptos |
|---|---:|---:|---:|---:|---:|
| Flávio ≥ +20 pp | 32,8 | 26,4 | 2,42 | 1,72 | −0,69 |
| Flávio +10 a +20 | 12,8 | 12,0 | 2,82 | 1,88 | −0,94 |
| Flávio 0 a +10 | 11,6 | 12,0 | 3,09 | 1,95 | −1,14 |
| Lula 0 a +10 | 9,3 | 10,5 | 3,37 | 2,03 | −1,34 |
| Lula +10 a +20 | 8,4 | 10,1 | 3,61 | 2,09 | −1,51 |
| Lula ≥ +20 pp | 25,1 | 29,1 | 3,48 | 1,81 | −1,68 |

- O aumento de válidos ocorreu **em todas as faixas**, com inclinação
  moderada para áreas favoráveis a Lula.
- O **comparecimento** subiu de forma quase igual em todas as faixas (1,7 a
  2,1 por 100 aptos). A diferença entre faixas vem da **queda de brancos e
  nulos**, maior onde Lula era forte (−1,68 contra −0,69).
- Correlação ponderada entre a votação de Lula no 1º turno e Δválidos: 0,13
  (seção), 0,11 (município). Com Flávio: −0,13 e −0,14. Correlações fracas.
- Regressão com efeitos fixos de UF, taxa de brancos/nulos e abstenção do 1º
  turno e controles do Censo 2022 (população, urbanização, alfabetização,
  renda, cor/raça): o coeficiente da votação de Lula no 1º turno fica entre
  0,007 e 0,011 (Δválidos por apto por unidade de participação) em seção,
  zona e município — praticamente nulo. O preditor dominante é a taxa de
  brancos e nulos do 1º turno (coeficiente 0,59 a 0,70). Tabela `02_regressoes.csv`.
- Sensibilidade à agregação: os sinais e magnitudes se mantêm em seção (497
  mil), zona (6,1 mil), município (5,6 mil); na UF (27) os coeficientes têm
  intervalos largos.

**Comparação histórica** (mesmo cálculo): em 2022 os válidos cresceram
sobretudo em áreas favoráveis a Jair Bolsonaro (77% do aumento líquido nas
seções onde ele tinha ≥ 20 pp de vantagem) e caíram nas áreas de Lula; em
2018, idem para Jair Bolsonaro. Em 2026 o padrão foi distribuído, com
inclinação para o finalista que estava atrás no 1º turno.

### Associação entre mobilização e crescimento de cada candidato (H3)

Por município (5.571; dado oficial, associação descritiva):
- correlação ponderada entre Δválidos e ΔLula: 0,78; entre Δválidos e ΔFlávio: 0,45;
- em regressão com controles, cada voto válido adicional por apto associa-se a
  +0,67 voto de Lula (IC 95%: 0,63–0,70) e +0,29 de Flávio (0,26–0,33);
- correlação entre Δ(brancos+nulos) e ΔLula: −0,40.

Lembrete: essas associações entre agregados **não** mostram que os novos
votos válidos vieram de quem se absteve ou anulou. Uma seção sem variação
líquida de comparecimento pode ter muitas pessoas que só votaram em um dos
turnos.

---

## IV — Transferências estimadas (Pergunta B, H1, H2, seção 7)

### Modelos

- **Modelo A** (`analise_03`): inferência ecológica R×C por
  quase-verossimilhança multinomial, uma matriz por UF (taxas ≥ 0, linhas
  somando 1), estimada pelo algoritmo EM acelerado; intervalos por bootstrap
  de municípios (200 réplicas). Unidades: amostra aleatória de 50.821 seções
  (10% por UF, mínimo 400) com o BU do 2º turno; sensibilidade em nível de
  município (todos). Mudanças de cadastro entre turnos (74.692 aptos em 55.722
  seções, por transferências temporárias) entram como abstenção.
- **Modelo B** (`analise_04`): bayesiano hierárquico (PyMC): efeito aleatório
  de UF em cada taxa, efeitos da urbanização municipal e da margem municipal
  do 1º turno, verossimilhança Dirichlet-multinomial. Três priors; 4.000
  seções; 4 cadeias × 400 sorteios.
- **Sensibilidade do Modelo A** (`analise_03b`): estratos região × faixa de
  margem; UF × tercil de urbanização; matriz própria para municípios grandes.

### H1 — Fidelidade

| Taxa nacional 2026 | Modelo A (seção) | Modelo A (município) | Modelo B prior neutra | Modelo B fidelidade alta | Modelo B troca alta |
|---|---:|---:|---:|---:|---:|
| Lula → Lula | 98,5% | 98,7% | 99,1% | 98,8% | 98,7% |
| Flávio → Flávio | 98,4% | 98,6% | 97,7% | 97,6% | 97,5% |
| Flávio → Lula | 0,20% | 0,11% | 0,23% | 0,42% | 0,76% |
| (IC 95%) | 0,12–0,32 | 0,09–0,32 | 0,03–0,57 | 0,19–0,71 | 0,49–1,13 |
| Lula → Flávio | 0,00% | 0,00% | 0,03% | 0,09% | 0,22% |
| Flávio → abstenção | 0,9% | 0,9% | 1,7% | 1,6% | 1,4% |
| Lula → abstenção | 1,1% | 1,2% | 0,8% | 0,9% | 0,8% |

Sensibilidade do Modelo A à definição dos estratos (taxas nacionais 2026;
`03b_sensibilidade_estratos.csv`):

| Estratificação | nº de matrizes | Flávio→Lula | Brancos/nulos→Lula | Abstenção→Lula | Outros→Lula |
|---|---:|---:|---:|---:|---:|
| UF (principal) | 27 | 0,20% | 60,9% | 10,3% | 42,4% |
| Região × faixa de margem no 1T | 15 | 0,02% | 60,1% | 10,3% | 42,7% |
| UF × tercil de urbanização | 77 | 0,16% | 59,1% | 10,7% | 40,3% |
| Município grande (≥ 60 seções na amostra) ou UF | 135 | 0,31% | 57,1% | 11,2% | 40,9% |

A última linha usa apenas variação **dentro** de municípios grandes; mesmo
assim a taxa brancos/nulos→Lula fica em 57%, o que indica que ela não resulta
de misturar regiões diferentes. Para comparação, em 2022 a mesma taxa ficou
entre 11% e 18% nas quatro estratificações.

A prior "troca alta" foi centrada em 15% de troca direta nos dois sentidos; a
posterior ficou em 0,76%. Os dados, e não a prior, determinam a ordem de
grandeza. **H1 — sustentada**: fidelidade de ~98% aos dois finalistas, troca
direta inferior a 1%.

### H2 — Candidatos eliminados

| Eliminado (votos no 1T) | → Lula | → Flávio | → branco/nulo | → abstenção |
|---|---:|---:|---:|---:|
| Augusto Cury (3.448.569) | 54% (52–56) | 29% (26–30) | 13% | 5% |
| Renan Santos (2.675.887) | 40% (38–42) | 35% (33–36) | 16% | 9% |
| Ronaldo Caiado (2.605.148) | 32% (29–35) | 53% (50–54) | 12% | 3% |
| Zema e demais (587.143) | 27% (22–30) | 55% (50–58) | 12% | 6% |

(Modelo A, seção; em nível de município as estimativas individualizadas têm
intervalos mais largos — `03_matriz_transicao_nacional_2026.csv`.) Em
conjunto, os eliminados deram cerca de 3,9 milhões de votos a Lula e 3,6
milhões a Flávio. **H2 — sustentada**: a transferência dos eliminados
explica parte do crescimento dos dois finalistas, mas não basta para o de
Lula (aritmética, seção II).

### Seção 7 — teste de migração mínima Flávio→Lula

Impõe-se em todas as UFs um teto *c* para a taxa e mede-se quanto o ajuste
piora (teste F de quase-verossimilhança somado nas UFs).

| Teto Flávio→Lula | Viável aritmeticamente? | p conjunto (seções) | UFs que rejeitam a 5% | com Bonferroni | p conjunto (municípios) |
|---|---|---:|---:|---:|---:|
| 0% | sim (exceto 2 seções, 4 eleitores) | < 0,0001 | AP, AM, MA, CE | AP | 0,82 |
| ≤ 1% | sim | < 0,0001 | AP | AP | 0,68 |
| ≤ 2% | sim | < 0,0001 | AP | AP | 0,41 |
| ≤ 5% | sim | 0,0009 | AP | AP | 1,00 |
| ≤ 10% | sim | 1,00 | — | — | 1,00 |

No sentido inverso (Lula→Flávio), nenhum teto é rejeitado em nenhum nível.

- **Fluxos necessários dos outros grupos com teto 0%**: praticamente os
  mesmos do modelo livre (a migração livre estimada já é de 0,2%), isto é,
  ~3,9 milhões dos eliminados, ~3,6 milhões de brancos/nulos e ~3,4
  milhões de abstencionistas para Lula. Tabela `03_testes_migracao_por_uf_2026.csv`
  (colunas `fluxo_*`).
- **Região de maior incompatibilidade: Amapá.** Com as 1.914 seções do estado
  (`03c_amapa_todas_secoes.csv`): no interior (613 seções) a migração zero
  ajusta perfeitamente (p ≈ 1,0); em Macapá e Santana (1.301 seções) o modelo
  estima 7,9% (IC 6,2–9,2%) e rejeita tetos até 5%. Fora do AP, a soma dos
  testes da hipótese 0% dá χ² = 25,3 com 16 graus de liberdade (p = 0,065):
  não rejeita a migração nula a 5%, mas por margem pequena. AM, MA e CE
  rejeitam isoladamente a 5% (taxas livres de 1,5% a 2,0%), mas não depois da
  correção de Bonferroni; com teto de 1%, nenhuma UF além do AP rejeita.
- **Dependência dos pressupostos:** o resultado nacional (0,1% a 0,8%) se
  mantém nas quatro estratificações do Modelo A e nas três priors do Modelo B.
  Ele depende da hipótese de que, dentro de cada estrato, as taxas não variam
  sistematicamente junto com a composição do 1º turno.
- **Identificabilidade:** a aritmética não distingue "0% de migração" de "até
  80%"; os modelos distinguem graças à variação entre seções. Se essa
  variação for produzida por fatores não modelados, as duas hipóteses voltam
  a ser não identificáveis.
- **Comparação**: em 2022 (Jair Bolsonaro e Lula) e em 2018 (Jair Bolsonaro e
  Haddad) a migração estimada entre finalistas também foi ≈ 0%, sem rejeição
  do teto 0% em nenhum nível (em 2018 o sentido Haddad→Bolsonaro foi
  rejeitado em SC e BA no nível municipal).

### Modelo C — simulação de Monte Carlo (20.000 sorteios por família)

Cada sorteio foi ajustado (raking) para reproduzir exatamente os totais
nacionais oficiais; mede-se então o ajuste aos 5.757 municípios.
(`05_monte_carlo_resumo.csv`, figura `monte_carlo_familias.png`.)

| Família | Erro do sorteio bruto no total de Lula (mediana, p.p. dos aptos) | Deviance por 1.000 eleitores (mediana) | Fração com ajuste até 10% acima do melhor ajuste de matriz única | Flávio→Lula após calibração (mediana; 5–95%) |
|---|---:|---:|---:|---|
| C1 Fidelidade alta, transferência dos eliminados | −4,8 | 4,4 | 0,01% | 1,8% (0,6–4,5) |
| C2 Fidelidade alta + mobilização | −3,5 | 5,1 | 0,01% | 1,7% (0,5–4,6) |
| C3 Transferências moderadas (~6%) | −4,7 | 8,3 | 0% | 7,8% (3,8–13,3) |
| C4 Heterogeneidade regional | −4,2 | 4,0 | 36% | 4,8% (0,1–14,4) |

Leitura: (a) nenhuma família, sem calibração, reproduz o total de Lula — todas
o subestimam em 3,5 a 4,8 p.p. dos aptos (5,5 a 7,6 milhões de votos), porque
nenhuma supôs mobilização assimétrica a favor de Lula; a calibração
aritmética impõe essa assimetria. (b) A família de trocas moderadas em todo o
país (C3) tem o pior ajuste territorial e nenhum sorteio próximo do melhor
ajuste. (c) Permitir matrizes diferentes por região (C4) melhora o ajuste. As
frações dependem da largura arbitrária de cada família e **não** são
probabilidades das hipóteses. Estabilidade: 4 lotes independentes, R-hat entre
lotes 0,9999–1,0002, erro-padrão de Monte Carlo das médias < 0,0003.

---

## V — Coerência legislativa e presidencial (H4)

### Votos e cadeiras (dado oficial)

| Partido | Votos p/ deputado federal | % | Cadeiras na Câmara | % | Senado: % votos | cadeiras |
|---|---:|---:|---:|---:|---:|---:|
| PL | 25.824.755 | 22,7 | 121 | 23,6 | 28,2 | 19 de 54 |
| PT | 14.788.038 | 13,0 | 70 | 13,6 | 13,2 | 6 |
| PSD | 9.391.321 | 8,3 | 43 | 8,4 | 5,1 | 2 |
| Republicanos | 7.911.780 | 7,0 | 41 | 8,0 | 4,3 | 2 |
| MDB | 7.890.384 | 6,9 | 36 | 7,0 | 5,7 | 7 |
| União | 7.858.039 | 6,9 | 46 | 9,0 | 3,8 | 3 |
| PP | 7.611.922 | 6,7 | 41 | 8,0 | 10,6 | 3 |

Tabela completa: `06_votos_cadeiras_partidos.csv`. O Senado é eleito por
maioria simples (duas vagas por UF em 2026), por isso cadeiras e votos
divergem mais que na Câmara (proporcional, com federações).

Por bloco (classificação descrita em `analise_06_legislativo.py`; partidos de
centro não são tratados como direita), votos para deputado federal: direita
47,0% (direita estrita PL+PP+União+Republicanos+Novo: 45,8%), centro 26,7%,
esquerda 26,3%.

### Voto dividido

- Flávio teve 47,0% dos válidos; o PL, 22,7% dos válidos para deputado. A
  razão entre os dois (2,07) é **menor** que em 2022 (Jair Bolsonaro 43,2% ×
  PL 16,6% = 2,60) e em 2018 (Jair Bolsonaro 46,0% × PSL 11,6% = 3,95). Em
  2026 o voto presidencial de direita esteve mais alinhado ao voto no partido
  do candidato do que nas duas eleições anteriores.
- Correlação ponderada por seção entre PL (deputado) e Flávio (presidente):
  0,53; entre PL e Lula: −0,53. Por município, a correlação entre o partido
  do candidato de direita e o candidato foi 0,53 em 2026, 0,36 em 2022 (PL ×
  Jair Bolsonaro) e 0,68 em 2018 (PSL × Jair Bolsonaro).
- Seções com PL ≥ 30% para deputado **e** Lula ≥ 50% no 1º turno: 17.048
  (3,4%; 3,3% dos aptos). Com PL ≥ 40% e Lula ≥ 60%: 3.222 (0,6%).
- Inferência ecológica (mesmo estimador do Modelo A, todas as seções no 1º
  turno; amostra no 2º): dos eleitores do PL para deputado, 87% votaram em
  Flávio e 5,4% (4,6–7,6) em Lula no 1º turno; no 2º turno, 92% em Flávio e
  5,0% (3,9–8,5) em Lula. Eleitores de outros partidos de direita: 37% Lula
  no 2º turno; de centro: 50%; da federação do PT: 91%.

**H4 — sustentada** no sentido de que há divergência entre voto legislativo e
presidencial, e ela é **consistente com voto dividido** de magnitude comum no
Brasil (menor que em 2018 e 2022). A divergência não indica incoerência dos
dados.

Observação de dados: em 17.233 seções o número de votos para deputado é
menor que o comparecimento (nunca maior; diferença total de 165.584, 0,13%).
O padrão é compatível com eleitores em trânsito fora da sua UF, que votam só
para presidente; esta explicação não foi verificada com o cadastro de
trânsito.

---

## VI — Resultados dos testes estatísticos

| Teste | Resultado | Onde |
|---|---|---|
| Totais calculados × oficiais | 16/16 idênticos | `01_conferencia_oficial.csv` |
| BU (50.821) × detalhe por seção | 0 divergências em 5 campos | `integridade/verificacoes_base_2026.json` |
| Divulgação municipal (5.757) × detalhe por seção | 0 divergências | idem |
| Recuperação de matriz conhecida (dados sintéticos) | erro máx. < 0,03; teste detecta teto falso (p < 10⁻⁶) | `tests/` (11 testes, todos passam) |
| Modelo A: sobredispersão φ por UF (seção) | mediana ≈ 1,1; AP 1,8 | `03_matriz_transicao_por_uf_2026.csv` |
| Modelo A: total previsto de Lula | 64,19 mi × 64,26 mi observados (−0,1%) | idem |
| Modelo B: convergência | 0 divergências; R-hat máx. 1,011 (neutra), 1,019 (fidelidade), 1,042 (troca alta); ESS mín. 121–253 | `04_bayes_diagnosticos.json` |
| Modelo B: verificação preditiva | intervalo de 90% cobre 96–97% das seções; p preditivo dos totais 0,17–0,71; DP da participação de Lula reproduzido (p = 0,52–0,62) | idem |
| Monte Carlo: estabilidade | R-hat entre lotes ≤ 1,0002 | `05_monte_carlo_estabilidade.csv` |

Ressalvas: o R-hat de 1,042 da prior "troca alta" está acima do limite usual
de 1,01; as conclusões não dependem dela (as outras duas priors convergiram
melhor e dão taxas Flávio→Lula menores). O Modelo B usou 4.000 seções, e não
as 50.821, por custo computacional (cada prior levou 10 a 24 minutos).

---

## VII — Anomalias e explicações concorrentes (H5)

### Resíduos (Modelo D)

Resíduo de cada unidade = votos observados de Lula no 2º turno − esperado pela
matriz da UF, padronizado pela variância de amostragem **mais** a variação
entre lugares não explicada pelo modelo (que não diminui com o tamanho da
unidade); correção de Benjamini-Hochberg para múltiplas comparações.

| | 2026 | 2022 | 2018 |
|---|---:|---:|---:|
| Municípios com resíduo robusto \|z\| > 3 | 0,9% | 1,2% | 1,2% |
| Municípios sinalizados (q < 0,05) | 12 | 26 | 11 |
| ... dos quais com o finalista do PT **abaixo** do esperado | 10 | 18 | 4 |
| Seções (amostra) com \|z\| > 3 | 0,8% | 0,7% | 0,8% |
| I de Moran dos resíduos municipais (p por permutação) | 0,34 (0,001) | 0,28 (0,001) | 0,38 (0,001) |
| Efeito do modelo de urna (dentro do município) | nenhum (p 0,41–0,76) | UE2011 p = 0,012, UE2020 p = 0,062 | — |

Municípios sinalizados em 2026 (`07_maiores_residuos_municipios_2026.csv`):
Brasília (DF), Belo Monte (AL), Santo Antônio de Lisboa (PI), Fernando de
Noronha (PE), Bagre (PA), São João (PE), Mangaratiba (RJ), Miguel Leão (PI),
Galinhos (RN), Inácio Martins (PR), Primeira Cruz (MA), Santo Amaro do
Maranhão (MA).
- Brasília: o DF é um único município; no nível municipal recebe a matriz da
  região Centro-Oeste, e o DF teve 2º turno para governador. É um erro de
  especificação do modelo municipal, não uma anomalia dos dados (no nível de
  seção o DF tem matriz própria).
- Os outros 11 são municípios pequenos; 10 têm Lula **abaixo** do esperado, e
  esses mesmos 10 tiveram queda de comparecimento entre 3 e 13 pontos (ex.:
  Primeira Cruz, −12,6 p.p.), situação em que a hipótese de taxas constantes
  na UF funciona mal. O único com Lula acima do esperado (São João, PE) teve
  aumento de 7,9 pontos no comparecimento.
- Seções com variação de comparecimento acima de 20 p.p.: 300 (0,06%); 41
  delas tiveram mudança de aptos entre turnos (transferência temporária).

### Anomalias estatísticas identificadas e explicações possíveis

| Observação | Magnitude | Explicações compatíveis | Inconsistência verificável? |
|---|---|---|---|
| Mobilização assimétrica: brancos/nulos e abstencionistas do 1T com destino majoritário em Lula | ~7 milhões de votos (3,6 de brancos/nulos, 3,4 de abstenção) | (1) mobilização da campanha de Lula, que estava atrás; (2) eleitores de esquerda que anularam ou não votaram no 1T (já há precedente em 2018: brancos e nulos caíram nos redutos do PT entre os turnos); (3) viés de agregação da inferência ecológica (reduzido, mas não eliminado, pelas estratificações); (4) migração direta não captada pelos modelos | Não |
| Macapá e Santana (AP): ajuste melhor com 7,9% de migração Flávio→Lula | ~12,7 mil votos | abstenção diferencial não modelada; realinhamento político local; migração real | Não (BU = detalhe em todas as 1.914 seções) |
| Resíduos espacialmente agrupados | I de Moran 0,34 | fatores regionais não modelados (presente também em 2018 e 2022) | Não |
| 12 municípios com resíduo atípico | 0,2% dos municípios | quedas fortes de comparecimento; erro de especificação (DF) | Não |

Nenhuma dessas observações, isolada ou em conjunto, constitui evidência de
fraude: elas são padrões estatísticos incomuns, de magnitude pequena (AP) ou
com explicações comportamentais plausíveis (mobilização), sem inconsistência
nos registros oficiais.

**Lei de Benford não foi usada.** A distribuição de dígitos das contagens por
seção depende do tamanho das seções (limitado por lei) e da participação de
cada candidato, de modo que desvios ocorrem em eleições sem irregularidade
(Deckert, Myagkov e Ordeshook, 2011).

---

## VIII — Limitações

1. **Inferência ecológica.** Todas as taxas de transição são estimadas a
   partir de contagens agregadas. O sigilo do voto impede saber o que cada
   eleitor fez nos dois turnos. As estimativas dependem da hipótese de que,
   dentro de cada estrato (UF, região × faixa, etc.), as taxas não variam de
   forma sistemática com a composição do 1º turno. Se variarem, as
   estimativas são viesadas, e os intervalos de bootstrap não incluem esse
   erro.
2. **Não identificação.** Há combinações diferentes de taxas que produzem
   quase o mesmo ajuste (visto no AP: migração × abstenção diferencial). A
   aritmética sozinha permite migração Flávio→Lula de 0% a 81%.
3. **Dados do 2º turno por candidato e por seção.** Em 26/10/2026 o TSE ainda
   não tinha publicado o arquivo `votacao_secao` do 2º turno. Usou-se uma
   amostra aleatória de 50.821 BUs (10%; todas as seções no AP) e, por
   município, o resultado completo do sistema de divulgação. Os limites
   aritméticos por seção e o Modelo A por seção valem para a amostra; o
   pipeline passa a usar o arquivo completo quando for publicado.
4. **Fonte do 2º turno.** O sistema de divulgação é oficial (totalização final
   "tf: s"), mas os arquivos consolidados do Portal de Dados Abertos e o
   relatório PDF do 2º turno ainda não existiam; podem ocorrer ajustes
   posteriores (recursos, seções anuladas).
5. **Modelo B** rodou com 4.000 seções e cadeias curtas por custo
   computacional; uma prior teve R-hat 1,042.
6. **Covariáveis** são municipais (Censo 2022) e aplicadas a todas as seções
   do município; Boa Esperança do Norte (MT), criado depois do Censo, não tem
   covariáveis.
7. **Classificação partidária** em blocos é uma escolha deste estudo; os
   resultados principais usam PL e a federação do PT isoladamente.
8. **Eleitores em trânsito e transferências temporárias**: tratados como
   entrada/saída de cadastro (≈ 0,05% do eleitorado); a explicação para as
   17.233 seções com menos votos para deputado do que comparecimento não foi
   verificada com o cadastro de trânsito.

---

## IX — Conclusões

**Pergunta 1. O aumento de votos válidos ocorreu predominantemente em áreas
favoráveis a Lula, a Flávio ou de forma distribuída?**
De forma distribuída, com inclinação moderada para áreas favoráveis a Lula
(25% dos aptos e 29% do aumento nas áreas com Lula ≥ +20 p.p.; 33% e 26% nas
de Flávio ≥ +20 p.p.). A inclinação vem da queda maior de brancos e nulos
nessas áreas; o comparecimento cresceu de forma parecida em todas. Com
controles, o efeito da votação inicial de Lula é praticamente nulo.
*Hipótese "concentrou-se nas áreas de Lula": **parcialmente sustentada**.*

**Pergunta 2. Os votos dos eliminados são suficientes para explicar o
crescimento dos finalistas? Quais transferências são compatíveis?**
Não são suficientes: o crescimento combinado (14,1 milhões) é igual aos votos
dos eliminados (9,3 milhões) mais o aumento líquido de válidos (4,8 milhões),
e o crescimento de Lula sozinho supera os eliminados em 1,06 milhão. São
compatíveis com os dados territoriais: eliminados divididos entre Lula (~42%)
e Flávio (~39%), com Cury e Renan Santos mais para Lula e Caiado e Zema mais
para Flávio; brancos/nulos e abstencionistas do 1º turno indo
majoritariamente para Lula.
*"Eliminados bastam": **não sustentada pelos dados disponíveis**
(aritmética). "Eliminados + mobilização explicam o resultado": **sustentada**.*

**Pergunta 3. É possível explicar o resultado sem migração significativa de
Flávio para Lula? Sob quais premissas?**
Sim. Todos os modelos estimam migração entre 0,02% e 0,8% (≈ 10 mil a 430 mil
eleitores), e uma migração nacional moderada (≥ 5%) ajusta pior a
distribuição territorial (Monte Carlo C3; teste da seção 7 em nível
municipal). Premissas: (a) as taxas de transição são aproximadamente
constantes dentro de cada estrato; (b) eleitores que votaram em branco, nulo
ou se abstiveram no 1º turno se mobilizaram de forma fortemente assimétrica
a favor de Lula. A exceção localizada é Macapá/Santana. A aritmética, sem
modelo, não exclui migração maior: com dados agregados, migração e
mobilização diferencial não são separáveis de forma definitiva.
*Status: **sustentada pelos dados disponíveis**, sob as premissas (a) e (b);
sem essas premissas, **indeterminada (não identificável)**.*

**Pergunta 4. A mudança de abstenções, brancos e nulos tem associação
estatisticamente relevante com o crescimento de Lula?**
Sim. Correlação municipal entre Δválidos e ΔLula de 0,78 (0,45 com Flávio);
coeficiente de 0,67 voto de Lula por voto válido adicional (0,29 para Flávio);
na inferência ecológica, 61% dos brancos/nulos e 10% dos abstencionistas do 1º
turno votaram em Lula, contra 1,5% e 2,7% em Flávio. Robusto a estratificação
e às priors.
*Status: **sustentada** (como associação entre agregados).*

**Pergunta 5. A divergência entre o desempenho legislativo do PL e a votação
presidencial é consistente com voto dividido?**
Sim. O voto de Flávio foi o dobro do voto no PL para deputado, razão menor que
em 2022 (2,6) e 2018 (3,95). Estima-se que cerca de 5% dos eleitores do PL
para deputado votaram em Lula, e que eleitores de partidos de centro se
dividiram ao meio. Combinações aparentemente divergentes (PL alto e Lula alto
na mesma seção) existem em 3,4% das seções.
*Status: **sustentada**.*

**Pergunta 6. Existem padrões atípicos que persistem após controles e
sensibilidade? Qual sua magnitude e quais explicações restam?**
Dois: (i) a mobilização assimétrica de brancos/nulos e abstencionistas a
favor de Lula, de ~7 milhões de votos, sem paralelo de mesma direção e
magnitude em 2018 e 2022, persistente em todas as especificações; (ii) em
Macapá/Santana, ajuste melhor com ~8% de migração direta (~12,7 mil votos),
persistente com todas as seções do AP. Explicações possíveis: comportamento
eleitoral (mobilização, retorno de eleitores que anularam no 1º turno,
dinâmica local no AP), viés residual de agregação, abstenção diferencial não
modelada. A distribuição geral dos resíduos, o agrupamento espacial e a
ausência de efeito do modelo de urna estão na faixa de 2018 e 2022. Não foi
encontrada nenhuma inconsistência nos registros oficiais.
*Status: **parcialmente sustentada** (há padrões atípicos; nenhum é
inconsistência verificável; suas causas não são identificáveis com dados
agregados).*

**Pergunta 7. 2026 difere significativamente dos padrões de 2018 e 2022?**
Em parte. Igual: fidelidade de ~95–99% aos finalistas e troca direta ≈ 0 nas
três eleições; distribuição dos resíduos; peso dos eliminados semelhante ao de
2022 (7,8% × 8,4% dos válidos). Diferente: variação dos válidos (+3,0 por 100
aptos × +0,2 e −1,5), comparecimento (+1,85 p.p. × +0,36 e −0,97),
brancos/nulos (−1,15 × +0,16 e +0,53) e destino desses eleitores (61% dos
brancos/nulos do 1T para o finalista do PT em 2026; 16% em 2022 e 23% em
2018). 2026 é a única das três eleições em que o finalista que estava atrás
no 1º turno virou, e a única em que o crescimento do finalista do PT superou o
total dos eliminados.
*Status: **parcialmente sustentada**.*

### Quadro das hipóteses de pesquisa

| Hipótese | Status |
|---|---|
| H1 — fidelidade aos finalistas | Sustentada |
| H2 — transferência dos eliminados explica parte do crescimento | Sustentada |
| H3 — mobilização de abstencionistas e brancos/nulos contribuiu para o crescimento de Lula | Sustentada (associação ecológica; quem mudou não é identificável) |
| H4 — diferenças entre voto legislativo e presidencial | Sustentada; consistente com voto dividido |
| H5 — padrões atípicos não explicados | Parcialmente sustentada (mobilização assimétrica; Macapá/Santana); sem inconsistência verificável |

Esses estados descrevem o grau de apoio dos dados às hipóteses e não são
classificações de candidatos ou partidos.

---

## Anexos

### Figuras (`resultados/figuras/`)

| Arquivo | Conteúdo | Natureza |
|---|---|---|
| `mapa_crescimento_lula.png` | ΔLula por 100 aptos, por município | dado oficial |
| `mapa_crescimento_flavio.png` | ΔFlávio por 100 aptos | dado oficial |
| `mapa_variacao_validos.png` | Δválidos por 100 aptos | dado oficial |
| `mapa_votos_eliminados.png` | votos dos eliminados (% dos válidos no 1T) | dado oficial |
| `mapa_variacao_margem.png` | variação da margem Lula − Flávio | dado oficial |
| `dispersao_variacoes_municipios.png` | seis gráficos de dispersão entre as variações | dado oficial |
| `ranking_uf_comparecimento_validos.png` | variação do comparecimento e dos válidos por UF | dado oficial |
| `matrizes_transicao_modeloA.png` | matrizes 2026, 2022, 2018 com IC 95% | estimativa |
| `teste_migracao_minima.png` | teste da seção 7 nas três eleições | estimativa |
| `bayes_sensibilidade_priors.png` | Modelo B, três priors | estimativa |
| `monte_carlo_familias.png` | Modelo C, quatro famílias | simulação |
| `mapa_residuos_modeloA.png`, `mapa_lisa_residuos.png` | resíduos e agrupamentos locais | estimativa |
| `legislativo_pl_vs_presidente.png` | PL (Câmara) × presidente, por seção | dado oficial |

### Fontes e integridade

Lista completa com URL, data de acesso (UTC), tamanho, SHA-256, Last-Modified
e ETag do servidor: `integridade/manifesto_downloads.csv`. Principais:

- `https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_secao/votacao_secao_2026_BR.zip` (Last-Modified 06/10/2026)
- `https://cdn.tse.jus.br/estatistica/sead/odsele/detalhe_votacao_secao/detalhe_votacao_secao_2026.zip` (26/10/2026 15:35 UTC)
- `https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_secao/votacao_secao_2026_<UF>.zip` (26/10/2026)
- `https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_partido_munzona/votacao_partido_munzona_2026.zip`, `votacao_candidato_munzona_2026.zip`
- `https://resultados.tse.jus.br/oficial/ele2026/6258/dados/<uf>/<uf><mun>-c0001-e006258-u.json` (5.787 arquivos; lista de hashes em `~/dados-tse/raw/2026/t2_divulgacao/lista_arquivos_sha256.txt`)
- `https://resultados.tse.jus.br/oficial/ele2026/arquivo-urna/3221/dados/...` (BUs; 50.821 seções da amostra + 1.914 do AP)
- Equivalentes de 2022 e 2018 (`votacao_secao_<ano>_BR`, `detalhe_votacao_secao_<ano>`, `votacao_partido_munzona_<ano>`)
- IBGE: malha municipal (API de malhas v3) e SIDRA, tabelas 4709, 9923, 9543, 10295, 9605 (Censo 2022) e 5938 (PIB 2021)

Verificações por base (seções duplicadas, ausentes, não instaladas,
anuladas, aptos que mudaram entre turnos, conferência BU × detalhe):
`integridade/verificacoes_base_<ano>.json`. Nenhum registro foi descartado;
seções não instaladas (41) ficam na base com zero votos; seções com mudança
de aptos entre turnos são tratadas com linha de "entrada"/coluna de "saída"
de cadastro.

### Observação sobre o formato do BU de 2026

A especificação ASN.1 publicada pelo TSE em 2022
(`formato-arquivos-bu-rdv-ass-digital.zip`) não decodifica o BU de 2026: o
campo `urna.correspondenciaResultado.carga.dataHoraCarga` mudou de tipo. O
leitor `src/boletim_urna.py` percorre a estrutura BER e extrai só os campos de
resultado; ele foi conferido contra o detalhe por seção em todas as 52.335
seções lidas (50.821 da amostra e mais 1.514 do AP), sem divergência.
