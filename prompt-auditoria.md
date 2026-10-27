# PROMPT — Auditoria científica, revisão estatística e validação adversarial das análises eleitorais de 2026

## 1. Papel e objetivo

Atue como uma equipe multidisciplinar formada por:

- Estatístico especializado em inferência ecológica e modelos hierárquicos bayesianos.
- Cientista de dados com experiência em eleições e comportamento eleitoral.
- Especialista em inferência causal, identificação parcial e análise de sensibilidade.
- Engenheiro de software Python especializado em reprodutibilidade científica.
- Auditor independente de dados eleitorais.

Sua missão é **auditar, corrigir, ampliar e validar cientificamente** as análises existentes no repositório:

**<https://github.com/ricardomaia/eleicoes_2026>**

Painel de apresentação:

<https://ricardomaia.github.io/eleicoes_2026/>

Não parta da premissa de que os resultados eleitorais são legítimos ou fraudulentos. Não procure evidências para confirmar uma conclusão preconcebida.

A investigação deve buscar determinar:

1. Quais conclusões são consequências matemáticas necessárias dos dados oficiais.
2. Quais são estimativas dependentes de pressupostos estatísticos.
3. Quais resultados são identificáveis a partir dos dados disponíveis.
4. Quais permanecem ambíguos devido à natureza agregada dos dados.
5. Quais resultados são robustos a diferentes especificações de modelo.
6. Se existem anomalias estatísticas que permaneçam relevantes após o controle de fatores conhecidos.
7. Se existem explicações alternativas capazes de reproduzir os mesmos resultados observados.

O produto final deve ser uma versão cientificamente mais sólida, reproduzível, transparente e metodologicamente conservadora do estudo.

---

## 2. Inspeção inicial do projeto

Antes de alterar qualquer código:

1. Inspecione a estrutura completa do repositório.
2. Leia o README, RELATORIO.md e demais documentos metodológicos.
3. Identifique os scripts de aquisição e tratamento de dados.
4. Identifique os modelos estatísticos utilizados.
5. Localize os datasets oficiais do TSE utilizados como referência.
6. Verifique as versões e a integridade dos arquivos.
7. Identifique dependências, sementes aleatórias e parâmetros.
8. Execute os testes existentes.
9. Reproduza os principais resultados publicados.

Crie um relatório inicial com:

- Inventário dos modelos e suas hipóteses.
- Inventário das fontes de dados.
- Resultados reproduzidos e eventuais divergências.
- Problemas metodológicos.
- Problemas de implementação.
- Problemas de documentação.
- Priorização das correções por impacto científico.

Não modifique dados originais.

Preserve resultados anteriores para permitir comparações.

Não invente números, fontes, cálculos ou resultados de experimentos que não tenham sido executados.

---

## 3. Revisão da inferência ecológica

### 3.1 Problema de identificabilidade

Os modelos atuais estimam transferências de votos entre categorias eleitorais utilizando dados agregados.

Investigue formalmente a identificabilidade dos parâmetros da matriz de transição.

Considere categorias de origem:

- Lula.
- Flávio Bolsonaro.
- Outros candidatos.
- Brancos e nulos.
- Abstencionistas.

E categorias de destino:

- Lula.
- Flávio Bolsonaro.
- Brancos e nulos.
- Abstencionistas.

Caso a estrutura temporal ou os dados oficiais exijam alterações nessas categorias, documente-as.

Construa a matriz:

\[
T_{ij}=P(Y_2=j\mid Y_1=i)
\]

Onde \(Y_1\) e \(Y_2\) representam as escolhas eleitorais nos dois turnos.

Responda:

- Os dados agregados identificam unicamente os elementos dessa matriz?
- Existem matrizes de transição substancialmente distintas que produzem os mesmos resultados?
- Qual é a dimensão do espaço de soluções observacionalmente equivalentes?
- Quais parâmetros são determinados pelos dados e quais são determinados principalmente pelas restrições e distribuições a priori?

Implemente um teste que construa matrizes alternativas capazes de reproduzir os resultados agregados com erros semelhantes.

Se possível, utilize otimização linear, programação quadrática ou métodos bayesianos para explorar o espaço de soluções.

### 3.2 Incerteza estrutural

Revise os intervalos de confiança divulgados, especialmente os associados à migração Flávio → Lula.

Diferencie explicitamente:

- Incerteza amostral.
- Incerteza dos parâmetros condicionada ao modelo.
- Incerteza de especificação.
- Incerteza de identificação.
- Incerteza decorrente da qualidade dos dados.

Investigue se os intervalos atuais são excessivamente estreitos.

Não interprete intervalos de confiança ou credibilidade condicionados a um modelo como limites absolutos para o comportamento eleitoral verdadeiro.

Produza intervalos alternativos ou conjuntos identificados quando apropriado.

---

## 4. Experimentos adversariais com dados sintéticos

Esta é uma das etapas prioritárias.

Desenvolva um gerador sintético de eleições de dois turnos no qual as transições individuais sejam conhecidas.

O gerador deve permitir controlar:

- Fidelidade aos candidatos.
- Migração entre candidatos.
- Conversão de brancos e nulos.
- Mobilização de abstencionistas.
- Desmobilização entre turnos.
- Heterogeneidade municipal e regional.
- Comportamentos correlacionados entre localidades.
- Tamanho do eleitorado.
- Preferências ideológicas latentes.
- Ruído amostral.
- Correlação espacial.

Implemente os seguintes cenários:

**Cenário A — Fidelidade elevada**

Os eleitores dos dois finalistas mantêm majoritariamente seus votos, enquanto novos votos válidos surgem da mobilização dos demais grupos.

**Cenário B — Migração compensada**

Existe migração expressiva entre os finalistas, mas mudanças simultâneas na participação eleitoral produzem resultados agregados semelhantes aos do cenário A.

**Cenário C — Abstenção diferencial**

A participação eleitoral varia entre apoiadores dos candidatos, sem necessidade de migração direta significativa.

**Cenário D — Forte heterogeneidade regional**

As transições variam significativamente entre estados e municípios, embora os resultados nacionais permaneçam semelhantes.

**Cenário E — Mistura de mecanismos**

Migração, mobilização, desmobilização e preferência ideológica variam simultaneamente.

**Cenário F — Má especificação proposital**

Os dados são gerados por um mecanismo diferente daquele pressuposto pelos modelos utilizados.

Execute os modelos existentes sem fornecer a eles conhecimento das transições reais.

Calcule:

- Viés.
- RMSE e MAE.
- Cobertura dos intervalos de 95%.
- Taxa de falsos positivos.
- Taxa de falsos negativos.
- Sensibilidade à heterogeneidade.
- Frequência de estimativas próximas aos limites paramétricos.
- Capacidade de distinguir cenários observacionalmente semelhantes.

Repita as simulações com diferentes sementes e tamanhos amostrais, informando também a incerteza Monte Carlo das métricas estimadas.

**Pergunta central:** um modelo que estima migração de 0,20% conseguiria reconhecer uma migração real de 5%, 10% ou 15% quando existissem fluxos compensatórios?

Caso não consiga, documente claramente essa limitação.

---

## 5. Comparação entre os modelos A e B

Revise o modelo de quase-verossimilhança multinomial com algoritmo EM e o modelo bayesiano hierárquico.

Investigue:

1. Sensibilidade às inicializações.
2. Máximos locais.
3. Identificabilidade dos parâmetros.
4. Dependência das distribuições a priori.
5. Capacidade de recuperar transições conhecidas.
6. Ajuste dentro e fora da amostra.
7. Influência das restrições impostas.
8. Convergência numérica.
9. Estabilidade dos intervalos.

Aumente o número de replicações bootstrap quando necessário, utilizando preferencialmente pelo menos 1.000 e, quando viável, 2.000 repetições.

Para os modelos bayesianos:

- Avalie R-hat, ESS e divergências.
- Utilize múltiplas cadeias.
- Realize verificações preditivas posteriores.
- Teste diferentes priors plausíveis.
- Investigue multimodalidade e correlações entre parâmetros.
- Documente problemas de convergência.

Não considere a concordância entre dois modelos como validação independente quando ambos compartilham pressupostos ou dependem dos mesmos dados agregados.

---

## 6. Mobilização de brancos, nulos e abstencionistas

Reavalie as estimativas segundo as quais:

- Aproximadamente 60,8% dos eleitores que votaram em branco ou nulo teriam migrado para Lula.
- Aproximadamente 1,5% teriam migrado para Flávio.
- Aproximadamente 10,2% dos abstencionistas teriam votado em Lula.
- Aproximadamente 2,7% teriam votado em Flávio.

Trate esses valores como resultados preliminares dos modelos publicados, não como fatos observados.

Investigue se essas estimativas podem surgir artificialmente devido a:

- Restrições de fidelidade.
- Erros de especificação.
- Heterogeneidade não modelada.
- Fluxos compensatórios.
- Agrupamento de eleitores com preferências diferentes.
- Dependência entre comparecimento e preferência eleitoral.

Teste modelos alternativos que permitam que a participação eleitoral dependa da preferência latente do eleitor.

Compare diferentes mecanismos de mobilização.

Procure evidências externas independentes, especialmente pesquisas em painel ou levantamentos pós-eleitorais, quando existirem dados metodologicamente adequados.

Não utilize pesquisas transversais como se acompanhassem necessariamente os mesmos indivíduos entre os turnos.

Produza uma avaliação sobre quais taxas de conversão são efetivamente identificáveis e quais permanecem dependentes de pressupostos.

---

## 7. Revisão das correlações e relações aritméticas

Revise as correlações apresentadas entre:

- Crescimento de votos válidos.
- Crescimento dos votos de Lula.
- Crescimento dos votos de Flávio.

Considere a identidade:

\[
\Delta V_{\text{válidos}}
=

\Delta V_{\text{Lula}}
+
\Delta V_{\text{Flávio}}
\]

Investigue a possibilidade de correlação parte-todo.

Desenvolva testes que distingam associações substantivas de dependências matemáticas.

Utilize métodos adequados para dados composicionais, quando aplicável.

Compare resultados absolutos, taxas normalizadas pelo eleitorado e decomposições de fluxos líquidos.

Não interprete uma correlação produzida parcialmente por identidade aritmética como evidência independente de transferência de votos.

---

## 8. Sensibilidade à agregação geográfica

Investigue diferenças entre análises por:

- Seção eleitoral.
- Município.
- Estado.
- Região.
- Brasil.

Dê atenção especial à divergência anteriormente identificada entre os testes conjuntos de migração zero por seções e por municípios.

Avalie:

- Problema da unidade espacial modificável (MAUP).
- Heterogeneidade intramunicipal.
- Dependência espacial.
- Pseudorreplicação.
- Dependência entre observações.
- Efeitos das diferentes ponderações.
- Influência de seções com tamanhos distintos.
- Alterações de composição e correspondência das seções entre turnos.

Para inferência estatística, considere erros-padrão robustos a agrupamentos, bootstrap hierárquico ou alternativas adequadas.

Reproduza os testes com as mesmas hipóteses nas diferentes granularidades, explicando por que resultados eventualmente divergem.

---

## 9. Investigação específica do Amapá

Revise as estimativas de migração Flávio → Lula em Macapá, Santana e demais municípios relevantes.

Investigue:

- Robustez dos resultados.
- Sensibilidade às priors.
- Influência da abstenção diferencial.
- Mudanças na composição do eleitorado entre turnos.
- Influência de seções atípicas.
- Intervalos de identificação.
- Ajuste de modelos alternativos.
- Impacto de múltiplas comparações.

Não atribua mudanças individuais a partir de diferenças agregadas sem explicitar os pressupostos necessários.

Avalie se a aparente anomalia permanece sob os diferentes modelos.

Apresente as conclusões separando observações, hipóteses e inferências.

---

## 10. Comparação entre eleições presidenciais e legislativas

Revise a utilização dos resultados das eleições para deputado federal e senador como evidência de coerência ou incoerência eleitoral.

Evite pressupor que:

- Todo eleitor do candidato presidencial de um partido vota no mesmo partido para deputado.
- Todo eleitor de um partido mantém a mesma preferência na eleição presidencial.
- Votos partidários legislativos correspondem diretamente a blocos ideológicos homogêneos.

Considere:

- Coligações, federações e alianças.
- Voto nominal e voto de legenda.
- Estratégias de voto dividido.
- Diferenças entre eleições proporcionais e majoritárias.
- Oferta de candidatos.
- Particularidades estaduais.
- Fragmentação partidária.

Construa comparações alternativas entre blocos políticos, explicitando a classificação utilizada.

Avalie se os dados permitem estimar a frequência de voto ideologicamente cruzado ou apenas estabelecer limites.

---

## 11. Validação preditiva e testes fora da amostra

Implemente validação espacialmente agrupada.

Treine os modelos utilizando determinados municípios ou regiões e avalie sua capacidade de prever dados não utilizados no ajuste.

Use métricas apropriadas:

- Log-verossimilhança preditiva.
- Erro absoluto.
- Erro quadrático.
- Calibração preditiva.
- Cobertura de intervalos.
- Erros por estado e região.

Evite vazamento de informações entre conjuntos de treinamento e teste.

Separe claramente duas capacidades diferentes:

1. Prever resultados eleitorais agregados.
2. Recuperar transições individuais entre turnos.

Um modelo pode apresentar boa capacidade preditiva agregada sem identificar corretamente os fluxos individuais.

---

## 12. Identificação parcial e limites de transição

Implemente uma análise complementar baseada em limites matemáticos.

Em vez de estimar somente uma matriz de transição pontual, determine conjuntos de matrizes compatíveis com os resultados agregados e com diferentes restrições defensáveis.

Utilize, quando apropriado:

- Programação linear.
- Restrições de não negatividade.
- Conservação do eleitorado.
- Limites sobre taxas de fidelidade.
- Limites sobre abstenção diferencial.
- Restrições monotônicas justificáveis.
- Otimização robusta.

Produza limites inferiores e superiores para fluxos relevantes.

Investigue especialmente a quantidade de votos de Lula que poderia ter se originado de:

- Eleitores de Flávio.
- Outros candidatos.
- Brancos e nulos.
- Abstencionistas.

Compare limites sem pressupostos fortes, limites sob pressupostos moderados e estimativas dos modelos completos.

Não apresente limites condicionais como se fossem limites universais.

---

## 13. Análise de anomalias eleitorais

Revise os testes de detecção de anomalias.

Diferencie:

- Outliers estatísticos.
- Diferenças demográficas.
- Heterogeneidade política regional.
- Erros de processamento.
- Problemas de qualidade dos dados.
- Inconsistências entre registros oficiais.
- Evidências efetivamente relevantes para investigação de irregularidades.

Inclua controles por múltiplas comparações quando necessários.

Realize testes de sensibilidade para fatores de confusão e dependência espacial.

Quando disponíveis, compare fontes independentes de evidência documental e de auditoria.

Não utilize isoladamente Benford, dígitos finais, correlações eleitorais ou valores-p para concluir pela existência ou inexistência de fraude.

Classifique cada achado conforme sua força probatória.

---

## 14. Integridade dos dados oficiais

Verifique:

- Proveniência dos datasets.
- Hashes dos arquivos.
- Versões disponíveis.
- Integridade dos boletins de urna.
- Consistência entre agregações.
- Duplicidades.
- Registros faltantes.
- Alterações de seções entre turnos.
- Tratamento de votos anulados ou pendentes.
- Correspondência dos denominadores.
- Tratamento dos eleitores aptos e do comparecimento.

Caso o projeto utilize uma amostra de 50.821 seções, avalie seu processo de seleção e represente adequadamente a incerteza amostral.

Sempre que tecnicamente viável, reproduza os cálculos sobre o conjunto integral dos dados oficiais.

A concordância entre arquivos provenientes do mesmo sistema não deve ser apresentada como uma validação inteiramente independente.

---

## 15. Revisão histórica

Amplie, quando houver dados compatíveis, a comparação com eleições anteriores.

Normalize diferenças relacionadas a:

- Tamanho do eleitorado.
- Participação.
- Votos válidos.
- Número de candidatos.
- Distribuição regional.
- Polarização.
- Regras eleitorais.

Evite calcular probabilidades de eventos raros a partir de séries históricas demasiado curtas.

Caso não existam dados comparáveis em quantidade suficiente, indique que a raridade estatística não pôde ser estimada com confiabilidade.

---

## 16. Revisão das conclusões

Reescreva as conclusões distinguindo quatro categorias:

**A. Fatos diretamente observados**

Valores extraídos ou calculados sem pressupostos comportamentais adicionais.

**B. Consequências matemáticas necessárias**

Conclusões decorrentes de identidades, restrições e limites.

**C. Estimativas condicionais**

Resultados dependentes de modelos estatísticos e pressupostos explícitos.

**D. Hipóteses não identificadas**

Explicações que permanecem possíveis, mas não são demonstradas pelos dados disponíveis.

Para cada afirmação relevante, documente:

- Evidência de suporte.
- Método.
- Premissas.
- Incerteza.
- Sensibilidade.
- Explicações alternativas.
- Grau de confiança justificável.

Revise especialmente afirmações sobre fidelidade eleitoral, migração entre candidatos, mobilização de brancos e nulos e conversão de abstencionistas.

Evite expressões como "comprovado", "demonstrado" ou "descartado" quando as evidências sustentarem apenas compatibilidade estatística.

---

## 17. Implementação e documentação

Implemente as melhorias no repositório, mantendo compatibilidade com o painel existente sempre que possível.

Crie ou atualize:

- Scripts de simulação.
- Testes automatizados.
- Testes de regressão.
- Relatórios de convergência.
- Diagnósticos de identificação.
- Análises de sensibilidade.
- Visualizações comparativas.
- Documentação metodológica.
- Instruções de reprodução.

Crie um arquivo:

`AUDITORIA_METODOLOGICA.md`

Esse documento deve apresentar:

1. Resumo executivo.
2. Problemas identificados.
3. Correções implementadas.
4. Experimentos realizados.
5. Resultados numéricos.
6. Comparação entre modelos.
7. Resultados que permaneceram robustos.
8. Resultados que mudaram.
9. Limitações não resolvidas.
10. Conclusões cientificamente sustentáveis.

Atualize o relatório principal somente após validar os novos resultados.

Mantenha rastreabilidade entre cada conclusão e seu código ou dataset de origem.

Não substitua resultados originais silenciosamente. Registre mudanças metodológicas e seus efeitos.

---

## 18. Critérios de aceitação

O trabalho somente estará concluído quando:

- Os resultados publicados anteriormente tiverem sido reproduzidos ou suas divergências explicadas.
- Os modelos tiverem sido submetidos a experimentos adversariais.
- A incerteza estrutural e a identificabilidade tiverem sido avaliadas.
- A análise de brancos, nulos e abstencionistas tiver sido revisada.
- As correlações parte-todo tiverem sido avaliadas.
- A divergência entre granularidades geográficas tiver sido investigada.
- Os resultados específicos do Amapá tiverem sido submetidos à análise de sensibilidade.
- Os diagnósticos bayesianos e os intervalos bootstrap tiverem sido revisados.
- Os resultados robustos e não robustos tiverem sido diferenciados.
- A documentação tiver sido atualizada.
- Os testes automatizados tiverem sido executados.

Se recursos computacionais, dados ou tempo de execução impedirem a conclusão de algum item, documente-o expressamente como pendente, sem apresentar resultados simulados ou presumidos.

---

## 19. Perguntas científicas finais

Ao final da auditoria, responda objetivamente:

1. Os resultados oficiais de 2026 podem ser explicados sem migração expressiva de eleitores de Flávio para Lula?

2. Os dados permitem determinar a taxa dessa migração ou apenas limitar um conjunto de valores possíveis?

3. A estimativa original de aproximadamente 0,20% permanece válida quando se relaxam as hipóteses do modelo?

4. A conversão estimada de brancos e nulos para Lula permanece robusta em diferentes especificações?

5. Existem cenários alternativos substancialmente diferentes que reproduzem os resultados com qualidade estatística semelhante?

6. Qual é a amplitude real da incerteza sobre a origem dos votos adicionais de Lula?

7. Existem anomalias estatísticas relevantes que não sejam explicadas pelos mecanismos testados?

8. Quais resultados resistem aos experimentos adversariais?

9. Quais conclusões anteriores precisam ser reformuladas ou retiradas?

10. Qual é a explicação estatisticamente mais bem sustentada, considerando conjuntamente ajuste, capacidade preditiva, identificabilidade, robustez e evidências independentes?

Se os dados não permitirem decidir entre explicações concorrentes, declare explicitamente essa impossibilidade.

**Princípio fundamental: não confunda a capacidade de um modelo reproduzir resultados agregados com a capacidade de identificar os comportamentos individuais que os produziram.**

Inicie pela auditoria do repositório e pela reprodução dos resultados existentes. Em seguida, execute as revisões prioritárias e implemente as correções sustentadas pelos testes, sem exigir confirmação a cada etapa.
