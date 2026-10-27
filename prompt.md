# PROMPT — Auditoria estatística da transferência de votos nas eleições presidenciais brasileiras de 2026

## 1. Papel e objetivo

Atue como uma equipe multidisciplinar composta por:

- Cientista de dados especializado em estatística eleitoral.
- Estatístico com experiência em inferência bayesiana e modelos hierárquicos.
- Cientista político especializado em comportamento eleitoral.
- Especialista em econometria e inferência ecológica.
- Auditor independente de dados eleitorais.
- Desenvolvedor Python especializado em processamento de grandes bases de dados.

Sua missão é realizar uma **investigação estatística rigorosa, reproduzível, imparcial e baseada em dados oficiais** sobre a transferência de votos entre o primeiro e o segundo turno das eleições presidenciais brasileiras de 2026.

O estudo deverá determinar se o crescimento da votação de Luiz Inácio Lula da Silva em relação a Flávio Bolsonaro pode ser explicado pela migração dos votos dos candidatos eliminados, pela redução dos votos brancos e nulos e pelas mudanças de comparecimento do eleitorado.

Também deverá investigar se a distribuição territorial dos resultados contém padrões estatísticos atípicos que não sejam satisfatoriamente explicados pelos modelos utilizados.

**Não assuma antecipadamente que houve fraude, irregularidade ou comportamento eleitoral anormal. Também não assuma antecipadamente que todos os resultados observados são adequadamente explicados.**

Considere tanto evidências favoráveis quanto desfavoráveis a cada hipótese.

## 2. Fontes oficiais

Utilize prioritariamente dados públicos do Tribunal Superior Eleitoral (TSE):

https://dadosabertos.tse.jus.br/dataset/resultados-2026

https://dadosabertos.tse.jus.br/

Obtenha, preferencialmente:

1. Votação nominal para presidente por seção eleitoral — primeiro e segundo turnos.
2. Detalhamento da apuração por seção eleitoral.
3. Quantidade de eleitores aptos, comparecimento e abstenções.
4. Votos brancos, nulos e válidos.
5. Votação de todos os candidatos presidenciais no primeiro turno.
6. Votação para deputado federal e senador no primeiro turno.
7. Dados equivalentes das eleições de 2018 e 2022 para referência histórica.
8. Dados públicos do IBGE sobre população, renda, escolaridade, urbanização e outras variáveis relevantes.

Utilize outras fontes apenas como complemento, documentando origem, data e metodologia.

Não invente números, não substitua dados indisponíveis por estimativas sem identificação explícita e não confunda totais nacionais com dados efetivamente analisados por seção.

### Verificação e integridade

- Identifique as URLs exatas dos arquivos utilizados.
- Registre data de acesso, tamanho e, quando possível, hash SHA-256.
- Verifique o esquema dos CSVs, seus tipos e codificações.
- Identifique registros duplicados, ausentes e inconsistentes.
- Diferencie seções agregadas, reorganizadas ou transferidas entre os turnos.
- Valide os totais calculados contra os relatórios oficiais do TSE.
- Não descarte registros divergentes sem documentar o motivo.
- Respeite a distinção entre eleitores aptos, comparecimento, votos válidos e abstenção.

Utilize Python, preferencialmente com Polars ou DuckDB para processamento, Pandas para análises auxiliares, SciPy, Statsmodels e PyMC para modelagem estatística.

Caso os arquivos sejam muito grandes, processe-os por lotes, estado ou partição, sem comprometer a abrangência nacional.

## 3. Hipóteses de pesquisa

### H1 — Fidelidade do eleitorado aos finalistas

A maior parte dos eleitores que votou em Lula ou Flávio Bolsonaro no primeiro turno manteve sua preferência no segundo.

Estime, dentro dos limites dos dados agregados:

- Probabilidade de um eleitor de Lula permanecer votando em Lula.
- Probabilidade de um eleitor de Flávio permanecer votando em Flávio.
- Probabilidades de transferência entre os dois candidatos.
- Probabilidades de abstenção ou voto inválido no segundo turno.

Não imponha como premissa uma fidelidade elevada. Compare modelos com diferentes valores e distribuições a priori.

### H2 — Transferência dos candidatos eliminados

O crescimento dos finalistas foi parcialmente explicado pela transferência de votos anteriormente destinados a outros candidatos.

Investigue:

- Quais candidatos concentravam os votos potencialmente transferíveis.
- Quais localidades apresentaram maior correspondência entre votos de candidatos eliminados e crescimento de cada finalista.
- Quais combinações de transferência são matematicamente possíveis.
- Quais são estatisticamente mais compatíveis com os resultados territoriais.
- Se é possível explicar o crescimento de Lula sem migração relevante de eleitores de Flávio.

Construa intervalos de identificação para as transferências, distinguindo conclusões impostas pela aritmética de resultados dependentes de hipóteses estatísticas.

### H3 — Mobilização de abstencionistas e votos inválidos

O aumento líquido de votos válidos entre os turnos pode ter contribuído significativamente para o crescimento de Lula.

Investigue:

- Evolução das abstenções por município, zona e seção.
- Redução dos votos brancos e nulos.
- Correspondência territorial entre essas mudanças e o crescimento de cada candidato.
- Diferenças entre localidades inicialmente favoráveis a Lula e localidades inicialmente favoráveis a Flávio.
- Associação dessas mudanças com características sociodemográficas.

**Importante:** a diferença líquida entre comparecimentos ou votos válidos não identifica as pessoas que mudaram de comportamento.

Não interprete automaticamente todos os novos votos válidos como provenientes de pessoas que se abstiveram no primeiro turno.

### H4 — Coerência entre votação legislativa e presidencial

A votação obtida por candidatos e partidos de direita na Câmara dos Deputados e no Senado pode apresentar diferenças relevantes em relação à votação presidencial.

Investigue:

- Relação entre os votos para candidatos do PL e a votação presidencial.
- Relação entre votos legislativos de outros partidos e a votação presidencial.
- Frequência territorial de combinações aparentemente divergentes.
- Evidências de voto dividido (*split-ticket voting*).
- Seções com elevada votação legislativa em candidatos do PL e simultaneamente elevada votação presidencial em Lula.

Não classifique automaticamente todos os partidos não pertencentes ao PT como integrantes da direita.

Analise separadamente votos, cadeiras conquistadas, regras eleitorais, coligações, federações e particularidades dos distritos.

### H5 — Existência de padrões estatísticos atípicos

Investigue se as variações entre os turnos apresentam desvios sistemáticos não explicados adequadamente pelos modelos.

Considere:

- Variações extremas na votação de um candidato.
- Seções com mudanças incomuns de comparecimento.
- Correlações territoriais inesperadas.
- Concentração geográfica dos maiores resíduos.
- Diferenças importantes entre estados e municípios.
- Padrões que persistam após controle de composição eleitoral e variáveis socioeconômicas.
- Comparação com variações observadas em eleições anteriores.

Diferencie anomalias estatísticas, erros de modelagem, mudanças legítimas de comportamento e eventuais inconsistências de dados.

Uma anomalia estatística isolada não constitui prova de fraude.

## 4. Etapa inicial — Reconciliação matemática

Antes de qualquer inferência probabilística, reconstrua os resultados nacionais oficiais.

Produza uma tabela contendo:

| Indicador | Primeiro turno | Segundo turno | Diferença |
|---|---:|---:|---:|
| Lula | | | |
| Flávio Bolsonaro | | | |
| Outros candidatos | | | |
| Votos válidos | | | |
| Votos brancos | | | |
| Votos nulos | | | |
| Abstenções | | | |
| Comparecimento | | | |
| Eleitores aptos | | | |

Verifique se:

- As somas dos candidatos correspondem aos votos válidos.
- A soma de válidos, brancos e nulos corresponde ao comparecimento.
- Comparecimento e abstenção correspondem ao eleitorado apto, considerando eventuais diferenças de cadastro e totalização.
- O crescimento combinado dos finalistas é compatível com a quantidade de votos dos demais candidatos e a mudança líquida dos votos válidos.

Estabeleça limites matemáticos superiores e inferiores para cada transferência.

Esses limites deverão ser apresentados antes de qualquer inferência ecológica.

## 5. Análise geográfica

Crie uma base consolidada por seção eleitoral, com identificação de:

- Estado.
- Município.
- Zona.
- Seção.
- Eleitorado apto.
- Comparecimento em cada turno.
- Votos de cada candidato.
- Brancos, nulos e abstenções.

Quando as seções não forem diretamente comparáveis, agregue-as a uma unidade territorial estável e documente a perda de granularidade.

Calcule:

\[
\Delta L_i=L_{i,2}-L_{i,1}
\]

\[
\Delta F_i=F_{i,2}-F_{i,1}
\]

\[
\Delta V_i=V_{i,2}-V_{i,1}
\]

\[
O_i=V_{i,1}-L_{i,1}-F_{i,1}
\]

Onde \(i\) representa uma unidade territorial comparável.

### Pergunta central A

**Os votos válidos adicionais concentraram-se em regiões onde Lula já apresentava vantagem no primeiro turno?**

Calcule:

1. Distribuição dos aumentos de votos válidos entre regiões inicialmente favoráveis a cada finalista.
2. Diferença de comparecimento entre turnos.
3. Correlação entre votação inicial de Lula e crescimento posterior dos votos válidos.
4. Correlação entre votação inicial de Flávio e crescimento posterior dos votos válidos.
5. Modelos de regressão com controles territoriais e demográficos.
6. Sensibilidade dos resultados ao nível de agregação utilizado.

Utilize taxas e valores absolutos. Evite conclusões derivadas exclusivamente de correlações simples.

### Pergunta central B

**Os votos dos candidatos eliminados são suficientes e estatisticamente compatíveis com o crescimento observado de Lula e Flávio?**

Calcule:

1. Distribuição geográfica dos votos destinados aos demais candidatos.
2. Relação entre essa votação e o crescimento de cada finalista.
3. Limites matemáticos para transferências.
4. Matrizes probabilísticas de transferência.
5. Intervalos de incerteza.
6. Diferenças entre estimativas nacionais e regionais.

Identifique quais resultados são observados, quais são estimados e quais dependem de pressupostos.

## 6. Modelos estatísticos obrigatórios

### Modelo A — Inferência ecológica

Implemente um modelo de inferência ecológica para estimar fluxos entre:

Origem:

- Lula.
- Flávio Bolsonaro.
- Outros candidatos, individualizados quando identificável.
- Brancos e nulos.
- Abstenção.

Destino:

- Lula.
- Flávio Bolsonaro.
- Brancos e nulos.
- Abstenção.

Considere que as probabilidades de transição devem ser não negativas e somar 1 por grupo de origem.

Trate mudanças no eleitorado apto e alterações cadastrais explicitamente.

Reconheça problemas de não identificação e apresente intervalos em vez de estimativas pontuais injustificadamente precisas.

### Modelo B — Inferência bayesiana hierárquica

Implemente um modelo bayesiano que permita heterogeneidade entre:

- Estados.
- Municípios.
- Áreas urbanas e rurais.
- Diferentes padrões de votação do primeiro turno.

Utilize distribuições a priori justificadas.

Realize análises de sensibilidade com diferentes priors.

Apresente intervalos de credibilidade e verificações preditivas posteriores.

### Modelo C — Simulação de Monte Carlo

Construa pelo menos quatro famílias de cenários:

**Cenário 1:** alta fidelidade aos dois finalistas, com transferências predominantemente dos demais candidatos.

**Cenário 2:** alta fidelidade, com mobilização diferenciada de abstencionistas e eleitores que anteriormente votaram em branco ou nulo.

**Cenário 3:** transferências moderadas entre todos os grupos.

**Cenário 4:** heterogeneidade territorial relevante, com padrões distintos entre regiões.

Calibre cada cenário com restrições aritméticas reais.

Realize simulações suficientes para obter estabilidade numérica e informe diagnósticos de convergência.

Compare as distribuições simuladas com os resultados observados usando métricas preditivas adequadas, sem interpretar frequências simuladas como probabilidades reais de uma hipótese sem definição e calibração do modelo.

### Modelo D — Detecção de anomalias

Utilize métodos como:

- Resíduos padronizados e verificações preditivas.
- Regressões hierárquicas.
- Análise de dispersão.
- Detecção robusta de outliers.
- Análise de autocorrelação espacial.
- Testes de permutação apropriados.
- Comparação com eleições históricas.

Considere múltiplas comparações e diferenças de tamanho entre seções eleitorais.

Não utilize a Lei de Benford como evidência autônoma de irregularidade. Caso seja explorada, justifique previamente suas condições de aplicabilidade e limitações em dados eleitorais.

## 7. Teste específico: migração mínima entre Flávio e Lula

Estime a compatibilidade dos resultados com os seguintes limites hipotéticos para a transferência direta de eleitores de Flávio para Lula:

- 0%.
- Até 1%.
- Até 2%.
- Até 5%.
- Até 10%.

Para cada hipótese:

1. Verifique sua viabilidade matemática.
2. Determine os fluxos necessários dos demais grupos.
3. Verifique se esses fluxos são compatíveis com as restrições territoriais.
4. Estime a qualidade de ajuste dos modelos.
5. Identifique regiões com maior incompatibilidade.
6. Calcule intervalos de incerteza.
7. Analise a dependência em relação aos pressupostos.

Repita o procedimento considerando migração de Lula para Flávio.

Não trate as transferências como necessariamente unidirecionais.

Se os dados agregados não permitirem distinguir dois cenários, declare explicitamente que eles são estatisticamente não identificáveis.

## 8. Comparação histórica

Repita as principais análises, sempre que os dados permitirem, para as eleições presidenciais de 2018 e 2022.

Normalize as métricas para permitir comparações apesar das diferenças de eleitorado, comparecimento, candidatos e contexto político.

Avalie:

- Crescimento percentual e absoluto dos finalistas.
- Participação dos votos de candidatos eliminados.
- Mudança nos votos inválidos.
- Mudança no comparecimento.
- Heterogeneidade territorial das transferências estimadas.
- Distribuição dos resíduos dos modelos.

O objetivo não é presumir que todas as eleições devam apresentar o mesmo comportamento, mas construir referências empíricas para avaliar a magnitude das mudanças de 2026.

## 9. Resultados e visualizações obrigatórios

Produza:

1. Tabela nacional reconciliada entre os turnos.
2. Ranking dos estados por variação de comparecimento e votos válidos.
3. Mapa do crescimento de Lula por município.
4. Mapa do crescimento de Flávio por município.
5. Mapa da variação dos votos válidos.
6. Mapa de concentração dos votos dos candidatos eliminados.
7. Gráficos de dispersão entre essas variáveis.
8. Matrizes de transferência estimadas, com intervalos de incerteza.
9. Gráficos comparativos das simulações de Monte Carlo.
10. Lista de unidades territoriais com maiores resíduos padronizados, acompanhada de diagnóstico e ressalvas.

Identifique claramente em todos os gráficos o que é dado oficial, estimativa ou simulação.

## 10. Requisitos de auditoria e reprodutibilidade

Entregue:

- Código Python completo e executável.
- Arquivo de dependências.
- Scripts de download e validação dos dados.
- Procedimentos de limpeza e tratamento.
- Relatórios de integridade dos arquivos.
- Dados derivados, quando a redistribuição for permitida.
- Registro de parâmetros e sementes aleatórias.
- Testes automatizados de consistência.
- Instruções para reprodução integral.

Não simule resultados empíricos caso falte acesso às bases.

Se alguma etapa não puder ser executada, descreva o impedimento e mantenha a conclusão correspondente em aberto.

## 11. Relatório final

Estruture o relatório em:

### I — Resumo executivo

Apresente os principais resultados, com números, nível de confiança e limitações.

### II — Reconciliação dos votos

Demonstre matematicamente a diferença entre os turnos.

### III — Mobilização eleitoral

Identifique onde ocorreram as maiores alterações no comparecimento e nos votos válidos.

### IV — Transferências estimadas

Apresente quais fluxos são compatíveis com os resultados.

### V — Coerência legislativa e presidencial

Examine os padrões de voto dividido e as diferenças entre sistemas eleitorais.

### VI — Resultados dos testes estatísticos

Apresente efeitos estimados, intervalos, diagnósticos e qualidade do ajuste.

### VII — Anomalias e explicações concorrentes

Diferencie observações incomuns de inconsistências verificáveis.

### VIII — Limitações

Explique detalhadamente as restrições da inferência ecológica, do sigilo do voto e dos dados disponíveis.

### IX — Conclusões

Responda objetivamente:

**Pergunta 1:** O aumento de votos válidos ocorreu predominantemente em áreas inicialmente favoráveis a Lula, a Flávio ou de forma distribuída?

**Pergunta 2:** Os votos de candidatos eliminados são suficientes para explicar o crescimento dos finalistas? Quais transferências são compatíveis com os dados territoriais?

**Pergunta 3:** É possível explicar o resultado sem migração significativa de eleitores de Flávio para Lula? Sob quais premissas?

**Pergunta 4:** A mudança de abstenções, brancos e nulos apresenta associação estatisticamente relevante com o crescimento de Lula?

**Pergunta 5:** A divergência entre o desempenho legislativo do PL e a votação presidencial é consistente com padrões de voto dividido?

**Pergunta 6:** Existem padrões estatisticamente atípicos que persistem após controles e análise de sensibilidade? Qual sua magnitude e quais explicações permanecem possíveis?

**Pergunta 7:** Os resultados de 2026 diferem significativamente dos padrões históricos de 2018 e 2022, após normalização e consideração das diferenças de contexto?

Para cada pergunta, atribua um dos seguintes estados de evidência:

- Sustentada pelos dados disponíveis.
- Parcialmente sustentada.
- Não sustentada pelos dados disponíveis.
- Indeterminada ou não identificável.

Esses estados não devem ser tratados como classificações de candidatos ou partidos.

## 12. Instrução final de execução

**Não se limite a propor uma metodologia. Execute a pesquisa com os dados reais do TSE.**

Comece identificando e baixando os arquivos, processe os resultados por seção eleitoral, valide os totais nacionais e execute progressivamente os modelos.

Registre o resultado de cada etapa e suas limitações.

Priorize evidências quantitativas, transparência metodológica, reprodutibilidade e disposição para refutar as hipóteses iniciais.

Não procure apenas confirmar uma suspeita. Procure determinar quais explicações permanecem compatíveis com os dados e quais podem ser rejeitadas, indicando a força e os limites da evidência.

O produto final deverá ser um relatório científico, acompanhado dos códigos e dados necessários para auditoria independente.
