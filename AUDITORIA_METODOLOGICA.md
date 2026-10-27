# Auditoria metodológica do estudo "Transferência de votos entre os turnos da eleição presidencial de 2026"

**Versão de 27/10/2026.** Auditoria pedida em [`prompt-auditoria.md`](prompt-auditoria.md),
sobre o estudo publicado em [`RELATORIO.md`](RELATORIO.md) (versão de 26/10/2026) e no
painel <https://ricardomaia.github.io/eleicoes_2026/>. Código da auditoria em
`src/auditoria_*.py` e `src/ei_cov.py`; tabelas em `resultados/auditoria/tabelas/`;
figuras em `resultados/auditoria/figuras/`. Os resultados originais
(`resultados/tabelas/`, `resultados/figuras/`) não foram alterados, para permitir
a comparação. Cada número abaixo tem a tabela de origem indicada.

---

## 1. Resumo executivo

O estudo original é reproduzível (reprodução exata do Modelo A, seção 3.1),
seus dados conferem com as fontes oficiais, e o resultado aritmético (os
candidatos eliminados não bastam para o crescimento de Lula; pelo menos 5
milhões de votos válidos novos; migração direta não determinada pela
aritmética) permanece intacto. O que muda com a auditoria é a **interpretação
das taxas de transição estimadas**, em especial da migração Flávio→Lula de
0,20% e da conversão de brancos/nulos para Lula de 61%:

1. **A hipótese de constância das taxas dentro da UF é rejeitada pelos
   próprios dados.** A versão sem restrições do mesmo modelo (regressão de
   Goodman, erro-padrão por município) dá coeficientes impossíveis como
   probabilidades: Lula→Lula = 1,016 e Flávio→Lula = −0,025 (IC 95% de −0,027
   a −0,022; negativo em 19 das 27 UFs). Isso significa que, dentro das UFs,
   os lugares com mais eleitores de Lula ganharam mais votos para Lula do que
   qualquer matriz constante permite. O "0,20%" publicado é o valor que o
   algoritmo devolve quando a solução livre é negativa e o piso em zero é
   imposto; não é uma medida de migração. A sobredispersão real, medida com a
   variância correta de transições individuais, tem mediana 5,0 por UF
   (não 1,1), o que confirma heterogeneidade forte entre seções.

2. **A migração Flávio→Lula não é identificada pelos dados agregados.** Sob a
   hipótese de constância, a matriz é identificada (posto 5, número de
   condição entre 32 e 67 em todas as UFs) e o teste de teto da publicação
   detecta migrações de 5%, 10% e 15% em dados sintéticos. Mas basta que as
   taxas dos outros grupos variem com a composição local, compensando a
   migração seção a seção, para a mesma migração ser estimada em 0,24% com
   intervalo que exclui a verdade em 100% das repetições. Num cenário
   intermediário e realista (migração de 3,5%, taxas dependentes do contexto,
   heterogeneidade municipal), o modelo estima 0,08% e nunca rejeita um teto
   de 1%. Sem hipótese sobre a forma da heterogeneidade, o conjunto
   identificado da taxa Flávio→Lula vai de 0 a 78%; com fidelidade mínima de
   90% aos dois finalistas, de 0 a 11%; com 95%, de 0 a 9%.

3. **A conversão de brancos/nulos (61%) e de abstencionistas (10%) para Lula
   é a parte menos robusta do estudo.** Os dados sintéticos mostram que
   abstenção diferencial ou mobilização ligadas à preferência local viciam
   essas taxas em 20 pontos ou mais sem que o ajuste piore de forma
   detectável. Nos dados reais, a mesma amostra agregada por zona ou município
   muda a taxa dos eliminados→Lula de 42% para 46–53% e a de brancos/nulos de
   61% para 53–60% (problema da unidade espacial modificável). O Modelo B
   encontra dependência clara da conversão de abstencionistas na margem
   municipal. Os limites identificados sob hipóteses moderadas não restringem
   essas taxas (0 a 100%).

4. **A divergência entre os testes por seção e por município é explicada**:
   o teste por seção trata seções do mesmo município como independentes
   (efeito de desenho 2,8 para a migração e 8,3 para brancos/nulos). Corrigido
   pelo efeito de desenho, o p-valor conjunto do teto 0% passa de 10⁻¹⁰ para
   0,025 e o do teto 5% de 0,0009 para 0,046; a mesma amostra agregada por
   zona dá p = 0,90. O resultado "p < 0,0001" do relatório não deve ser lido
   como evidência forte contra migração nula.

5. **A correlação de 0,78 entre Δválidos e ΔLula é quase toda aritmética**:
   sob uma distribuição nula em que o ganho conjunto (eliminados + Δválidos)
   é repartido entre os finalistas sem nenhuma relação com Δválidos, a
   correlação esperada é 0,74 e o coeficiente esperado é 0,80 (o publicado é
   0,71, abaixo da nula). Onde os válidos cresceram mais, a fração do ganho
   que foi para Lula foi menor (correlação −0,26).

6. **Modelo B e Modelo A concordam porque compartilham a mesma informação e
   quase as mesmas hipóteses**, não porque se validem. Com cadeias quatro
   vezes mais longas, o Modelo B converge (R-hat ≤ 1,008, ESS ≥ 417) e
   reproduz as taxas publicadas; a taxa Flávio→Lula varia de 0,23% a 0,75%
   conforme a prior, ou seja, numa região em que a verossimilhança é plana a
   prior ainda decide a ordem de grandeza.

7. **Amapá.** A migração de 8 a 10% estimada em Macapá e Santana resiste a
   bootstrap por zona e por local de votação e aos modelos com taxas
   dependentes do contexto, mas (a) depende das seções em que o
   comparecimento mudou mais de 10 pontos (sem elas, cai a 3,0–3,5%; sem as
   de mais de 5 pontos, a 1,0–1,3%); (b) o que o modelo troca por migração
   não é abstenção diferencial, e sim conversão quase total dos eleitores dos
   candidatos eliminados; (c) sem a hipótese de constância, reproduzir todas
   as seções com migração zero exige que apenas 0,1% a mais do eleitorado
   se comporte fora da matriz comum. É um resultado de modelo, não uma
   inconsistência de dados.

8. **O que resiste.** Fatos oficiais e identidades; a impossibilidade de os
   eliminados explicarem sozinhos o crescimento de Lula; a entrada de pelo
   menos 5 milhões de votos válidos novos; a ausência de inconsistência entre
   fontes do TSE; a fidelidade elevada aos finalistas como consequência dos
   limites (com 90% de fidelidade imposta, nenhuma seção contradiz os dados
   em 96% dos casos); a capacidade preditiva agregada dos modelos (erro
   absoluto médio de 1,7 ponto na participação de Lula fora da amostra). O
   que não resiste: as estimativas pontuais de migração e de conversão de
   não votantes como medidas do comportamento individual, e a leitura do
   teste de teto por seção como rejeição forte da migração nula.

Resposta curta às perguntas finais do prompt: seção 10.

---

## 2. Inspeção inicial e problemas identificados

### 2.1 Inventário dos modelos e hipóteses

| Modelo | Script | Hipótese central | Unidades | Incerteza |
|---|---|---|---|---|
| A — quase-verossimilhança multinomial, EM + SQUAREM, uma matriz por UF | `analise_03`, `ei.py` | taxas constantes dentro da UF (Goodman); B ≥ 0, linhas = 1 | 50.821 seções (amostra de BUs) e 5.757 municípios | bootstrap por município, 200 réplicas; teste F de quase-verossimilhança com φ multinomial |
| B — bayesiano hierárquico (PyMC) | `analise_04` | logitos = μ + efeito de UF + urbanização + margem municipal; Dirichlet-multinomial | 4.000 seções | 4 cadeias × 400 sorteios (600 de aquecimento) |
| C — Monte Carlo por famílias | `analise_05` | matriz sorteada de Dirichlet, calibrada por raking aos totais nacionais | municípios | 4 lotes de 5.000 |
| D — resíduos, I de Moran, modelo de urna | `analise_07` | resíduos do Modelo A | municípios e seções | DerSimonian-Laird, Benjamini-Hochberg |
| Sensibilidade a estratos | `analise_03b` | mesma constância, estratos mais finos | seções | sem intervalos |
| Amapá completo | `analise_03c` | constância | 1.914 seções | bootstrap por seção |

### 2.2 Fontes de dados e integridade (seção 14 do prompt)

- Fontes, hashes e datas estão em `integridade/manifesto_downloads.csv`; as
  verificações por base em `integridade/verificacoes_base_<ano>.json`. Os
  totais nacionais conferem com os documentos oficiais (16 de 16 indicadores)
  e as três fontes do TSE para o 2º turno (detalhe por seção, divulgação
  municipal, BUs) coincidem sem divergência. Como o relatório já observa,
  isso mostra coerência interna do sistema do TSE, não validação externa.
- **Votação presidencial por seção no 2º turno.** Durante quase toda a
  auditoria o arquivo nacional estava na versão de 06/10 (só 1º turno) e os
  arquivos por UF, mesmo nas versões de 26/10, só traziam o 2º turno para
  governador (cargo 3). Em 27/10/2026, 00h50 em Brasília, o CDN passou a
  anunciar a versão de 26/10 17h42 UTC (241.891.087 bytes, SHA-256
  `c928321f63f2d095706fca73d4607c048d2ada23bda6876455d6911aaf1bc9c1`), mas
  o pedido normal ainda devolvia a antiga; só um pedido sem cache
  (`Cache-Control: no-cache`) trouxe a nova. Ela contém a votação por
  candidato nas 499.205 seções do 2º turno, com totais iguais aos oficiais.
  `montar_base.py` foi reconstruído com ela: a amostra de 50.821 BUs passou
  a ser conferência independente do arquivo por seção (zero divergências em
  aptos, comparecimento, brancos, nulos, Lula e Flávio) e a soma por município
  confere com o JSON de divulgação (zero divergências em 5.757 municípios).
  Todos os resultados desta auditoria citados nas seções 4.1 a 4.8 foram
  calculados com a amostra; a seção 4.11 traz os recalculados com todas as
  seções (saídas com sufixo `_todas`), e os resultados originais com a
  amostra estão preservados em `resultados/versao_amostra_bu/`.
- **Inconsistência de versões no CDN do TSE**: entre o download e uma nova
  consulta no mesmo dia, o servidor passou a informar versões diferentes dos
  arquivos por UF (datas e tamanhos distintos; em PR, SP e PA a versão
  informada passou a ser mais antiga que a baixada). Registrado em
  `RELATORIO.md`, seção VIII, item 9, com a lista de UFs e o SHA-256 da nova
  versão do AP. Quem reproduzir o estudo deve conferir o SHA-256 do
  manifesto.
- **Amostra de seções.** O desenho (`baixar_bu_t2_amostra.py`) é aleatório
  simples dentro de cada UF, fração 10%, mínimo 400, semente fixa, universo =
  seções instaladas do 2º turno. É um desenho correto e reproduzível. A
  amostra não é autoponderada (AC, AP, RR, TO, RO e ZZ têm fração maior que
  10%); o Modelo A respeita isso porque estima por UF e expande pelos totais
  da UF, mas as somas "seção (amostra)" dos limites de Fréchet no relatório
  não são expandidas, como lá se diz. A incerteza amostral entra nos
  bootstraps; o efeito de desenho (seções do mesmo município) é medido na
  seção 4.3.
- Seções não instaladas (41), transferências temporárias (74.692 aptos em
  55.722 seções) e nulos técnicos são tratados explicitamente no código e
  conferidos pelos testes.

### 2.3 Problemas metodológicos encontrados (por impacto)

1. **Constância rejeitada e piso em zero** (seções 4.1 e 4.2): o estimador
   restrito devolve um valor pequeno e positivo quando o irrestrito é
   negativo; os intervalos de bootstrap herdam o piso e por isso "excluem o
   zero". Impacto: a conclusão "migração entre 0,02% e 0,8% em todos os
   modelos" descreve o comportamento do estimador, não um intervalo para a
   migração real.
2. **Não identificação sem constância** (4.1, 4.2, 4.4): intervalos
   publicados são condicionais a uma hipótese que os dados contradizem.
3. **Pseudorreplicação no teste de teto por seção** (4.3): φ de seção ignora a
   correlação dentro do município.
4. **Variância multinomial inadequada** (4.3): subestima a heterogeneidade
   real em 3 a 7 vezes; o "φ ≈ 1,1" do relatório não indica bom ajuste.
5. **Correlação parte-todo** (4.5) apresentada como associação substantiva.
6. **Modelo B com cadeias curtas e R-hat 1,04** (4.6): resolvido com cadeias
   longas; as conclusões não mudam, mas a dependência da prior é maior do que
   o relatório sugere.
7. **Monte Carlo (Modelo C)**: as "frações de bom ajuste" dependem da largura
   arbitrária das famílias e são corretamente qualificadas no relatório; não
   acrescentam identificação. Não foi refeito.
8. **Problema da unidade espacial modificável** (4.3): resultados do nível
   município não são "sensibilidade" do nível seção, são outra estimativa.

### 2.4 Problemas de implementação e documentação

- O estimador EM está correto e é reproduzível (seção 3.1). As restrições de
  célula são impostas de forma exata. Nenhum erro de cálculo foi encontrado
  nas tabelas originais.
- `ei.sobredispersao` usa a variância multinomial; a auditoria acrescenta a
  variância de transição independente (`auditoria_comum.variancia_transicao`).
- O teste de teto soma χ² de UFs com φ de seção; a correção por efeito de
  desenho é aproximada (seção 4.3) e o teste de Wald da regressão de Goodman
  é a alternativa exata sem restrições.
- `analise_04`: `DirichletMultinomial` só modela sobredispersão em relação à
  multinomial; como a variância correta é menor que a multinomial, o modelo
  é conservador nas linhas dominantes. Não corrigido (mudança de modelo).
- Documentação: o relatório descreve as limitações da inferência ecológica
  corretamente na seção VIII, mas o resumo executivo e as conclusões usam
  as estimativas como se fossem intervalos para o comportamento real. As
  conclusões foram reescritas (seção 9 e `RELATORIO.md`, seção IX-A).
- Console do Windows em cp1252 derruba scripts que imprimem "→"; corrigido em
  `auditoria_comum.py` (UTF-8).

---

## 3. Reprodução e correções implementadas

### 3.1 Reprodução

`auditoria_00_reproducao.py` recalcula o bloco principal do Modelo A (2026,
seção, origens base) do zero, sem o cache `interim/ei_bloco_*.pkl`, com a
mesma semente. Resultado: diferença máxima **0,000000** em todas as 20 taxas,
nos 40 limites de intervalo e nos 10 χ² dos testes de teto
(`00_reproducao_modeloA.csv`, `00_reproducao_teste_migracao.csv`; 978 s).
Os 11 testes originais passam; os 10 testes novos (`tests/test_auditoria.py`)
também.

### 3.2 O que foi acrescentado ao repositório

| Item | Arquivo |
|---|---|
| Variância correta de transições individuais; caminhos da auditoria | `src/auditoria_comum.py` |
| Regressão de Goodman sem restrições com EP por conglomerado; conjuntos identificados por programação linear (S0–S4); fronteira de heterogeneidade; equivalentes construtivos | `src/auditoria_01_identificacao.py` |
| Gerador sintético com transições individuais; cenários A–F e Hσ; métricas | `src/auditoria_02_sintetico.py` |
| Múltiplas inicializações; φ com duas variâncias; bootstrap 1.000 por município e por seção; teste de teto em quatro granularidades e com correção de desenho | `src/auditoria_03_estabilidade.py` |
| Modelo B com 1.000 + 1.000 iterações, correlações posteriores | `src/auditoria_04_bayes.py` |
| Modelos M1 (taxas × margem municipal) e M2 (preferência latente) | `src/ei_cov.py`, `src/auditoria_05_covariaveis.py` |
| Nula aritmética para a correlação parte-todo | `src/auditoria_06_parte_todo.py` |
| Amapá: bootstrap por conglomerado, M1/M2, perfil de troca, influência, fronteira | `src/auditoria_07_amapa.py` |
| Validação cruzada agrupada por município; comparação sintética A × B2 | `src/auditoria_08_validacao_cruzada.py` |
| Limites de Fréchet para o voto cruzado | `src/auditoria_09_legislativo_limites.py` |
| Figuras comparativas | `src/auditoria_10_figuras.py` |
| Testes de método | `tests/test_auditoria.py` |
| Etapas no pipeline (`--so-auditoria`, `--com-auditoria`) | `src/executar_tudo.py` |

---

## 4. Experimentos realizados e resultados numéricos

### 4.1 Identificabilidade (prompt, seção 3.1)

**Sob constância.** `01_condicionamento_por_uf.csv`: a matriz de composição
do 1º turno (n × 5, ponderada por √N) tem posto 5 em todas as 27 UFs; o
número de condição vai de 32 (SP) a 67 (RR). Portanto, se cada UF tivesse
uma única matriz de transição, ela seria determinada pelos dados: a
dimensão do espaço de soluções equivalentes é zero. As restrições B ≥ 0 e
linhas = 1 não são necessárias para identificar, só reduzem variância.

**O estimador sem restrições contradiz a hipótese.** `01_goodman_wls_nacional.csv`
(mínimos quadrados ponderados de y/N sobre x, sem intercepto, por UF; EP por
município; agregação nacional pelos totais de origem):

| Origem → Lula (2T) | Coeficiente nacional | EP | IC 95% | UFs com coeficiente negativo |
|---|---:|---:|---|---:|
| Lula (1T) | 1,016 | 0,0016 | 1,012 a 1,019 | 0 |
| Flávio (1T) | **−0,025** | 0,0013 | −0,027 a −0,022 | 19 |
| Outros (1T) | 0,447 | 0,0086 | 0,431 a 0,464 | 0 |
| Brancos/nulos (1T) | 0,624 | 0,0168 | 0,591 a 0,657 | 0 |
| Abstenção (1T) | 0,091 | 0,0028 | 0,086 a 0,097 | 3 |

Lula→Flávio dá −0,035. Por município (todos os 5.757) o padrão é o mesmo
(Flávio→Lula −0,029, IC −0,033 a −0,025). Um coeficiente acima de 1 para
Lula→Lula e abaixo de 0 para Flávio→Lula não pode ser uma probabilidade;
é o sinal clássico de viés de agregação: as taxas dos outros grupos variam
junto com a composição (onde Lula é mais forte, mais não votantes vão para
Lula), e o modelo linear atribui essa variação às linhas dos finalistas. O
estimador restrito (EM) resolve isso levando Flávio→Lula ao piso zero nas 19
UFs e deixando positivas as 8 restantes (AP 9,9%, AM 2,0%, MA 1,6%, PI 1,5%,
CE 1,5%, RR 1,0%, TO 0,9%, AC 0,8%); a média ponderada é o 0,20% publicado.

**Sem constância.** `01_limites_lp_conjuntos_hipoteses.csv`: para cada seção
da amostra, programa linear sobre a matriz de fluxos com as margens da seção
e as hipóteses do conjunto; limites somados por UF e expandidos pelos totais
da UF (`*_expandida`):

| Conjunto de hipóteses | Flávio→Lula (taxa) | Flávio→Lula (votos) | Lula→Flávio | Seções em que a hipótese é impossível |
|---|---|---|---|---:|
| S0: nenhuma (Fréchet) | 0 a 77,8% | 40 a 43,5 mi | 0 a 73,5% | 0 |
| S1: fidelidade ≥ 90% aos dois finalistas | 0 a 11,1% | 40 a 6,23 mi | 0 a 9,2% | 1.931 (3,8%) |
| S2: S1 + abstenção ≤ 10% entre quem votou nos finalistas | 0 a 11,1% | idem | 0 a 9,2% | 1.931 |
| S3: S2 + pelo menos 70% dos abstencionistas continuam abstendo | 0 a 12,9% | 69 a 7,23 mi | 0 a 11,0% | 3.370 (6,7%) |
| S4: fidelidade ≥ 95% | 0 a 9,0% | 40 a 5,04 mi | 0 a 7,9% | 4.201 (8,3%) |

Nas seções em que a hipótese é impossível (por exemplo, Lula perdeu mais de
10% dos votos do 1º turno naquela seção), usou-se o limite de Fréchet. Por
município (5.757, todas as células): sob S1, Flávio→Lula de 0 a 10,2%;
outros→Lula de 0 a 98,5%; brancos/nulos→Lula de 0 a 99,97%; abstenção→Lula
de 0 a 48,2%; sob S3, abstenção→Lula de 0 a 30,1%; sob S4, Flávio→Lula de 0 a
6,3%. **Conclusão:** hipóteses moderadas limitam a migração direta a cerca de
um décimo dos eleitores de Flávio, mas não dizem nada sobre a origem dos
votos de Lula entre eliminados, brancos/nulos e abstencionistas. Esses
limites são condicionais às hipóteses listadas e não valem fora delas.

**Dimensão do conjunto equivalente sem constância:** cada seção tem um
politopo de fluxos de dimensão 12 (20 células menos 8 margens
independentes); o espaço de matrizes seção a seção compatíveis com os dados
tem dimensão 12 × 50.821. A construção explícita
`01_equivalentes_construtivos.csv` mostra uma família B_i = B̂ + Δ_i com
x_i·Δ_i = 0 (mesma verossimilhança) que soma δ à migração Flávio→Lula e
compensa só nas linhas de Flávio e da abstenção do 1º turno; essa família
restrita cabe em [0, 1] em 30% das seções para δ = 1 ponto e em 11% para
δ = 2 pontos, e em quase nenhuma para δ ≥ 5, porque a linha da abstenção
sozinha não tem votos de Lula suficientes para compensar. Quando as linhas
dos eliminados e dos brancos/nulos também participam da compensação, a
família cabe em muito mais seções — é o que o programa linear abaixo
quantifica.

**Fronteira de heterogeneidade** (`01_fronteira_heterogeneidade_nacional.csv`,
`_por_uf.csv`; programa linear por UF com subamostra de até 600 seções; 162
programas, 65 s cada em média, todos com solução ótima). Fração mínima do
eleitorado cujo comportamento precisa desviar de uma matriz comum à UF para
que todas as seções sejam reproduzidas exatamente, com a taxa Flávio→Lula
da matriz comum fixada em c:

| c imposto | Fração mínima desviante (média nacional ponderada) | UF máxima | Brancos/nulos→Lula da matriz comum | Abst.→Lula | Eliminados→Lula |
|---|---:|---:|---:|---:|---:|
| livre (ótimo de desvio absoluto mínimo) | 2,75% | AC 4,8% | 61,3% | 10,6% | 40,1% |
| 0% | 2,75% | 4,8% | 61,5% | 10,6% | 40,5% |
| 0,2% | 2,76% | 4,8% | 61,2% | 10,5% | 39,9% |
| 2% | 2,79% | 4,8% | 59,3% | 9,3% | 35,2% |
| 5% | 2,89% | 4,8% | 56,9% | 7,4% | 26,6% |
| 10% | 3,13% | 5,0% | 50,9% | 4,4% | 13,0% |

Com c livre, a matriz comum de desvio absoluto mínimo coincide com a do EM
(Flávio→Lula 0,11%; brancos/nulos→Lula 61%; abstencionistas→Lula 10,6%),
o que mostra que, **sob constância**, os dois estimadores concordam. Mas a
fronteira é quase plana: passar de migração zero para 10% exige que apenas
0,38 ponto percentual a mais do eleitorado (de 2,75% para 3,13%) se comporte
fora da matriz comum, e a heterogeneidade mínima já presente nos dados com
migração zero (2,75%) é sete vezes maior que esse acréscimo. Em nenhuma UF
o acréscimo passa de 0,8 ponto (MT, RO, RS). Os dados não distinguem, sem a
hipótese de constância, migração zero de migração de 10%. A compensação
necessária é a mostrada nas colunas da direita: menos eleitores dos
eliminados, dos brancos/nulos e dos abstencionistas para Lula.

### 4.2 Experimentos adversariais com dados sintéticos (prompt, seção 4)

`auditoria_02_sintetico.py`; parâmetros em `02_sintetico_parametros.json`;
628 execuções (19 cenários × {20 repetições com 2.000 seções, 12 com 10.000};
5 cenários × 4 repetições com 50.000). O gerador sorteia, para cada eleitor
de cada origem, o destino com a matriz da seção (transições individuais
conhecidas), com estados, municípios e ideologia latente θ que produzem
correlação espacial. O Modelo A é aplicado sem nenhuma informação sobre as
transições. Taxa Flávio→Lula, 10.000 seções, 12 repetições
(`02_sintetico_resumo_celulas.csv`; erro-padrão Monte Carlo do viés entre
0,0002 e 0,0016):

| Cenário | Verdade | Estimada | Viés | Cobertura IC 95% | φ (multinomial) |
|---|---:|---:|---:|---:|---:|
| A — fidelidade elevada, matriz ≈ constante | 0,20% | 0,24% | +0,03 pp | 0,92 | 0,43 |
| B1 — migração 5% com compensação constante | 5,26% | 5,26% | 0,00 | 0,83 | 0,47 |
| B1 — migração 10% | 10,25% | 10,24% | −0,01 | 1,00 | 0,51 |
| B1 — migração 15% | 15,23% | 15,24% | +0,01 | 0,92 | 0,56 |
| **B2 — migração 5% com compensação exata por seção** | 5,20% | **0,24%** | **−4,95 pp** | **0,00** | 0,46 |
| **B2 — migração 10%** | 9,87% | **0,24%** | **−9,62 pp** | **0,00** | 0,49 |
| **B2 — migração 15%** | 13,01% | **0,26%** | **−12,8 pp** | **0,00** | 0,49 |
| C — abstenção diferencial por preferência local, migração 0,2% | 0,20% | 0,00% | −0,20 | 0,00 (todas no limite) | 0,68 |
| D — forte heterogeneidade regional | 0,36% | 0,50% | +0,14 | 0,67 | 1,16 |
| **E — mistura: migração 3% + dependência em θ + heterogeneidade** | 3,45% | **0,08%** | **−3,37 pp** | **0,00** | 0,64 |
| F — má especificação (θ, θ², sobredispersão) | 0,31% | 0,00% | −0,31 | 0,00 | 1,65 |

Com 2.000 e 50.000 seções os resultados são os mesmos; o tamanho da amostra
não corrige viés de especificação. Conversão de brancos/nulos→Lula: no
cenário C a verdade é 57,8% e a estimativa 37,5% (viés −20 pp); no F, 65,6%
contra 45,3%; no B2 com 10% de migração, 24,9% contra 58,2% (+33 pp). A
conversão de abstencionistas→Lula no C: 13,6% contra 17,6%. Heterogeneidade
municipal pura (Hσ, σ_mun de 0 a 1,0 na escala logit): com migração 0,2%, a
estimativa sobe para 0,65% e a cobertura cai a 0,83; com migração 5%, a
estimativa fica certa (viés ≤ 0,2 pp). O φ multinomial dos dados reais
(mediana 1,1; AP 2,4) está entre os cenários D e F, isto é, a heterogeneidade
real é da ordem de σ_mun ≈ 0,6 a 1,0, bem acima do cenário A.

Testes de teto (`02_sintetico_resumo_testes.csv`, 10.000 seções):

| Cenário | Teto 0% rejeitado | Teto 1% | Teto 2% | Teto 5% | Leitura |
|---|---:|---:|---:|---:|---|
| A | 17% | 0% | 0% | 0% | sem falso positivo acima de 1% |
| B1 (5/10/15%) | 100% | 100% | 100% | 100% / 100% / 100% (5%: 83%) | poder total sob constância |
| B2 (5/10/15%) | 8–25% | **0%** | **0%** | **0%** | falso negativo de 100% |
| E (3,5%) | 8% | 8% | 0% | 0% | falso negativo de 92–100% |
| C, F (≈ 0,2–0,3%) | 0% | 0% | 0% | 0% | — |

**Resposta à pergunta central do prompt:** um modelo que estima 0,20%
reconhece uma migração real de 5, 10 ou 15% **somente se** os fluxos
compensatórios forem iguais em todas as seções do estrato. Se a compensação
variar com a composição local (que é exatamente o que a regressão sem
restrições indica nos dados reais), a migração é invisível, qualquer que
seja o tamanho da amostra, e o teste de teto a declara ausente.

### 4.3 Estabilidade, variância e agregação (prompt, seções 5 e 8)

`auditoria_03_estabilidade.py`.

- **Inicializações** (`03_multi_start_por_uf.csv`): 20 inícios aleatórios por
  UF. A log-verossimilhança final varia no máximo 2,7 unidades (RS), mas a
  taxa Flávio→Lula varia entre ótimos equivalentes em PI (0 a 1,5%), AC (0 a
  0,8%), PB (0 a 0,6%), SE (0 a 0,4%) e RN (0 a 0,3%): nessas UFs a
  verossimilhança é plana nessa direção, ou seja, a taxa não é determinada
  nem sob constância.
- **Variância correta** (`03_phi_duas_variancias.csv`): com a variância
  multinomial, φ tem mediana 1,10 (0,77 a 2,85); com a variância de
  transições independentes, Σ_r x_r B_rc(1 − B_rc)/N, φ tem mediana **4,97**
  (2,8 no DF a 14,2 no PA). A variância multinomial é 3,3 a 7,3 vezes maior
  que a correta na coluna de Lula, por isso "φ ≈ 1" não indica ajuste bom:
  há de três a catorze vezes mais variação entre seções do que uma matriz
  constante explica.
- **Bootstrap de 1.000 réplicas** (`03_bootstrap_1000.csv`): Flávio→Lula
  0,197%; percentil por município 0,125 a 0,322% (publicado com 200: 0,12 a
  0,32%); básico 0,072 a 0,269%; por seção, ignorando municípios, 0,155 a
  0,274%. Efeito de desenho (variância por município / por seção): 2,8 para
  Flávio→Lula, 3,3 para Lula→Lula, 8,3 para brancos/nulos→Lula, 3,7 para
  abstenção→Lula. Brancos/nulos→Lula: 60,9% (57,5 a 61,4). Todos esses
  intervalos são condicionais à constância e ao piso em zero.
- **Teste de teto por nível** (`03_teste_teto_por_nivel.csv`):

| Nível | Unidades | Flávio→Lula | Outros→Lula | Brancos/nulos→Lula | Abst.→Lula | p conjunto, teto 0% | teto 2% | teto 5% |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| seção (amostra), como publicado | 50.421 | 0,20% | 42,4% | 60,9% | 10,3% | 8 × 10⁻¹¹ | 3 × 10⁻⁸ | 0,0009 |
| seção, χ² dividido pelo efeito de desenho 2,8 | 50.421 | — | — | — | — | **0,025** | 0,002 | **0,046** |
| zona (mesma amostra agregada) | 6.881 | 0,13% | 46,1% | 59,8% | 9,4% | 0,90 | 0,66 | 1,00 |
| município (mesma amostra agregada) | 6.248 | 0,10% | 50,7% | 56,2% | 9,0% | 0,996 | 0,82 | 1,00 |
| município (todos, resultado completo) | 6.907 | 0,11% | 52,6% | 53,0% | 8,9% | 0,82 | 0,41 | 1,00 |

  A divergência seção × município descrita no relatório tem duas causas:
  pseudorreplicação (seções do mesmo município não são independentes) e
  mudança de unidade (as taxas dos eliminados e dos brancos/nulos mudam em
  até 10 pontos ao agregar, o problema da unidade espacial modificável). O
  teste de Wald unilateral da regressão de Goodman
  (`03_teste_teto_wald_goodman.csv`) não rejeita nenhum teto porque o
  coeficiente irrestrito é negativo, o que, de novo, aponta para má
  especificação, não para "migração zero".

### 4.4 Taxas dependentes do contexto: modelos M1 e M2 (prompt, seções 3.2 e 6)

`ei_cov.py`, `auditoria_05_covariaveis.py`. M1: cada linha da matriz é
softmax(α + β·z), com z a margem Lula − Flávio do município no 1º turno,
padronizada (30 parâmetros por UF). M2: quem votou em branco/nulo ou se
absteve no 1º turno tem preferência latente π_i = Lula₁/(Lula₁ + Flávio₁)
da sua seção e comparece/converte com taxas τ_L e τ_F (15 parâmetros por
UF; a participação eleitoral depende da preferência latente). Ajuste por
UF na amostra; taxas nacionais calculadas aplicando as taxas de cada UF
aos totais de origem de todas as 499 mil seções. Intervalos de 95% para
M1 e M2 por bootstrap de municípios (100 réplicas por UF, percentis 2,5 e
97,5 das taxas nacionais; `05_taxas_nacionais_por_modelo.csv`); o
intervalo de M0 está na seção 3.3 (`03_bootstrap_1000.csv`):

| Taxa nacional | M0 (constância) | M1 (margem municipal) | M2 (preferência latente) |
|---|---:|---:|---:|
| Flávio→Lula | 0,20% | 0,11% (0,08 a 0,26) | 0,60% (0,49 a 0,78) |
| Lula→Flávio | 0,00% | 0,00% (0,00 a 0,02) | 0,00% (0,00 a 0,00) |
| Lula→abstenção | 1,1% | 0,7% (0,6 a 1,1) | 1,1% (0,9 a 1,3) |
| Flávio→abstenção | 0,9% | 1,6% (1,4 a 1,8) | 0,4% (0,3 a 0,6) |
| Eliminados→Lula | 42,4% | 40,9% (40,2 a 42,6) | **58,7%** (57,5 a 60,4) |
| Eliminados→Flávio | 39,0% | 40,6% (39,2 a 41,4) | 26,7% (24,8 a 27,5) |
| Brancos/nulos→Lula | 60,9% | 59,7% (58,5 a 60,5) | **31,2%** (30,8 a 31,5) |
| Brancos/nulos→Flávio | 1,5% | 2,5% (1,7 a 3,2) | 10,5% (9,9 a 11,1) |
| Brancos/nulos→abstenção | 0,6% | 1,0% (0,5 a 2,2) | 19,8% (19,0 a 20,5) |
| Abstenção→Lula | 10,3% | 10,5% (10,0 a 10,9) | 9,9% (9,4 a 10,4) |
| Abstenção→Flávio | 2,7% | 3,1% (2,8 a 3,4) | 4,8% (4,4 a 5,2) |
| Deviance total (27 UFs) | 131.152 | **126.595** | 134.750 |

M1 reduz a deviance em 4.557 (3,5%) com 405 parâmetros a mais, uma
melhora grande para a escala desses dados; em 17 UFs o otimizador parou no
limite de iterações (500) com ganho ainda pequeno por passo, de modo que a
deviance de M1 é um limite superior. Sob M1 as taxas variam com a margem
(`05_M1_taxas_por_quantil_margem.csv`): nos municípios do decil mais
favorável a Flávio, brancos/nulos→Lula é 55% e abstenção→Flávio 4,4%; no
decil mais favorável a Lula, 63% e 2,3%; eliminados→Lula vai de 38% a 45%;
Flávio→Lula fica entre 0,09% e 0,18%. M2 ajusta pior no total (+3.598), mas
melhor que M0 em MG, MS, MT, RS, SC, PI e RR; sob M2 a conversão de
brancos/nulos para Lula cai de 61% para **31%**, a dos eliminados sobe de
42% para **59%** e a migração Flávio→Lula sobe para 0,60%. Os intervalos
de bootstrap de M1 e M2 não se sobrepõem em nenhuma dessas três taxas:
a diferença entre os modelos é de especificação, não de amostragem. Para
Flávio→Lula, o intervalo de M1 (0,08 a 0,26) cruza o de M0 (0,13 a 0,32) e
o de M2 (0,49 a 0,78) fica acima dos dois. Esses intervalos medem a
variação por reamostragem de municípios dentro de cada forma funcional;
não dizem nada sobre o conjunto identificado da seção 4.1, que contém os
três. Vários intervalos são assimétricos, com a estimativa pontual perto de
um dos extremos (por exemplo, Lula→Lula sob M1: 98,9%, intervalo 98,4 a
99,0): as réplicas, iniciadas na estimativa pontual e com o mesmo limite de
500 iterações, tendem a parar do mesmo lado, consequência da convergência
incompleta de M1 em 17 UFs. **O que isso
mostra:** os votos de Lula que não vêm dele mesmo podem ser repartidos de
maneiras muito diferentes entre eliminados, brancos/nulos e abstencionistas
conforme a forma da dependência de contexto que se admite; a previsão
agregada dos três modelos é praticamente a mesma (seção 4.8). As
estimativas de "61% dos brancos/nulos" e "42% dos eliminados" são, portanto,
dependentes da especificação. A migração Flávio→Lula fica abaixo de 1% nos
três modelos, inclusive nos limites superiores dos intervalos (0,26% sob
M1, 0,78% sob M2), mas por serem variantes da mesma família (taxas da seção
determinadas pela composição e por uma matriz comum), isso não restringe
as hipóteses não identificadas da seção 4.1.

### 4.5 Correlação parte-todo (prompt, seção 7)

`auditoria_06_parte_todo.py`, `06_parte_todo.csv`, 5.571 municípios,
ponderação pelos aptos. Identidade: ΔLula + ΔFlávio = eliminados + Δválidos.
Distribuição nula: o ganho conjunto de cada município é repartido entre os
finalistas com uma fração independente de Δválidos (constante igual à
nacional, 0,737; binomial; ou Beta com a dispersão real das frações
municipais, κ = 3,4).

| Medida | Observado | Nula constante | Nula binomial | Nula Beta (IC 95%) |
|---|---:|---:|---:|---|
| correlação Δválidos × ΔLula (taxas por apto) | 0,777 | 0,738 | 0,738 | 0,559 (0,475 a 0,614) |
| coeficiente de ΔLula sobre Δválidos | 0,710 | 0,798 | 0,798 | 0,795 (0,658 a 0,906) |
| correlação em valores absolutos | 0,996 | 0,994 | 0,994 | 0,975 |
| correlação Δválidos × fração do ganho para Lula | **−0,261** | 0 | 0 | 0 |
| correlação Δválidos × Δlog(Lula/Flávio) | 0,026 | — | — | — |

A correlação de 0,78 e o coeficiente de 0,67 citados no relatório (0,71 sem
os controles) são o que a aritmética produz quando o ganho é repartido na
proporção nacional; o coeficiente observado está **abaixo** da nula, e a
fração do ganho conjunto que foi para Lula é menor onde os válidos cresceram
mais. A pergunta 4 do relatório ("associação estatisticamente relevante
entre mobilização e crescimento de Lula") não é sustentada por essas
correlações; o que resta é a associação entre a queda de brancos/nulos e a
votação inicial de Lula (−0,46 por município), que é descritiva.

### 4.6 Modelo B com cadeias longas (prompt, seção 5)

`auditoria_04_bayes.py`, 4.000 seções, 4 cadeias × (1.000 aquecimento +
1.000 sorteios), `04_bayes_diagnosticos_<prior>.json`,
`04_bayes_matriz_nacional_<prior>.csv`:

| Prior | Flávio→Lula | Brancos/nulos→Lula | Abst.→Lula | R-hat máx. | ESS mín. | Divergências | Tempo |
|---|---|---|---|---:|---:|---:|---:|
| neutra | 0,23% (0,03 a 0,58) | 57,5% (54,0 a 60,4) | 10,8% (9,8 a 11,7) | 1,004 | 752 | 0 | 70 min |
| fidelidade alta | 0,42% (0,20 a 0,72) | 54,7% (51,7 a 57,6) | 11,2% (10,2 a 12,2) | 1,005 | 417 | 4 | 48 min |
| troca alta (centrada em 15%) | 0,75% (0,45 a 1,10) | 54,6% (51,3 a 57,7) | 11,1% (10,1 a 12,0) | 1,008 | 519 | 0 | 46 min |

Os valores são os publicados com cadeias curtas; o problema de convergência
da prior "troca alta" (R-hat 1,042) desaparece. As correlações posteriores
entre taxas nacionais são fracas (|r| ≤ 0,27 fora da própria linha), isto
é, dentro do modelo não há troca entre migração e abstenção diferencial. O
coeficiente da margem municipal sobre a conversão de abstencionistas é
positivo para Lula (+0,23, intervalo de 89% de 0,15 a 0,31) e negativo para
Flávio (−0,57, de −0,77 a −0,36): o Modelo B já incorpora a dependência de
contexto que o Modelo A ignora, e mesmo assim dá a mesma migração. Isso
reforça que a concordância A–B não é validação independente: os dois modelos
usam as mesmas seções, a mesma composição e a mesma forma funcional
multiplicativa; o que os dados não identificam, os dois deixam para a
hipótese ou para a prior (a prior ainda move a migração por um fator de
três, de 0,23% a 0,75%).

### 4.7 Amapá (prompt, seção 9)

`auditoria_07_amapa.py`, todas as 1.914 seções com BU (`07_amapa_*.csv`).

**Observações (dado oficial).** O comparecimento no AP caiu 8,06 pontos entre
os turnos (a maior queda do país); não havia disputa estadual no 2º turno.
Em 1.417 das 1.914 seções a variação de comparecimento ficou dentro de
±10 pontos; em 569, dentro de ±5.

**Estimativas sob constância** (`07_amapa_principal.csv`): Flávio→Lula de
10,0% no estado (IC 95% por seção 8,3 a 11,5%; por zona 4,1 a 11,9%; por
município 0 a 11,9%; por local de votação 7,5 a 12,0%), 7,9% em Macapá e
Santana (5,6 a 9,1% por zona), 0% no interior. O relatório usa o bootstrap
por seção; por município o intervalo inclui zero. A regressão de Goodman sem
restrições, com erro-padrão por zona, dá 4,1% (EP 2,1) no estado, 6,9%
(EP 0,3) em Macapá e Santana e **−8,2%** no interior: a hipótese de
constância também falha no AP. Com Bonferroni sobre 27 UFs × 2 sentidos, o
teto de 5% em Macapá e Santana tem p = 0,053.

**Modelos alternativos.** M1 (taxas dependentes da participação de Lula na
seção) reduz a deviance em 9% (11.333 → 10.293) e mantém a migração em 11,4%
no estado e 8,9% em Macapá e Santana; M2 (preferência latente) dá 11,3% e
8,6%. A estimativa não depende de a abstenção de cada grupo ser constante.

**Perfil de troca** (`07_amapa_perfil_troca.csv`): fixando Flávio→Lula em 0%
no estado, o melhor ajuste não aumenta a abstenção dos eleitores de Lula
(17,0% contra 20,4% no ajuste livre); o que muda é a origem dos votos de
Lula: eliminados→Lula sobe de 59% para 91% e brancos/nulos→Lula de 76% para
79%, com aumento de deviance de 290 (145 na escala de φ). Em Macapá e
Santana, com 0% de migração, abstencionistas→Lula sobe de 2,6% para 7,6% e
eliminados→Lula de 62% para 84%. A leitura do relatório ("o modelo está
trocando migração por abstenção diferencial") não corresponde ao que o
ajuste faz: a troca é entre migração direta e conversão quase total dos
eleitores dos candidatos eliminados.

**Influência** (`07_amapa_influencia.csv`): excluir qualquer município ou
zona muda a taxa estadual entre 9,0% e 10,9% (sem Macapá: 6,4%). Mas
excluir as seções com |Δcomparecimento| > 10 pontos (497 seções) leva a taxa
a **3,5%** no estado e **3,0%** em Macapá e Santana; com > 5 pontos
(1.345 seções excluídas, ficam 569), a 1,0% e 1,3%. A migração estimada é
sustentada pelas seções em que o comparecimento mudou muito, exatamente onde
a composição dos votantes entre os turnos é mais diferente e a constância é
menos plausível.

**Fronteira de heterogeneidade** (`07_amapa_fronteira.csv`, programa linear
com as 1.914 seções): a fração mínima do eleitorado cujo comportamento
precisa desviar de uma matriz comum para reproduzir todas as seções é 4,42%
com a migração livre (10,0%) e **4,51% com migração zero**; em Macapá e
Santana, 3,21% contra 3,26%. Uma diferença de 0,05 a 0,1 ponto percentual do
eleitorado separa as duas hipóteses: sem a hipótese de constância, a
migração no Amapá não é identificada.

**Síntese para o AP.** Observação: queda de comparecimento de 8 pontos e
realinhamento forte nas seções de maior variação de comparecimento.
Hipóteses compatíveis: (1) migração direta de 8 a 11% em Macapá e Santana;
(2) conversão quase total dos eleitores dos candidatos eliminados mais
mobilização local; (3) heterogeneidade de comportamento entre seções da
ordem de 0,1% do eleitorado. Inferência: sob constância, (1) ajusta melhor
que (2) por 145 unidades de deviance escalada; sem constância, as três são
equivalentes. A "anomalia" é um resultado de modelo, não uma inconsistência
de dados (BU = detalhe por seção em todas as 1.914 seções).

### 4.8 Validação preditiva fora da amostra (prompt, seção 11)

`auditoria_08_validacao_cruzada.py`: em cada UF, os municípios da amostra são
divididos em 5 grupos; cada modelo é ajustado em 4 e avaliado nas seções do
quinto (nenhuma seção do município de teste entra no treino; no DF o grupo é
a zona). Médias nacionais ponderadas pelos eleitores
(`08_validacao_cruzada_nacional.csv`):

| Modelo | Log-verossimilhança preditiva por eleitor | Erro absoluto médio da participação de Lula | RMSE | Cobertura do intervalo de 95% | Maior desvio de calibração por decil |
|---|---:|---:|---:|---:|---:|
| M0 — constância | −1,08968 | 1,71 pp | 2,19 pp | 95,8% | 1,1 pp |
| M1 — taxas × margem municipal | −1,08969 | **1,68 pp** | 2,17 pp | 95,8% | 0,7 pp |
| M2 — preferência latente | −1,08977 | 1,71 pp | 2,19 pp | 95,3% | 0,6 pp |

Por região (`08_validacao_cruzada_por_regiao.csv`), M1 é melhor no Sul,
Sudeste e Centro-Oeste e pior no Norte; as diferenças são de décimos de
ponto. Os três modelos preveem os agregados das seções não usadas no ajuste
com erro de 1,5 a 2 pontos e intervalos bem calibrados.

**As duas capacidades são distintas.** Nos dados sintéticos
(`08_validacao_cruzada_sintetica_A_vs_B2.csv`), os cenários A (migração
verdadeira 0,24%) e B2 (9,9%) têm esperanças idênticas por seção; a mesma
validação cruzada dá log-verossimilhança preditiva −1,0948 e −1,0942, erro
absoluto 1,01 e 1,13 pp, cobertura 94,5% e 96,2%. O modelo prevê os
agregados igualmente bem nos dois mundos e recupera as transições só em um
deles. Capacidade preditiva agregada não é evidência sobre fluxos
individuais.

### 4.9 Voto legislativo × presidencial (prompt, seção 10)

`auditoria_09_legislativo_limites.py`, `09_limites_voto_cruzado.csv`: limites
de Fréchet por seção (todas as 499 mil), 1º turno, mesma população
(comparecimento):

| Eleitores de … para deputado federal | → Lula | → Flávio |
|---|---|---|
| PL (25,8 mi) | 0,7% a 88,6% | 4,4% a 98,3% |
| outros partidos de direita (27,7 mi) | 4,6% a 91,2% | 3,6% a 91,5% |
| centro (30,5 mi) | 8,8% a 92,7% | 2,4% a 85,9% |
| federação do PT (17,5 mi) | 4,0% a 99,8% | 0,03% a 92,6% |

A estimativa ecológica do relatório (5,4% dos eleitores do PL para deputado
votaram em Lula) está dentro dos limites, mas os limites não a confirmam: a
aritmética admite de 0,7% a 88,6%. A classificação em blocos (PL; direita;
centro; federação do PT; outros de esquerda) segue Bolognesi, Ribeiro e
Codato (2023) com posicionamento próprio de partidos novos, e o relatório já
faz as ressalvas sobre coligações, voto de legenda e oferta de candidatos. A
razão entre o voto presidencial e o voto no partido (2,07 em 2026; 2,60 em
2022; 3,95 em 2018) é um fato oficial; o resto (frequência de voto cruzado)
é estimativa ecológica sujeita às mesmas limitações das seções 4.1 e 4.2.
Os dados permitem **limitar** o voto cruzado, não estimar sua frequência sem
hipóteses.

### 4.10 Anomalias e revisão histórica (prompt, seções 13 e 15)

- As anomalias do relatório (12 municípios sinalizados, I de Moran 0,34,
  Macapá/Santana) são resíduos de um modelo cuja hipótese de constância é
  rejeitada; parte do agrupamento espacial dos resíduos é a própria
  dependência de contexto que M1/M2 modelam. Com φ correto (mediana 5), os
  resíduos padronizados do relatório (que já usam τ² de DerSimonian-Laird)
  continuam válidos como ordenação, mas os p-valores por seção não.
  Classificação da força probatória: outliers estatísticos (12 municípios,
  2 seções com migração mínima de 4 eleitores) — fraca; heterogeneidade
  regional (Moran) — explicação de modelo; diferença entre registros oficiais
  — nenhuma encontrada; evidência relevante para irregularidade — nenhuma.
- Série histórica: três eleições (2018, 2022, 2026). A raridade estatística
  da "mobilização assimétrica" de 2026 não pode ser estimada com três
  pontos; o relatório a descreve como "a característica mais incomum", o que
  é uma comparação descritiva, não uma probabilidade. Além disso, a
  comparação com 2018 e 2022 usa as mesmas taxas ecológicas, sujeitas ao
  mesmo viés; só a comparação de agregados oficiais (válidos +3,0 por 100
  aptos contra +0,2 e −1,5; brancos/nulos −1,15 contra +0,16 e +0,53) é
  fato.

### 4.11 Recalculo com todas as seções (arquivo completo do 2º turno)

Em 27/10/2026, 00h50, a votação por candidato nas 499.205 seções do 2º turno
foi obtida (seção 2.2). As análises por seção da auditoria foram refeitas com
todas as seções (497.897 após excluir exterior e seções sem aptos; saídas com
sufixo `_todas`), e o pipeline original (`analise_03`) passou a usar todas as
seções no nível "seção". Comparação com a amostra de 50.821 BUs:

| Resultado | Amostra de BUs | Todas as seções | Tabela |
|---|---:|---:|---|
| Posto / número de condição | 5 / 32 a 67 | 5 / 32 a 67 | `01_condicionamento_por_uf_todas.csv` |
| Goodman sem restrições, Flávio→Lula | −0,025 (−0,027 a −0,022); 19 UFs negativas | **−0,024 (−0,026 a −0,022); 22 UFs negativas** | `01_goodman_wls_nacional_todas.csv` |
| Goodman, Lula→Lula | 1,016 | 1,014 | idem |
| Goodman, brancos/nulos→Lula / abst.→Lula / eliminados→Lula | 0,624 / 0,091 / 0,447 | 0,623 / 0,092 / 0,449 | idem |
| Inicializações: UFs com Flávio→Lula > 0 no EM | AP 9,9%, AM 2,0%, MA 1,6%, PI 1,5%, CE 1,5%, RR 1,0%, TO 0,9%, AC 0,8% | AP 10,0%, AM 3,1%, PI 2,0%, TO 1,4%, CE 1,3%, RR 1,3%, MA 1,2%, AC 0,4% | `03_multi_start_por_uf_todas.csv` |
| φ multinomial / φ de transição independente (medianas) | 1,10 / 4,97 | 1,06 / 5,15 | `03_phi_duas_variancias_todas.csv` |
| M0 / M1 / M2: Flávio→Lula | 0,20% / 0,11% / 0,60% | 0,20% / 0,13% / 0,54% | `05_taxas_nacionais_por_modelo_sem_bootstrap_todas.csv` |
| M0 / M1 / M2: brancos/nulos→Lula | 60,9% / 59,7% / 31,2% | 60,8% / 59,9% / 31,2% | idem |
| M0 / M1 / M2: eliminados→Lula | 42,4% / 40,9% / 58,7% | 42,6% / 40,9% / 59,0% | idem |
| Deviance M0 / M1 / M2 | 131.152 / 126.595 / 134.750 | 1.271.369 / 1.231.648 / 1.307.945 | `05_ajuste_por_uf_todas.csv` |
| Limites de Fréchet por seção, Flávio→Lula | 0 a 77,3% (amostra, sem expansão) | **0 a 77,8%** (20 eleitores a 43,6 mi) | `resultados/tabelas/01_limites_secao_todas.csv` |
| Votos de Lula além de Lula(1T) + eliminados, soma por unidade | 263.686 (amostra) | **2.588.877** (por seção; 1.837.161 por município) | `resultados/tabelas/01_quantidades_minimas.csv` |
| Migração mínima Flávio→Lula obrigatória | 4 eleitores em 2 seções | **20 eleitores em 10 seções** | idem |

| Limites LP sob S1 (fidelidade ≥ 90%), Flávio→Lula / Lula→Flávio | 0 a 11,1% / 0 a 9,2%; 1.931 seções impossíveis (3,8%) | **0 a 11,1% / 0 a 9,2%**; 17.298 seções impossíveis (3,5%) | `01_limites_lp_conjuntos_hipoteses_todas.csv` |
| Limites LP sob S4 (fidelidade ≥ 95%), Flávio→Lula | 0 a 9,0% | 0 a 9,1%; 39.341 seções impossíveis (7,9%) | idem |
| Modelo A por seção, Flávio→Lula, bootstrap por município (percentil) | 0,20% (0,13 a 0,32); 1.000 réplicas | **0,20% (0,11 a 0,27)**; 200 réplicas | `03_bootstrap_1000_todas.csv` |
| Brancos/nulos→Lula, bootstrap por município | 60,9% (57,5 a 61,4) | 60,8% (57,4 a 61,2) | idem |
| Efeito de desenho (variância por município / por seção) | 2,8 (Flávio→Lula); 8,3 (brancos/nulos) | **16,5; 80,7** | idem |
| Teste de teto 0% por seção: χ² / p / p corrigido pelo efeito de desenho | 83,9 / 8 × 10⁻¹¹ / 0,025 | **483,0 / < 10⁻¹⁵ / 0,033** | `03_teste_teto_por_nivel_todas.csv` |
| Teste de teto 5% por seção: p / p corrigido | 0,0009 / 0,046 | 2 × 10⁻⁷ / **0,147** | idem |
| Teste de teto 0% por zona (todas as 7.540) / por município (5.757) | 0,90 (amostra agregada) / 0,82 | **0,66 / 0,82** | idem |
| Taxas por zona: Flávio→Lula / brancos/nulos→Lula / eliminados→Lula | 0,13% / 59,8% / 46,1% | 0,11% / 57,3% / 47,5% | idem |

Com dez vezes mais seções, o χ² do teste por seção sobe de 84 para 483,
mas o efeito de desenho sobe de 2,8 para 16,5, e o p-valor corrigido fica
igual (0,03): a informação adicional das seções do mesmo município é quase
toda redundante para esse teste. Agregadas por zona, as 7.540 zonas do país
não rejeitam nenhum teto (p = 0,66 para 0%).

| Fronteira de heterogeneidade: fração desviante com migração 0% / 10% | 2,75% / 3,13% | **2,77% / 3,14%** | `01_fronteira_heterogeneidade_nacional_todas.csv` |
| Família construtiva (compensação só em Flávio e abstenção): seções em que cabe δ = 1 / 2 pontos | 30% / 11% | 28% / 16% | `01_equivalentes_construtivos_todas.csv` |

| Modelo A do pipeline (nível "seção" = todas), Flávio→Lula | 0,20% (0,12 a 0,32) | 0,20% (0,10 a 0,26) | `resultados/tabelas/03_matriz_transicao_nacional_2026.csv` |
| Idem, brancos/nulos→Lula / abst.→Lula / eliminados→Lula | 60,8% / 10,2% / 42,4% | 60,7% / 10,2% / 42,6% | idem |
| Idem, Cury / Renan Santos / Caiado → Lula | 54% / 40% / 32% | 54% / 40% / 32% | idem |
| Teste de teto 0% (pipeline): UFs que rejeitam a 5% / com Bonferroni | 4 / 1 (AP) | 7 / 6 (AP, AM, PI, CE, MA, TO) | `resultados/tabelas/03_teste_migracao_2026_secao.csv` |
| AP, Flávio→Lula, bootstrap por município (pipeline) | 9,9% (0 a 13,5%; 400 seções) | 10,0% (0 a 11,5%; 1.914 seções) | `resultados/tabelas/03_matriz_transicao_por_uf_2026.csv` |

Com todas as seções o teste por seção do pipeline passa a rejeitar o teto
0% em sete UFs (AP, AM, PI, CE, MA, TO e mais uma a 5%), seis delas após
Bonferroni; é o mesmo teste que, corrigido pelo efeito de desenho (16,5),
dá p = 0,033 no conjunto, e que não rejeita nada quando as mesmas seções são
agregadas por zona. As taxas livres dessas UFs (1,2% a 3,1%, AP 10%) são as
mesmas da amostra; o que mudou foi o número de seções, não a evidência por
eleitor. As tabelas de `resultados/tabelas/` e o painel foram regerados com
a base completa (`analise_03b`, `06`, `07`, `08`, `09`, `10`); o Modelo B e
o Monte Carlo (`analise_04`, `05`) não foram refeitos (o Modelo B usa 4.000
seções sorteadas; o Monte Carlo é municipal).

Leitura: multiplicar por dez o número de seções não muda nenhuma conclusão
da auditoria. A regressão sem restrições continua dando coeficientes
impossíveis (agora negativos em 22 UFs), a sobredispersão real continua
cinco vezes a multinomial, e as três especificações continuam repartindo
os votos de Lula de formas diferentes com a mesma migração abaixo de 1%.
Como esperado dos dados sintéticos, o tamanho da amostra não corrige viés
de especificação nem cria identificação. O que o arquivo completo acrescenta
é aritmético: o mínimo de votos de Lula que não vêm nem dele nem dos
eliminados sobe de 1,84 milhão (por município) para **2,59 milhões** (por
seção), e passam a existir 10 seções em que alguma migração direta
Flávio→Lula é obrigatória (20 eleitores no total).

---

## 5. Comparação entre modelos

| Método | Hipótese que identifica | Flávio→Lula | Brancos/nulos→Lula | Eliminados→Lula | Abst.→Lula | Ajuste / previsão | Fonte |
|---|---|---|---|---|---|---|---|
| Limites de Fréchet (S0) | nenhuma | 0 a 77,8% | 0 a 100% | 0 a 100% | 0 a 99,6% | exato | 01_limites_lp… |
| Limites sob fidelidade ≥ 90% (S1) | fidelidade | 0 a 11,1% | 0 a 100% | 0 a 98,5% | 0 a 48,2% | exato | idem |
| Limites sob S3 | S1 + abstenções limitadas | 0 a 12,9% | 0 a 100% | 0 a 98,5% | 0 a 30,1% | exato | idem |
| Fronteira de heterogeneidade | matriz comum + desvio mínimo | 0 a 10% custa 0,38 pp do eleitorado | 61% → 51% ao impor 10% | 40% → 13% | 10,6% → 4,4% | exato | 01_fronteira… |
| Goodman sem restrições | constância | −2,5% (IC −2,7 a −2,2) | 62,4% | 44,7% | 9,1% | — | 01_goodman… |
| Modelo A (EM), seção | constância + piso | 0,20% (0,13 a 0,32) | 60,9% | 42,4% | 10,3% | dev. 131.152; MAE 1,71 pp | 03_bootstrap_1000; 08 |
| Modelo A, zona / município (amostra) | constância | 0,13% / 0,10% | 59,8% / 56,2% | 46,1% / 50,7% | 9,4% / 9,0% | — | 03_teste_teto_por_nivel |
| Modelo A, todos os municípios | constância | 0,11% | 53,0% | 52,6% | 8,9% | — | idem |
| Modelo B, prior neutra / fidelidade / troca | constância + covariáveis + prior | 0,23% / 0,42% / 0,75% | 57,5% / 54,7% / 54,6% | 38,7% / 39,2% / 38,5% | 10,8% / 11,2% / 11,1% | PPC cobertura 96,7% | 04_bayes_… |
| M1 (margem municipal) | forma funcional em z | 0,11% (0,08 a 0,26) | 59,7% (58,5 a 60,5) | 40,9% (40,2 a 42,6) | 10,5% | dev. 126.595; MAE 1,68 pp | 05_…; 08 |
| M2 (preferência latente) | forma funcional em π | 0,60% (0,49 a 0,78) | 31,2% (30,8 a 31,5) | 58,7% (57,5 a 60,4) | 9,9% | dev. 134.750; MAE 1,71 pp | idem |
| Sintético B2 (verdade 10%) → Modelo A | — | estimado 0,24% | estimado 58% (verdade 25%) | estimado 42% (verdade 17%) | estimado 10,5% (verdade 4,6%) | idêntico ao cenário A | 02_sintetico… |

Leitura: quanto mais forte a hipótese, mais estreito o resultado; os
modelos concordam entre si na migração porque compartilham a hipótese de
uma matriz comum à UF (ou a forma funcional), não porque a migração esteja
determinada; e as conversões de não votantes e de eliminados mudam de 20 a
30 pontos entre especificações igualmente capazes de prever os agregados.

---

## 6. Resultados que permaneceram robustos

1. Reconciliação oficial, identidades contábeis e conferência entre as três
   fontes do TSE.
2. Limites aritméticos: eliminados insuficientes para o crescimento de Lula
   (mínimo de 1,06 a 1,84 milhão de votos de outras origens); pelo menos 5,04
   milhões de válidos novos por município; migração direta mínima zero.
3. Fidelidade elevada aos finalistas: imposta a 90%, só 3,8% das seções a
   contradizem; os limites e todos os modelos a colocam acima de 95% a 98%.
4. Capacidade preditiva agregada dos modelos (seção 4.8) e estabilidade
   numérica do EM (sem máximos locais relevantes fora da direção plana).
5. Convergência do Modelo B com cadeias longas e reprodução das suas taxas.
6. Resultado histórico agregado: 2026 difere de 2018 e 2022 nos válidos e
   nos brancos/nulos (fatos oficiais).

## 7. Resultados que mudaram

1. "Migração Flávio→Lula entre 0,02% e 0,8% em todos os modelos" → **não
   identificada**; estimativas pontuais são artefato do piso em zero;
   conjunto identificado sob fidelidade ≥ 90%: 0 a 11%; sob 95%: 0 a 9%.
2. "p < 0,0001 contra migração zero por seção" → p = 0,025 com correção de
   desenho e p = 0,90 na mesma amostra agregada por zona; não é evidência
   forte.
3. "61% dos brancos/nulos e 10% dos abstencionistas foram para Lula" →
   estimativas condicionais a uma hipótese rejeitada; variam de 53% a 61% e de
   8,9% a 10,8% só com a unidade de agregação; viés de 20 pontos ou mais em
   cenários sintéticos com abstenção diferencial; não restritas por
   hipóteses moderadas (0 a 100%).
4. "Correlação 0,78 e 0,67 voto de Lula por válido adicional" → aritmética
   parte-todo; a fração do ganho para Lula é menor onde os válidos cresceram
   mais.
5. "Os dados, e não a prior, determinam a ordem de grandeza" (Modelo B) →
   a prior move a migração por um fator de três (0,23% a 0,75%).
6. "Macapá/Santana: o modelo troca migração por abstenção diferencial" → a
   troca é com a conversão dos eleitores dos eliminados; a estimativa depende
   das seções de maior variação de comparecimento; sem constância, migração
   zero e 10% são equivalentes a menos de 0,1% do eleitorado.
7. H3 ("mobilização de abstencionistas e brancos/nulos contribuiu para o
   crescimento de Lula") → o sentido da contribuição é consequência
   aritmética (alguém além dos eliminados deu 1,06 a 1,84 milhão de votos a
   Lula, e os brancos/nulos e abstencionistas são a origem mais plausível);
   a magnitude (3,6 e 3,4 milhões) é hipótese condicional, não medida.

## 8. Limitações não resolvidas

- Votação presidencial por seção no 2º turno indisponível; tudo o que é
  por seção usa a amostra de 50.821 BUs.
- Nenhuma fonte independente de comportamento individual (painel ou
  pesquisa pós-eleitoral com os mesmos respondentes nos dois turnos) estava
  disponível para esta auditoria; sem ela, a origem dos votos de Lula
  permanece no conjunto identificado, não num ponto.
- Os modelos M1 e M2 são hipóteses alternativas, não hipóteses mais fracas;
  identificam porque restringem a forma da dependência entre taxas e
  composição. Em 17 UFs o otimizador de M1 parou no limite de iterações,
  e as réplicas do bootstrap herdam essa convergência incompleta (intervalos
  assimétricos, seção 4.4). O bootstrap de M1 e M2 usa 100 réplicas por UF
  na amostra de BUs (31 minutos com 10 processos); não foi refeito com
  todas as seções, cujas estimativas pontuais estão na seção 4.11.
- A fronteira de heterogeneidade usa subamostra aleatória de 600 seções
  por UF (a versão com 1.500 foi interrompida por tempo: cerca de 6 minutos
  por programa linear); o Amapá foi calculado com todas as 1.914 seções.
- Os cenários sintéticos são escolhas desta auditoria; outros mecanismos
  podem produzir vieses diferentes. O gerador não reproduz a estrutura
  espacial real (vizinhança), só a hierarquia estado/município.
- O Modelo C (Monte Carlo) não foi refeito; sua leitura no relatório já era
  qualificada.
- Anomalias: não foram comparadas com fontes documentais de auditoria (atas,
  logs de urna), fora do escopo.
- Correção por efeito de desenho no teste de teto é aproximada (razão de
  variâncias do bootstrap).

## 9. Conclusões cientificamente sustentáveis

**A. Fatos diretamente observados.** Tabela nacional reconciliada; variação
de válidos, brancos/nulos, abstenção e comparecimento por seção, município e
UF; votos legislativos; igualdade entre fontes do TSE; mudanças de versão no
CDN.

**B. Consequências matemáticas necessárias.** Pelo menos 1,06 milhão
(nacional) a 1,84 milhão (por município) de votos de Lula no 2º turno não
vieram nem de Lula nem dos eliminados; pelo menos 5,04 milhões de válidos do
2º turno não vieram de válidos do 1º; migração direta entre finalistas não é
obrigatória em nenhum município e em 50.819 de 50.821 seções; sob fidelidade
≥ 90%, Flávio→Lula ≤ 11,1% e Lula→Flávio ≤ 9,2%; a correlação Δválidos ×
ΔLula de 0,74 e o coeficiente de 0,80 decorrem da identidade contábil.

**C. Estimativas condicionais.** Sob constância das taxas dentro da UF (ou
dentro de estratos mais finos), a matriz é identificada e dá Flávio→Lula de
0,1% a 0,3% (piso), brancos/nulos→Lula de 53% a 61%, abstencionistas→Lula de
9% a 11%, eliminados→Lula de 42% a 53% conforme a unidade; sob taxas que
variam com a margem municipal (M1): migração 0,11% (IC 95% de 0,08 a
0,26), brancos/nulos→Lula 60%, eliminados→Lula 41%; sob preferência
latente dos não votantes (M2): migração 0,60% (0,49 a 0,78),
brancos/nulos→Lula 31%, eliminados→Lula 59%. Sob as priors
do Modelo B, migração de 0,2% a 0,8%. A hipótese de
constância é contradita pelo estimador irrestrito (coeficientes fora de
[0, 1]) e pela sobredispersão (φ ≈ 5).

**D. Hipóteses não identificadas.** Migração Flávio→Lula entre 0 e cerca de
10% com compensação por abstenção diferencial ou mobilização dependente do
contexto (cenários B2 e E reproduzem os agregados com a mesma qualidade);
qualquer repartição dos 7 milhões de votos "novos" de Lula entre
brancos/nulos, abstencionistas e eliminados compatível com os limites;
migração de 8% em Macapá/Santana contra conversão quase total dos
eleitores dos eliminados ou heterogeneidade local de 0,1% do eleitorado.
Nenhuma delas é demonstrada nem descartada pelos dados
agregados.

Para cada afirmação relevante do relatório, evidência, método, premissas,
incerteza, sensibilidade, alternativas e grau de confiança estão na tabela
`resultados/auditoria/tabelas/afirmacoes_revisadas.csv`.

## 10. Respostas às perguntas finais (prompt, seção 19)

1. **Os resultados oficiais podem ser explicados sem migração expressiva de
   Flávio para Lula?** Sim. Com migração zero, os agregados nacionais, por UF,
   por município e por seção são reproduzíveis (limites de Fréchet;
   fronteira de heterogeneidade quase plana). Também podem ser explicados
   com migração de 5 a 10%, com a mesma qualidade. "Podem ser explicados
   sem" não é "foram produzidos sem".

2. **Os dados determinam a taxa ou só a limitam?** Só a limitam. Sem
   hipóteses: 0 a 78%. Com fidelidade mínima de 90% aos dois finalistas: 0 a
   11,1%; com 95%: 0 a 9,0%. Um valor pontual só existe sob uma hipótese de
   constância (ou de forma funcional) que os dados contradizem.

3. **A estimativa de 0,20% permanece válida quando se relaxam as
   hipóteses?** Não. Ela é o piso em zero de um estimador cuja solução livre
   é −2,5%; varia de 0 a 1,5% entre ótimos equivalentes em cinco UFs; muda
   com a unidade (0,10% a 0,20%); e, em dados sintéticos com compensação
   dependente do contexto, o mesmo estimador devolve 0,24% para migrações
   reais de 5, 10 e 15%. Sob M1 e M2 (taxas dependentes do contexto), 0,11%
   (0,08 a 0,26) e 0,60% (0,49 a 0,78): abaixo de 1%, mas pela mesma razão
   estrutural.

4. **A conversão de brancos/nulos para Lula é robusta?** Não como medida.
   Sob constância, 53% a 61% conforme a unidade; sob o Modelo B, 55% a 57%;
   sob M1, 60%; sob M2, **31%** (com eliminados→Lula em 59% em vez de
   42%); sob hipóteses moderadas sem constância, 0 a 100%. Em
   dados sintéticos com abstenção diferencial, o viés chega a 20 pontos com
   intervalos que nunca cobrem a verdade. O que é robusto é a consequência
   aritmética de que entre 1,06 e 1,84 milhão de votos de Lula vieram de
   brancos/nulos, abstencionistas ou eleitores de Flávio.

5. **Existem cenários alternativos substancialmente diferentes com a mesma
   qualidade estatística?** Sim: os cenários B2 e E dos dados sintéticos
   reproduzem, por construção ou na prática, a mesma verossimilhança e a
   mesma previsão fora da amostra com migrações de 3,5% a 15%; no Amapá,
   migração zero e 10% diferem em 0,1% do eleitorado na fronteira de
   heterogeneidade.

6. **Qual é a amplitude real da incerteza sobre a origem dos votos
   adicionais de Lula?** Dos 10,38 milhões de votos a mais, até 9,32 milhões
   podem ter vindo dos eliminados e pelo menos 1,06 milhão de outras
   origens; cada origem individual (eliminados, brancos/nulos,
   abstencionistas, Flávio) tem conjunto identificado que vai de zero ao
   limite de Fréchet, e a migração direta vai de 0 a cerca de 11% dos
   eleitores de Flávio (até 6,2 milhões de votos) sob fidelidade de 90%. A
   amplitude é da ordem dos próprios totais; as estimativas pontuais
   publicadas (3,9; 3,6; 3,4; 0,1 milhão) são uma solução entre muitas.

7. **Existem anomalias estatísticas relevantes não explicadas pelos
   mecanismos testados?** Não foi encontrada inconsistência entre registros
   oficiais. Os padrões atípicos (Macapá/Santana; resíduos agrupados; 12
   municípios) são explicáveis por dependência de contexto e por variação de
   comparecimento, e também por migração local; os dados agregados não
   decidem. A mobilização assimétrica nacional é um fato de agregados cuja
   origem individual não é identificada.

8. **Quais resultados resistem aos experimentos adversariais?** A fidelidade
   elevada aos finalistas (recuperada em todos os cenários, viés < 2 pp); a
   detecção de migração quando a compensação é constante (poder 100%); a
   previsão agregada. Não resistem: a migração sob compensação dependente do
   contexto; as conversões de não votantes sob abstenção diferencial; o
   teste de teto como teste de migração.

9. **Quais conclusões anteriores precisam ser reformuladas ou retiradas?**
   Reformuladas: Pergunta 3 (de "sustentada" para "indeterminada / não
   identificável"); Pergunta 4 (de "sustentada" para "associação
   aritmética; comportamento não identificado"); H1 e H3 (de "sustentada"
   para "sustentada como limite / consequência aritmética; magnitudes
   condicionais"); conclusão 3 do resumo (Amapá: a troca é com os eleitores
   dos eliminados, e depende das seções de maior variação de comparecimento);
   a afirmação de que "os dados, e não a prior, determinam a ordem de
   grandeza" (a prior move a migração por um fator de 3). Retiradas: a
   leitura de "p < 0,0001" como rejeição forte da migração nula e a de
   "0,20% (0,12–0,32)" como intervalo para a migração real. Mantidas:
   integridade, aritmética, mobilização assimétrica como fato de agregados,
   comparação histórica dos agregados.

10. **Qual é a explicação estatisticamente mais bem sustentada?** Nenhuma
    explicação individual é identificada pelos dados agregados. O que se
    sustenta conjuntamente é: fidelidade alta aos finalistas (limites e
    todos os modelos); entrada de pelo menos 5 milhões de válidos novos e de
    pelo menos 1,06 milhão de votos de Lula de origem diferente de Lula e
    dos eliminados (aritmética); e um conjunto de combinações de migração
    (0 a cerca de 10%) e mobilização (brancos/nulos, abstencionistas) que
    ajustam e preveem igualmente bem. Entre essas combinações, a que o
    relatório publicou (migração ≈ 0, mobilização fortemente assimétrica) é
    a solução de um estimador sob uma hipótese rejeitada; a que atribui
    parte do crescimento a migração moderada é igualmente compatível. Os
    dados não permitem decidir entre elas; uma decisão exigiria dados de
    painel ou pesquisa pós-eleitoral com os mesmos respondentes nos dois
    turnos, que não existiam para esta auditoria.
