/* Aba Investigando — registro de denúncias de fraude analisadas.
   Carregado antes de app.js. invMontar() é chamada por renderizar.investigando (app.js)
   e usa o que app.js define ($, esc). Cada caso guarda as publicações (com cópia local em
   investigando/arquivo/, para o caso de serem apagadas), o contexto, cada alegação com a
   verificação feita e o resultado, as falácias segundo o guia de Stephen Downes e as
   respostas publicadas. Os números citados vêm dos arquivos do TSE descritos em
   "Fontes e limites" (BWeb do 2º turno, votacao_secao, boletins de urna). */
"use strict";

const INV_DOWNES = "https://fallacies.ca/";
const INV_FALACIA = n => `https://fallacies.ca/cgi-bin/page.cgi?fallacy=${n}`;
const INV_RESULTADOS = {
  falso: ["nao", "Falso"],
  enganoso: ["parcial", "Enganoso"],
  correto: ["ok", "Correto"],
  naoverificado: ["indet", "Não verificado"],
  semevidencia: ["indet", "Sem evidência apresentada"],
};

const INV_CASOS = [
  {
    id: "video-3-boletins-teixeira",
    titulo: "Vídeo “3 boletins mostram o roubo nas eleições” (Teixeira de Freitas, BA)",
    registrado: "2026-10-29",
    resultado: "falso",
    resumo: "Um fiscal mostra três boletins de urna em que Flávio teve 167 votos a mais que Lula e conclui que houve roubo porque Flávio venceu a cidade inteira por só 93 votos. Os três boletins são verdadeiros e idênticos aos publicados pelo TSE. A diferença entre 167 e 93 vem das outras 300 seções da cidade, onde Lula teve 74 votos a mais.",
    publicacoes: [
      { plataforma: "X", autor: "Renato Cabral Monteiro (@RenatoMontMusic)", url: "https://x.com/RenatoMontMusic/status/2115083771259105561",
        publicado: "2026-10-27T14:10:42Z", papel: "Publicação analisada: republica o vídeo, em resposta a @carlosjordy." },
      { plataforma: "Instagram", autor: "@vinicius_teixeira_bahia", url: null, publicado: null,
        papel: "Autor original do vídeo, identificado pela marca d'água. A publicação original não foi localizada." },
      { plataforma: "X", autor: "Carlos Jordy (@carlosjordy)", url: "https://x.com/carlosjordy/status/2114748093723795614",
        publicado: "2026-10-26T15:56:50Z", papel: "Contexto: publicação a que o vídeo responde. Traz outro vídeo, não analisado neste caso." },
    ],
    arquivo: {
      pasta: "investigando/arquivo/x_RenatoMontMusic_2115083771259105561/",
      video: "video_720x1280.mp4", capa: "quadro_boletins.jpg",
      itens: [["Vídeo (MP4, 720×1280, 1min10s)", "video_720x1280.mp4"], ["Transcrição do áudio", "transcricao.txt"],
        ["Metadados das publicações", "metadados.json"], ["Hashes SHA-256", "SHA256SUMS"]],
      nota: "Arquivado em 29/10/2026. Texto e data das publicações obtidos pelo endpoint público de incorporação do X; transcrição automática feita localmente (faster-whisper).",
    },
    contexto: [
      "O homem do vídeo diz que trabalhou como fiscal na eleição em Teixeira de Freitas (BA) e mostra três boletins de urna impressos. Lê os votos: 159 Flávio e 118 Lula; 167 e 105; 168 e 104. Diz que os três somam 164 votos a mais para Flávio, que no site do TSE Flávio venceu na cidade por apenas 93 votos, e conclui: “Teixeira, Bahia, Brasil, nós fomos roubados”. Termina pedindo que o vídeo seja compartilhado e que deputados, senadores e o TSE sejam marcados.",
    ],
    alegacoes: [
      { texto: "Os três boletins mostram Flávio com 164 votos a mais que Lula.",
        verificacao: "Os boletins são das seções 189, 205 e 219 da zona 183, todas no mesmo local de votação (nº 1392). Votos, eleitores aptos, comparecimento e horário de fechamento conferem exatamente com o boletim publicado pelo TSE (arquivo BWeb). A vantagem de Flávio nas três é de 167 votos (41 + 62 + 64), não 164.",
        resultado: "correto" },
      { texto: "Flávio venceu em Teixeira de Freitas por só 93 votos.",
        verificacao: "Confere: Flávio 41.454 e Lula 41.361 nas 303 seções do município.",
        resultado: "correto" },
      { graficos: ["teixeira_soma", "teixeira_locais"], texto: "Se três seções deram 167 votos a mais para Flávio, a cidade não poderia ter dado só 93; portanto houve roubo.",
        verificacao: "As outras 300 seções deram a Lula 74 votos a mais que a Flávio (167 − 93 = 74). Não há nada de anormal nisso. Dos 45 locais de votação da cidade, Lula venceu em 22 e Flávio em 23. O local 1392, de onde vêm os três boletins, é o 5º mais favorável a Flávio (506 votos a mais); no local 1350, Lula teve 1.025 votos a mais. Os boletins que o próprio fiscal guardou conferem com os dados oficiais, o que é evidência de que a totalização registrou corretamente o que as urnas apuraram.",
        resultado: "falso" },
    ],
    analise: [
      "O argumento depende de uma premissa que não é dita: que a vantagem de Flávio na cidade inteira tinha de ser pelo menos igual à vantagem dele em três seções. Isso só seria verdade se todas as outras seções também dessem vantagem a Flávio. Como a cidade ficou praticamente dividida ao meio, as seções onde Lula venceu compensam as seções onde Flávio venceu, e o saldo final é pequeno.",
      "As três seções vêm de um único local de votação, um dos mais favoráveis a Flávio, e o próprio autor reconhece que “só tô com três boletins”, “de uma só zona, de um só colégio”. Os boletins das outras 300 seções estão publicados no mesmo site do TSE que ele cita.",
    ],
    falacias: [
      { nome: "Composição", original: "Composition", n: 34, categoria: "Erros de categoria",
        uso: "Supõe que, porque as partes examinadas (três seções) dão vantagem a Flávio, o todo (a cidade) deveria dar vantagem igual ou maior. A vantagem de um conjunto de seções não se transfere para a soma de todas as seções." },
      { nome: "Amostra não representativa", original: "Unrepresentative Sample", n: 16, categoria: "Falácias indutivas",
        uso: "Os três boletins são do mesmo local de votação, o 5º mais favorável a Flávio entre os 45 da cidade. Uma amostra assim mostra o comportamento desse local, não o da cidade." },
      { nome: "Generalização precipitada", original: "Hasty Generalization", n: 17, categoria: "Falácias indutivas",
        uso: "Três seções de 303 (1%) são usadas para concluir que “Teixeira, Bahia, Brasil” foram roubados." },
      { nome: "Falácia da exclusão", original: "Fallacy of Exclusion", n: 20, categoria: "Falácias indutivas",
        uso: "Deixa de fora os boletins das outras 300 seções, publicados no mesmo site do TSE citado no vídeo, que explicariam a diferença entre 167 e 93." },
    ],
    respostas: [],
  },
  {
    id: "dossie-pericial-independente",
    titulo: "“Relatório Pericial Independente”: virada depois das 17h, biometria e seções unânimes",
    registrado: "2026-10-29",
    resultado: "enganoso",
    resumo: "Um PDF sem autor identificado, divulgado como carrossel no Instagram, afirma que Flávio venceu nas urnas fechadas até as 17h, que Lula virou nas urnas fechadas depois, que 8,6 milhões de votos sem biometria são quase o dobro da margem e que os dados ficaram 72 horas em sigilo. Os números de contagem estão quase todos corretos. As conclusões não decorrem deles, e duas afirmações são falsas.",
    publicacoes: [
      { plataforma: "Instagram", autor: "Thomas Queiroz (@thomqrz), com @isentoes, @falha_sp e @oodiodobem como coautores",
        url: "https://www.instagram.com/p/DfD0NpLDbsl/", publicado: "2026-10-29T01:21:53Z",
        papel: "Publicação analisada. No arquivamento: 20.847 curtidas e 667 comentários." },
      { plataforma: "PDF", autor: "Não identificado (“peritos independentes”)", url: null, publicado: null,
        papel: "Documento de 7 páginas datado de 28/10/2026, reproduzido nas imagens 2 a 8 do carrossel. Não foi localizada publicação do arquivo original." },
    ],
    arquivo: {
      pasta: "investigando/arquivo/instagram_DfD0NpLDbsl/",
      imagens: [1, 2, 3, 4, 5, 6, 7, 8].map(i => `instagram_DfD0NpLDbsl_0${i}.jpg`),
      itens: [["Legenda da publicação", "legenda.txt"], ["Metadados", "metadados.json"], ["Hashes SHA-256", "SHA256SUMS"]],
      nota: "Arquivado em 29/10/2026, com as 8 imagens na resolução original.",
    },
    contexto: [
      "O carrossel tem uma capa (“Anomalia nos microdados do TSE”, “Mais de 8 milhões de votos liberados sem biometria”) e as 7 páginas de um “Relatório Pericial Independente — com base em microdados oficiais do TSE”. O relatório diz ter processado as 499.205 seções do 2º turno a partir do arquivo de boletins de urna (BWeb). A legenda resume quatro pontos: a inversão das 17h, a biometria, as seções quase unânimes e um suposto sigilo de 72 horas.",
      "O 2º turno foi em 25/10/2026. A votação foi estendida até as 19h (horário de Brasília) nas seções que ainda funcionavam às 17h, por decisão do ministro Cristiano Zanin (STF), segundo o TSE. O TSE informou 34.393 votos dados depois das 17h: 32.399 entre 17h e 18h, 1.981 entre 18h e 19h e 13 depois das 19h.",
    ],
    alegacoes: [
      { graficos: ["horario", "fuso"], texto: "Nas urnas encerradas até as 17h, Flávio venceu com 52,39% e vantagem de quase 1,8 milhão; nas encerradas depois, Lula teve mais de 6,1 milhões de vantagem.",
        verificacao: "Os números se reproduzem com o BWeb usando a hora gravada no boletim, que é a hora local da seção: 150.742 seções “até 17h00”, Flávio 52,40%, vantagem de 1,75 milhão. Convertendo para a hora de Brasília, nenhuma seção fechou antes das 17h00: a primeira fechou 9 segundos depois e a mediana, 1,7 minuto depois. O grupo “até 17h00” reúne as seções que fecharam no primeiro minuto e todas as 32.026 seções de AC, AM, MS, MT, RO e RR, que fecham às 15h ou 16h locais (17h em Brasília); só essas dão 1,44 milhão da vantagem de Flávio. Dentro de cada estado, a diferença de votação entre seções que fecharam no primeiro minuto e as que fecharam de 1 a 15 minutos depois é de 0,4 ponto percentual (mediana).",
        resultado: "falso" },
      { graficos: ["margem"], texto: "Os 34 mil votos depois das 17h são um mito: mais de 2,5 milhões de eleitores votaram em urnas que passaram do limite.",
        verificacao: "O relatório compara coisas diferentes. Os 34.393 votos do TSE foram dados depois das 17h (a hora de cada voto vem do log da urna). Os 2,5 milhões são todos os eleitores, desde as 8h, das seções que fecharam depois das 17h15. O BWeb não registra a hora de cada voto. Das 6.757 seções que fecharam perto das 19h, o comparecimento foi 80,6%, contra 80,8% nas demais seções dos mesmos estados. Sem essas seções, Lula venceria por 4,24 milhões; mesmo que todos os votos delas fossem de Flávio, Lula venceria por 2,33 milhões.",
        resultado: "falso" },
      { graficos: ["vizinhas"], texto: "Nas seções que entraram na noite, Lula teve índices avassaladores (Bahia 72,31%, Pernambuco 65,70%, Maranhão 83,31%, São Paulo 57,46%).",
        verificacao: "Os percentuais conferem, mas medem a votação do dia inteiro nessas seções, e não a da prorrogação. Segundo o TSE, em todo o país foram dados 1.981 votos entre 18h e 19h e 13 depois das 19h. O comparecimento nessas seções (80,6%) foi igual ao das demais seções dos mesmos estados (80,8%). Para saber se a prorrogação mudou o voto, é preciso comparar as seções que ficaram abertas com as seções da mesma zona eleitoral que fecharam no horário normal (gráfico abaixo). Na Bahia e em Pernambuco, a votação foi a mesma das seções vizinhas. Em São Paulo, 1.560 das 1.656 seções ficam na capital, onde Lula teve mais votos do que no interior; comparadas às vizinhas da mesma zona, deram a Lula 3 pontos a mais. No Rio de Janeiro, o estado com mais seções abertas até perto das 19h, e na Paraíba, os dois fora da tabela do dossiê, Lula teve menos votos nessas seções do que nas vizinhas. O número do Maranhão vem de 3 seções com 634 eleitores. Somando as 284 zonas eleitorais onde houve seções abertas até perto das 19h, Lula teve nelas, em média, 0,33 ponto a menos do que nas seções vizinhas: foi melhor nessas seções em 133 zonas e pior em 151.",
        resultado: "enganoso" },
      { graficos: ["biometria"], texto: "8.632.488 eleitores foram liberados sem biometria, quase o dobro da margem de 4.430.191; os votos de Lula sobem com a taxa de liberação manual.",
        verificacao: "O número é correto (campo QT_ELEI_BIOM_SEM_HABILITACAO do BWeb). Liberação por código é o procedimento para o eleitor com biometria cadastrada cuja digital não foi reconhecida: ele é identificado pelo mesário com documento. Comparar esse total com a margem só faria sentido se esses votos fossem irregulares e todos de Lula, e o relatório não apresenta indício de nenhuma das duas coisas. A correlação entre a taxa de liberação da seção e o voto em Lula é 0,06 no país e 0,01 entre seções do mesmo município. Estados onde Flávio venceu têm taxas altas (RS 8,5%, SC 7,5%). As faixas de liberação acima de 30% somam 348 seções.",
        resultado: "enganoso" },
      { graficos: ["unanimes"], texto: "Lula teve 100% dos votos em 106 seções e mais de 90% em 6.899, contra 4 e 384 de Flávio (18 para 1): uma anomalia concentrada em zonas rurais com pouca fiscalização.",
        verificacao: "As contagens conferem (6.816 e 378 com “mais de 90%”). Comparando com as eleições anteriores, pelo mesmo cálculo: em 2018, quando o PT perdeu por 10,8 milhões, Haddad teve 14.958 seções acima de 90% contra 1.298 de Bolsonaro (11,5 para 1); em 2022, Lula teve 9.433 contra 213 (44 para 1). Em 2026 houve menos seções quase unânimes para o PT do que nas duas eleições anteriores. A assimetria acontece porque o voto no PT é geograficamente concentrado. O relatório não apresenta dado sobre fiscalização nessas seções.",
        resultado: "enganoso" },
      { texto: "Os microdados de horários e biometria ficaram 72 horas em sigilo e só foram liberados na manhã de 28/10.",
        verificacao: "O BWeb do 2º turno foi gerado em 26/10 às 07h42 e está no CDN do TSE desde 26/10 por volta das 9h (Brasília). Os boletins de urna de cada seção, com os mesmos campos, estavam no site de resultados do TSE em 26/10: este projeto baixou 50.821 deles naquele dia. O boletim impresso de cada seção é afixado no local de votação ao fim da apuração.",
        resultado: "falso" },
      { graficos: ["benford1", "benfordU"], texto: "O teste de Benford aplicado às 499.205 seções indica manipulação.",
        verificacao: [
          "O relatório não mostra o resultado do teste: diz que os gráficos não foram incluídos. Para avaliar a alegação, este projeto aplicou às seções de 2018, 2022 e 2026 o teste usado no dossiê e os dois testes de dígitos propostos pelos pesquisadores que defendem esse tipo de análise:",
          [
            ["Primeiro dígito (o teste do dossiê)", "rejeita a lei de Benford com valor-p praticamente zero para os dois finalistas das três eleições, inclusive em 2018, quando o PT perdeu. A causa é o tamanho limitado das seções: em 2026, 90% delas tiveram entre 161 e 334 votantes, então a maior parte das contagens de cada candidato fica entre 100 e 199 e começa com 1 (61% das seções para Lula e 62% para Flávio, contra 30% pela lei de Benford). Críticos e defensores dos testes de dígitos concordam que, nessas condições, o primeiro dígito não serve para detectar fraude."],
            ["Segundo dígito (defendido por Mebane e por Pericchi e Torres)", "também rejeita a lei de Benford nas três eleições, para os dois finalistas. Com quase 500 mil seções, desvios pequenos produzem valor-p próximo de zero, e os próprios defensores dizem que esse desvio, sozinho, não é evidência de fraude e pede estudo adicional."],
            ["Último dígito (proposto por Beber e Scacco para detectar números inventados por pessoas)", "em 2026, cada dígito de 0 a 9 aparece em 10,0% das seções, tanto para Lula (p = 0,84) quanto para Flávio (p = 0,19). Por estado, 3 de 56 testes rejeitam a uniformidade ao nível de 5% (Lula em MT e RO, Flávio no DF), o que se espera do acaso em 56 testes; nenhum rejeita após a correção para múltiplos testes."],
          ],
          "O estudo adicional que um alarme pediria é o que este painel faz nas outras alegações e abas: conferência dos boletins de urna, das contas oficiais e da votação por seção.",
        ],
        referencias: [
          { grupo: "Críticas ao uso da lei de Benford em eleições", itens: [
            { texto: "Deckert, J.; Myagkov, M.; Ordeshook, P. C. (2011). Benford's Law and the Detection of Election Fraud. Political Analysis, 19(3), 245–268.",
              url: "https://doi.org/10.1093/pan/mpr014",
              resumo: "Com simulações e com eleições sabidamente limpas ou fraudadas, mostra que a conformidade ou o desvio em relação à lei de Benford não segue padrão: a taxa de acerto do teste é equivalente à de jogar uma moeda." },
            { texto: "Shikano, S.; Mack, V. (2011). When Does the Second-Digit Benford's Law-Test Signal an Election Fraud? Jahrbücher für Nationalökonomie und Statistik, 231(5-6), 719–732.",
              url: "https://doi.org/10.1515/jbnst-2011-5-610",
              resumo: "Aplicado à eleição parlamentar alemã de 2009, contra a qual não houve denúncia séria de fraude, o teste do segundo dígito indicou fraude em vários distritos. Com uma distribuição de referência obtida por simulação, em vez da usual, o desvio desaparece." },
            { texto: "Mebane, W. R., Jr. (2020). Inappropriate Applications of Benford's Law Regularities to Some Data from the 2020 Presidential Election in the United States. University of Michigan, 10 nov. 2020.",
              url: "https://websites.umich.edu/~wmebane/inapB.pdf",
              resumo: "Responde a alegações de fraude baseadas no primeiro dígito dos votos por seção na eleição americana de 2020: o primeiro dígito é determinado sobretudo pelo número de eleitores de cada seção e não diz nada sobre fraude. O autor é um dos defensores do teste do segundo dígito." },
          ] },
          { grupo: "Defensores de testes de dígitos: o que dizem que se aplica a este caso", itens: [
            { texto: "Mebane, W. R., Jr. (2011). Comment on “Benford's Law and the Detection of Election Fraud”. Political Analysis, 19(3), 269–272.",
              url: "https://doi.org/10.1093/pan/mpr024",
              resumo: "Responde a Deckert e colegas e defende que a utilidade do teste do segundo dígito é uma questão em aberto. Concorda que um desvio do segundo dígito em relação ao esperado pela lei de Benford não é evidência de fraude, e afirma que, como o primeiro dígito das contagens de votos em geral não segue a lei, a lei de Benford não se aplica a essas contagens." },
            { texto: "Pericchi, L.; Torres, D. (2011). Quick Anomaly Detection by the Newcomb–Benford Law, with Applications to Electoral Processes Data from the USA, Puerto Rico and Venezuela. Statistical Science, 26(4), 502–516.",
              url: "https://doi.org/10.1214/09-STS296",
              resumo: "Propõem o teste do segundo dígito, com uma versão que considera o limite de eleitores por seção, como triagem rápida: se o teste falha, é preciso estudo adicional. Na eleição de Porto Rico de 2000 o primeiro dígito foi rejeitado, o que atribuem ao limite de eleitores por seção, e concluem que o segundo dígito tem aplicação mais ampla. Recomendam não usar valor-p em conjuntos grandes de dados eleitorais. Na eleição americana de 2004 o primeiro dígito se ajustou à lei." },
            { texto: "Beber, B.; Scacco, A. (2012). What the Numbers Say: A Digit-Based Test for Election Fraud. Political Analysis, 20(2), 211–234.",
              url: "https://doi.org/10.1093/pan/mps003",
              resumo: "Propõem testar o último dígito, que em eleições limpas aparece com frequência igual de 0 a 9 quando as contagens variam o suficiente, e cuja distorção indica números inventados por pessoas, como em atas preenchidas à mão. O teste depende de suposições mais fracas do que os testes baseados na lei de Benford." },
          ] },
        ],
        resultado: "semevidencia" },
      { texto: "Capítulo 6: cancelamento de passaportes, ameaça de prisão, caso Banco Master, reações de Trump, Argentina e mídia chinesa.",
        verificacao: "São afirmações políticas que não derivam dos dados eleitorais. Não foram verificadas.",
        resultado: "naoverificado" },
    ],
    analise: [
      "O relatório leu os campos certos do arquivo do TSE, e por isso suas contagens se reproduzem. O erro está no que ele conclui a partir delas. A divisão “até 17h / depois das 17h” é produzida por não converter o fuso horário; a comparação entre votos sem biometria e margem não diz nada sobre fraude; e a contagem de seções unânimes, vista ao lado das eleições anteriores, não tem nada de anormal.",
      "Duas afirmações são falsas como fato: o sigilo de 72 horas e a ideia de que a vitória de Lula veio de votos dados depois do horário. As seções que ficaram abertas até as 19h não alteram o vencedor, mesmo na hipótese extrema de todos os votos delas serem de Flávio.",
    ],
    falacias: [
      { nome: "Efeito conjunto", original: "Joint Effect", n: 24, categoria: "Falácias causais",
        uso: "Atribui a diferença de votação ao horário de fechamento da urna. Na verdade, a localização da seção causa as duas coisas: nos estados com fuso diferente de Brasília a urna aparece como fechada “antes das 17h” e, ao mesmo tempo, a votação de Flávio foi maior." },
      { nome: "Equívoco", original: "Equivocation", n: 31, categoria: "Falácias de ambiguidade",
        uso: "Usa “depois das 17h” em dois sentidos: seção que fechou depois das 17h (todas, porque quem está na fila às 17h ainda vota) e voto dado durante a prorrogação. Com isso, 88 milhões de eleitores de seções que fecharam entre 17h01 e 17h15 viram “prorrogação”, e os 34 mil votos informados pelo TSE viram “mito”." },
      { nome: "Conclusão irrelevante", original: "Irrelevant Conclusion", n: 29, categoria: "Fuga ao assunto",
        uso: "Mostra que o número de eleitores liberados por código (8,6 milhões) é maior que a margem (4,4 milhões) e conclui que o resultado não tem integridade. A comparação prova só que um número é maior que o outro; não mostra que algum desses votos foi irregular." },
      { nome: "Falácia da exclusão", original: "Fallacy of Exclusion", n: 20, categoria: "Falácias indutivas",
        uso: "Apresenta as seções quase unânimes de 2026 sem compará-las com 2018 e 2022, que têm mais seções desse tipo para o PT. Na tabela de estados com seções abertas à noite, omite o Rio de Janeiro e a Paraíba, onde Lula teve menos votos nessas seções do que nas seções vizinhas que fecharam no horário normal." },
      { nome: "Generalização precipitada", original: "Hasty Generalization", n: 17, categoria: "Falácias indutivas",
        uso: "Apresenta “Maranhão 83,31%” ao lado de estados com centenas de seções, quando o número vem de 3 seções com 634 eleitores." },
      { nome: "Autoridade anônima", original: "Anonymous Authorities", n: 13, categoria: "Mudança de assunto",
        uso: "Atribui as conclusões a “peritos independentes”, à “equipe de inteligência” e à “perícia”, sem nomear ninguém nem publicar código ou dados que permitam conferir o trabalho." },
      { nome: "Apelo à autoridade", original: "Appeal to Authority", n: 12, categoria: "Mudança de assunto",
        uso: "Usa como apoio a opinião de Donald Trump e uma suposta admissão da mídia estatal chinesa, que não são fontes com conhecimento técnico sobre a apuração." },
      { nome: "Correlação coincidente", original: "Coincidental Correlation", n: 23, categoria: "Falácias causais",
        uso: "Trata como evidência de fraude o fato de decisões judiciais e investigações sobre outros assuntos terem ocorrido na mesma semana da eleição." },
      { nome: "Linguagem tendenciosa", original: "Prejudicial Language", n: 8, categoria: "Apelos a motivos em vez de razões",
        uso: "Expressões como “explosão atípica”, “aberrações”, “calada da noite”, “operação de abafamento” e “vitória fabricada” atribuem a conclusão antes de qualquer demonstração." },
    ],
    respostas: [],
  },
];

/* ---------------- gráficos ----------------
   Números calculados a partir do BWeb do 2º turno (499.205 seções) e de votacao_secao
   de 2018, 2022 e 2026. Cada gráfico tem uma tabela com os mesmos números. */
const INV_LOCAIS_TEIXEIRA = [ // local de votação, votos de Lula, votos de Flávio (zona 183)
  [1023, 1838, 3138], [1090, 649, 1224], [1031, 627, 1193], [1163, 1349, 1859], [1392, 1286, 1792], [1104, 726, 1207],
  [1406, 1202, 1665], [1368, 1718, 2131], [1074, 694, 1018], [1112, 1134, 1372], [1490, 914, 1139], [1058, 641, 865],
  [1341, 814, 1025], [1139, 333, 540], [1511, 426, 631], [1589, 631, 832], [1201, 1278, 1415], [1457, 1120, 1240],
  [1317, 375, 490], [1600, 109, 194], [1180, 1174, 1256], [1546, 99, 173], [1210, 779, 806], [1627, 74, 67],
  [1198, 314, 303], [1635, 23, 9], [1481, 1057, 1035], [1279, 144, 76], [1597, 266, 179], [1244, 348, 241],
  [1619, 138, 10], [1260, 221, 67], [1503, 1326, 1162], [1570, 583, 412], [1473, 1228, 1043], [1015, 1661, 1464],
  [1554, 822, 493], [1147, 1533, 1157], [1325, 810, 413], [1520, 1366, 865], [1422, 1628, 1007], [1287, 1414, 614],
  [1376, 1869, 1015], [1414, 2429, 1451], [1350, 2191, 1166],
];
const INV_HORARIO = [["0–1", 125624], ["1–2", 154492], ["2–5", 160346], ["5–10", 44053], ["10–15", 4288], ["15–30", 1482],
  ["30–60", 526], ["60–100", 329], ["100–130", 6662], ["130 ou mais", 95]];
const INV_VIZINHAS = [ // UF, seções abertas até perto das 19h, Lula no estado, Lula nessas seções, Lula nas demais seções das mesmas zonas
  ["BA", 985, 71.3, 72.3, 72.5], ["PE", 694, 69.2, 65.8, 65.8], ["SP", 1656, 46.2, 57.2, 54.1],
  ["RJ", 2998, 46.9, 45.7, 49.9], ["PB", 311, 67.5, 52.8, 57.7], ["MA", 3, 69.5, 83.3, 73.8]];
const INV_BIOMETRIA_UF = { // UF: [% do comparecimento liberado por código, % de Lula nos válidos]
  AC: [4.99, 33.4], AL: [6.96, 60.8], AM: [5.43, 54.0], AP: [4.58, 52.9], BA: [7.45, 71.3], CE: [7.13, 68.9], DF: [4.5, 45.7],
  ES: [6.28, 43.6], GO: [6.64, 40.3], MA: [6.3, 69.5], MG: [6.81, 50.4], MS: [7.25, 40.4], MT: [6.6, 33.9], PA: [5.56, 55.0],
  PB: [7.27, 67.5], PE: [6.53, 69.2], PI: [9.0, 75.9], PR: [6.99, 37.4], RJ: [7.45, 46.9], RN: [8.1, 65.7], RO: [6.27, 30.4],
  RR: [4.1, 27.5], RS: [8.45, 42.2], SC: [7.51, 30.6], SE: [6.97, 69.5], SP: [5.96, 46.2], TO: [4.95, 48.6]};
const INV_UNANIMES = [[2018, "Haddad", "J. Bolsonaro", 14958, 1298], [2022, "Lula", "J. Bolsonaro", 9433, 213], [2026, "Lula", "Flávio", 6816, 378]];
const INV_DIG1 = { benford: [30.1, 17.6, 12.5, 9.7, 7.9, 6.7, 5.8, 5.1, 4.6],
  lula: [60.81, 9.29, 0.94, 1.69, 2.81, 4.26, 5.60, 6.85, 7.75], flavio: [61.88, 7.21, 2.81, 3.44, 3.86, 4.35, 4.87, 5.45, 6.13] };
const INV_DIGU = { lula: [10.03, 9.95, 9.98, 9.98, 10.0, 9.99, 10.0, 10.0, 9.98, 10.08], flavio: [10.02, 9.98, 9.99, 10.11, 9.98, 10.02, 10.03, 10.0, 9.99, 9.89] };

const invCompacto = v => Math.abs(v) >= 1e6 ? fNum(v / 1e6, 2) + " mi" : Math.abs(v) >= 1e4 ? fNum(v / 1e3, 0) + " mil" : fInt(v);
const invP = (v, d = 1) => fNum(v, d) + "%";
/* barra com a ponta de dados arredondada (4px) e a base reta; fim: d, e, c (cima), b (baixo) */
function invBarra(x, y, w, h, fim) {
  const r = Math.max(0, Math.min(4, fim === "d" || fim === "e" ? Math.min(w, h / 2) : Math.min(h, w / 2)));
  if (fim === "d") return `M${x},${y}H${x + w - r}Q${x + w},${y} ${x + w},${y + r}V${y + h - r}Q${x + w},${y + h} ${x + w - r},${y + h}H${x}Z`;
  if (fim === "e") return `M${x + w},${y}H${x + r}Q${x},${y} ${x},${y + r}V${y + h - r}Q${x},${y + h} ${x + r},${y + h}H${x + w}Z`;
  if (fim === "c") return `M${x},${y + h}V${y + r}Q${x},${y} ${x + r},${y}H${x + w - r}Q${x + w},${y} ${x + w},${y + r}V${y + h}Z`;
  return `M${x},${y}V${y + h - r}Q${x},${y + h} ${x + r},${y + h}H${x + w - r}Q${x + w},${y + h} ${x + w},${y + h - r}V${y}Z`;
}
const invDica = (sel, html) => sel.on("mousemove", ev => mostrarDica(html, ev)).on("mouseleave", esconderDica);

/* barras horizontais a partir de zero; valores negativos crescem para a esquerda.
   Em telas largas o nome fica à esquerda da barra e o valor na ponta; em telas estreitas,
   nome e valor ficam numa linha acima da barra, que ocupa a largura toda. */
function invBarrasH(el, itens, rodape) {
  const W = larg(el), estreito = W < 520, bh = estreito ? 18 : 22;
  const mE = estreito ? 6 : Math.min(250, W * .42), passo = estreito ? 62 : 46, topo = estreito ? 30 : 6;
  const H = itens.length * passo + (rodape ? 34 : 12);
  const vmin = Math.min(0, d3.min(itens, i => i.v)), vmax = Math.max(0, d3.max(itens, i => i.v));
  const folga = estreito ? 0 : (vmax - vmin) * .28;
  const x = d3.scaleLinear().domain([vmin - (vmin < 0 ? folga : 0), vmax + (vmax > 0 ? folga : 0)]).range([mE, W - 8]);
  const svg = d3.select(el).html("").append("svg").attr("viewBox", `0 0 ${W} ${H}`).attr("role", "img");
  svg.append("line").attr("x1", x(0)).attr("x2", x(0)).attr("y1", estreito ? topo : 2).attr("y2", itens.length * passo - 8).attr("stroke", C.linhaF);
  itens.forEach((it, i) => {
    const y = i * passo + topo, x0 = x(Math.min(0, it.v)), w = Math.max(2, Math.abs(x(it.v) - x(0))), neg = it.v < 0;
    if (estreito) {
      svg.append("text").attr("class", "rot-forte").attr("x", mE).attr("y", y - 17).text(it.rot);
      svg.append("text").attr("class", "rot-medio").attr("x", W - 8).attr("y", y - 17).attr("text-anchor", "end").text(it.txt);
      if (it.sub) svg.append("text").attr("class", "rot").attr("x", mE).attr("y", y - 4).text(it.sub);
    } else {
      svg.append("text").attr("class", "rot-forte").attr("x", mE - 10).attr("y", y + (it.sub ? 9 : 15)).attr("text-anchor", "end").text(it.rot);
      if (it.sub) svg.append("text").attr("class", "rot").attr("x", mE - 10).attr("y", y + 23).attr("text-anchor", "end").text(it.sub);
      svg.append("text").attr("class", "rot-medio").attr("x", neg ? x(it.v) - 6 : x(it.v) + 6).attr("y", y + 15)
        .attr("text-anchor", neg ? "end" : "start").text(it.txt);
    }
    invDica(svg.append("path").attr("d", invBarra(x0, y, w, bh, neg ? "e" : "d")).attr("fill", it.cor), it.dica || it.txt);
  });
  if (rodape) svg.append("text").attr("class", "rot").attr("x", x(0)).attr("y", H - 8).attr("text-anchor", "middle").text(rodape);
}

/* colunas agrupadas por categoria; series: [{nome, cor, valores}] */
function invColunas(el, cats, series, { y0 = 0, y1, fmt, fmtEixo = fmt, rotY, ref, marcas, H = 260, rotular = () => false, dicaCat = c => c } = {}) {
  const W = larg(el), mE = 52, mT = rotY ? 28 : 14;
  // nomes de categoria que não cabem na largura da coluna ficam inclinados
  const larguraCol = (W - mE - 6) / cats.length, inclinar = d3.max(cats, c => c.length) * 7 > larguraCol;
  const mB = inclinar ? 58 : 34;
  H += mB - 34;
  const x = d3.scaleBand().domain(cats).range([mE, W - 6]).paddingInner(.25).paddingOuter(.1);
  const xi = d3.scaleBand().domain(series.map(s => s.nome)).range([0, x.bandwidth()]).padding(.08);
  const y = d3.scaleLinear().domain([y0, y1]).range([H - mB, mT]);
  const svg = d3.select(el).html("").append("svg").attr("viewBox", `0 0 ${W} ${H}`).attr("role", "img");
  svg.append("g").attr("class", "eixo").attr("transform", `translate(${mE},0)`).call(d3.axisLeft(y).ticks(5).tickSize(-(W - mE - 6)).tickFormat(fmtEixo))
    .call(g => g.select(".domain").remove()).call(g => g.selectAll(".tick line").attr("stroke", C.linha));
  const rotX = svg.append("g").attr("class", "eixo").attr("transform", `translate(0,${H - mB})`).call(d3.axisBottom(x).tickSize(0)).call(g => g.select(".domain").attr("stroke", C.linhaF)).selectAll("text");
  if (inclinar) rotX.attr("text-anchor", "end").attr("dx", "-.3em").attr("dy", ".9em").attr("transform", "rotate(-40)");
  else rotX.attr("dy", "1.1em");
  if (rotY) svg.append("text").attr("class", "rot").attr("x", mE).attr("y", 9).text(rotY);
  const bw = Math.min(24, xi.bandwidth());
  cats.forEach((c, i) => series.forEach(s => {
    const v = s.valores[i], bx = x(c) + xi(s.nome) + (xi.bandwidth() - bw) / 2;
    invDica(svg.append("path").attr("d", invBarra(bx, y(v), bw, Math.max(1, y(y0) - y(v)), "c")).attr("fill", s.cor), `<b>${esc(dicaCat(c))}</b><br>${esc(s.nome)}: ${fmt(v)}`);
    if (rotular(i, s, x.bandwidth() < 40)) svg.append("text").attr("class", "rot").attr("x", bx + bw / 2).attr("y", y(v) - 4).attr("text-anchor", "middle").text(fmt(v));
  }));
  if (marcas) { // valores de referência por categoria (pontos ligados por linha)
    const px = c => x(c) + x.bandwidth() / 2;
    svg.append("path").attr("d", d3.line()(cats.map((c, i) => [px(c), y(marcas.valores[i])]))).attr("fill", "none").attr("stroke", C.tinta2).attr("stroke-width", 2).attr("stroke-linejoin", "round");
    cats.forEach((c, i) => invDica(svg.append("circle").attr("cx", px(c)).attr("cy", y(marcas.valores[i])).attr("r", 5).attr("fill", C.tinta2).attr("stroke", C.papel).attr("stroke-width", 2),
      `<b>${esc(dicaCat(c))}</b><br>${esc(marcas.nome)}: ${fmt(marcas.valores[i])}`));
  }
  if (ref) {
    svg.append("line").attr("x1", mE).attr("x2", W - 6).attr("y1", y(ref.v)).attr("y2", y(ref.v)).attr("stroke", C.tinta2).attr("stroke-width", 1.5);
    svg.append("text").attr("class", "rot-medio").attr("x", W - 8).attr("y", y(ref.v) - 6).attr("text-anchor", "end").text(ref.rot);
  }
}

const INV_GRAFICOS = {
  teixeira_soma: {
    titulo: "Como 167 votos a mais em 3 seções viram 93 na cidade",
    como: "Cada barra é a diferença entre os votos de Lula e de Flávio. Barras para a esquerda: vantagem de Flávio; para a direita: vantagem de Lula. A vantagem da cidade é a soma das duas primeiras.",
    legenda: () => [[C.dir, "Vantagem de Flávio"], [C.lula, "Vantagem de Lula"]],
    tabela: () => ({ cab: ["Conjunto de seções", "Lula − Flávio"], linhas: [["As 3 seções do vídeo (local 1392)", "−167"], ["As outras 300 seções da cidade", "+74"], ["Teixeira de Freitas (303 seções)", "−93"]] }),
    desenhar: el => invBarrasH(el, [
      { rot: "As 3 seções do vídeo", sub: "local 1392, zona 183", v: -167, cor: C.dir, txt: "Flávio +167" },
      { rot: "As outras 300 seções", sub: "44 locais de votação", v: 74, cor: C.lula, txt: "Lula +74" },
      { rot: "A cidade inteira", sub: "303 seções", v: -93, cor: C.dir, txt: "Flávio +93" },
    ], "← vantagem de Flávio · vantagem de Lula →"),
  },
  teixeira_locais: {
    titulo: "Os 45 locais de votação de Teixeira de Freitas",
    como: "Cada coluna é um local de votação, ordenado da maior vantagem de Flávio (esquerda) para a maior vantagem de Lula (direita). Os três boletins do vídeo são do local 1392, o 5º mais favorável a Flávio.",
    legenda: () => [[C.dir, "Local onde Flávio venceu (23)"], [C.lula, "Local onde Lula venceu (22)"]],
    tabela: () => ({ cab: ["Local", "Lula", "Flávio", "Lula − Flávio"], linhas: INV_LOCAIS_TEIXEIRA.map(([l, a, b]) => [l, fInt(a), fInt(b), fSin(a - b, 0)]) }),
    desenhar: el => {
      const W = larg(el), H = 260, mE = 46, mB = 26, mT = 30;
      const d = INV_LOCAIS_TEIXEIRA.map(([l, a, b]) => ({ l, a, b, v: a - b }));
      const x = d3.scaleBand().domain(d.map(r => r.l)).range([mE, W - 6]).padding(.18);
      const y = d3.scaleLinear().domain([-1400, 1200]).range([H - mB, mT]);
      const svg = d3.select(el).html("").append("svg").attr("viewBox", `0 0 ${W} ${H}`).attr("role", "img");
      svg.append("g").attr("class", "eixo").attr("transform", `translate(${mE},0)`).call(d3.axisLeft(y).ticks(5).tickSize(-(W - mE - 6)).tickFormat(t => fSin(t, 0)))
        .call(g => g.select(".domain").remove()).call(g => g.selectAll(".tick line").attr("stroke", C.linha));
      svg.append("line").attr("x1", mE).attr("x2", W - 6).attr("y1", y(0)).attr("y2", y(0)).attr("stroke", C.linhaF);
      const bw = Math.min(24, x.bandwidth());
      d.forEach(r => {
        const destaque = r.l === 1392 || r.l === 1350, bx = x(r.l) + (x.bandwidth() - bw) / 2;
        invDica(svg.append("path").attr("d", invBarra(bx, Math.min(y(0), y(r.v)), bw, Math.max(1, Math.abs(y(r.v) - y(0))), r.v < 0 ? "b" : "c"))
          .attr("fill", r.v < 0 ? C.dir : C.lula).attr("fill-opacity", destaque ? 1 : .45),
          `<b>Local ${r.l}</b><br>Lula ${fInt(r.a)} · Flávio ${fInt(r.b)}<br>${r.v < 0 ? "Flávio" : "Lula"} +${fInt(Math.abs(r.v))}`);
        if (destaque) svg.append("text").attr("class", "rot-forte").attr("x", bx + bw / 2).attr("y", r.v < 0 ? y(r.v) + 16 : y(r.v) - 8)
          .attr("text-anchor", r.l === 1392 ? "start" : "end").text(r.l === 1392 ? (W < 520 ? "1392 (vídeo): Flávio +506" : "local 1392 (vídeo): Flávio +506") : (W < 520 ? "1350: Lula +1.025" : "local 1350: Lula +1.025"));
      });
      svg.append("text").attr("class", "rot").attr("x", mE).attr("y", 12).text("votos de Lula menos votos de Flávio");
    },
  },
  horario: {
    titulo: "Quanto tempo depois das 17h (Brasília) cada seção fechou",
    como: "Cada coluna conta as seções que fecharam naquela faixa de minutos depois das 17h, já convertido para o horário de Brasília. Nenhuma seção fechou antes das 17h: a mais rápida fechou 9 segundos depois. A pequena coluna perto de 120 minutos são as seções que ficaram abertas até as 19h.",
    tabela: () => ({ cab: ["Minutos depois das 17h", "Seções"], linhas: INV_HORARIO.map(([f, n]) => [f, fInt(n)]) }),
    desenhar: el => invColunas(el, INV_HORARIO.map(h => h[0]), [{ nome: "Seções", cor: C.realce, valores: INV_HORARIO.map(h => h[1]) }],
      { y1: 180000, fmt: invCompacto, rotY: "seções", rotular: (i, s, estreito) => (estreito ? [2, 8] : [0, 1, 2, 8]).includes(i), dicaCat: c => `${c} minutos depois das 17h` }),
  },
  fuso: {
    titulo: "De onde vem a vantagem de Flávio nas urnas “fechadas até as 17h”",
    como: "O dossiê leu a hora local gravada no boletim. Nos estados com fuso diferente de Brasília, a urna fecha às 15h ou 16h locais, que são 17h em Brasília, e por isso essas seções aparecem como “fechadas antes das 17h”. A maior parte da vantagem de Flávio nesse grupo vem delas.",
    tabela: () => ({ cab: ["Seções no grupo “até 17h00”", "Seções", "Vantagem de Flávio"], linhas: [["AC, AM, MS, MT, RO e RR (fuso diferente)", "32.026", "1.443.513"], ["Demais estados, fechadas no 1º minuto depois das 17h", "118.716", "304.955"]] }),
    desenhar: el => invBarrasH(el, [
      { rot: "AC, AM, MS, MT, RO e RR", sub: "32.026 seções · fuso diferente", v: 1443513, cor: C.dir, txt: "Flávio +1,44 mi" },
      { rot: "Demais estados", sub: "118.716 seções · fecharam no 1º minuto", v: 304955, cor: C.dir, txt: "Flávio +0,30 mi" },
    ]),
  },
  margem: {
    titulo: "O tamanho da prorrogação diante da margem",
    como: "As três primeiras barras são a vantagem de Lula em três situações: o resultado oficial, o resultado tirando todas as seções que ficaram abertas até perto das 19h, e o resultado se todos os votos dessas seções tivessem ido para Flávio. A última barra é o total de votos dados depois das 17h, segundo o TSE.",
    legenda: () => [[C.lula, "Vantagem de Lula"], [C.bn, "Votos dados depois das 17h"]],
    tabela: () => ({ cab: ["Situação", "Votos"], linhas: [["Vantagem oficial de Lula", "4.430.191"], ["Sem as 6.757 seções abertas até perto das 19h", "4.237.935"], ["Com todos os votos dessas seções para Flávio", "2.326.561"], ["Votos dados depois das 17h (TSE)", "34.393"]] }),
    desenhar: el => invBarrasH(el, [
      { rot: "Resultado oficial", sub: "vantagem de Lula", v: 4430191, cor: C.lula, txt: "4,43 mi" },
      { rot: "Sem as seções abertas até 19h", sub: "6.757 seções retiradas", v: 4237935, cor: C.lula, txt: "4,24 mi" },
      { rot: "Todos os votos delas para Flávio", sub: "hipótese extrema", v: 2326561, cor: C.lula, txt: "2,33 mi" },
      { rot: "Votos dados depois das 17h", sub: "total do país, segundo o TSE", v: 34393, cor: C.bn, txt: "34 mil" },
    ]),
  },
  vizinhas: {
    titulo: "Seções abertas até perto das 19h e suas vizinhas",
    como: "Em cada estado, o ponto cheio é a votação de Lula nas seções que ficaram abertas até perto das 19h; o ponto vazio, nas outras seções das mesmas zonas eleitorais, que fecharam no horário normal. Pontos próximos querem dizer que as seções votaram igual às vizinhas. “Abertas até perto das 19h” são as seções que fecharam 100 minutos ou mais depois das 17h (horário de Brasília); a contagem difere um pouco da do dossiê, que usa a hora local gravada no boletim.",
    legenda: () => [[C.tinta, "Seções abertas até perto das 19h", "border-radius:50%"], [C.papel, "Demais seções das mesmas zonas", `border-radius:50%;box-shadow:inset 0 0 0 2px ${C.tinta2}`]],
    tabela: () => ({ cab: ["UF", "Seções abertas até perto das 19h", "Lula no estado", "Lula nessas seções", "Lula nas vizinhas", "Diferença (p.p.)"],
      linhas: INV_VIZINHAS.map(([u, n, e, a, v]) => [u, fInt(n), invP(e), invP(a), invP(v), fSin(a - v, 1)]) }),
    desenhar: el => {
      const W = larg(el), mE = Math.min(130, W * .28), mD = 70, passo = 38, H = INV_VIZINHAS.length * passo + 34;
      const x = d3.scaleLinear().domain([40, 85]).range([mE, W - mD]);
      const svg = d3.select(el).html("").append("svg").attr("viewBox", `0 0 ${W} ${H}`).attr("role", "img");
      svg.append("g").attr("class", "eixo").attr("transform", `translate(0,${H - 22})`).call(d3.axisBottom(x).ticks(5).tickFormat(t => t + "%")).call(g => g.select(".domain").attr("stroke", C.linhaF));
      svg.append("line").attr("x1", x(50)).attr("x2", x(50)).attr("y1", 0).attr("y2", H - 22).attr("stroke", C.linha);
      svg.append("text").attr("class", "rot").attr("x", W - 8).attr("y", 10).attr("text-anchor", "end").text("diferença");
      INV_VIZINHAS.forEach(([u, n, e, a, v], i) => {
        const y = i * passo + 22, dica = `<b>${u}</b> · ${fInt(n)} seções<br>Abertas até perto das 19h: ${invP(a)}<br>Vizinhas da mesma zona: ${invP(v)}<br>Estado: ${invP(e)}`;
        svg.append("text").attr("class", "rot-forte").attr("x", mE - 12).attr("y", y - 2).attr("text-anchor", "end").text(u);
        svg.append("text").attr("class", "rot").attr("x", mE - 12).attr("y", y + 11).attr("text-anchor", "end").text(`${fInt(n)} seç${n === 1 ? "ão" : "ões"}`);
        svg.append("line").attr("x1", x(Math.min(a, v))).attr("x2", x(Math.max(a, v))).attr("y1", y).attr("y2", y).attr("stroke", C.linhaF).attr("stroke-width", 2);
        invDica(svg.append("circle").attr("cx", x(v)).attr("cy", y).attr("r", 6).attr("fill", C.papel).attr("stroke", C.tinta2).attr("stroke-width", 2), dica);
        invDica(svg.append("circle").attr("cx", x(a)).attr("cy", y).attr("r", 6).attr("fill", C.tinta).attr("stroke", C.papel).attr("stroke-width", 2), dica);
        svg.append("text").attr("class", "rot-medio").attr("x", W - 8).attr("y", y + 4).attr("text-anchor", "end").text(`${fSin(a - v, 1)} p.p.`);
      });
    },
  },
  biometria: {
    titulo: "Liberação por código e voto em Lula, por estado",
    como: "Cada ponto é um estado. Para a direita, mais eleitores liberados por código (digital não reconhecida); para cima, mais votos em Lula. Se a liberação favorecesse Lula, os pontos subiriam da esquerda para a direita. RS e SC, onde Flávio venceu, estão entre os que mais liberaram. Em telas estreitas, só alguns estados têm nome; os demais aparecem ao passar o mouse e na tabela.",
    tabela: () => ({ cab: ["UF", "Liberados por código (% do comparecimento)", "Lula (% dos válidos)"],
      linhas: Object.entries(INV_BIOMETRIA_UF).sort((p, q) => q[1][0] - p[1][0]).map(([u, [l, v]]) => [u, invP(l, 2), invP(v)]) }),
    desenhar: el => {
      const W = larg(el), H = 320, mE = 46, mB = 40, mT = 14;
      const x = d3.scaleLinear().domain([3.5, 9.5]).range([mE, W - 24]), y = d3.scaleLinear().domain([25, 80]).range([H - mB, mT]);
      const svg = d3.select(el).html("").append("svg").attr("viewBox", `0 0 ${W} ${H}`).attr("role", "img");
      svg.append("g").attr("class", "eixo").attr("transform", `translate(${mE},0)`).call(d3.axisLeft(y).ticks(6).tickSize(-(W - mE - 24)).tickFormat(t => t + "%"))
        .call(g => g.select(".domain").remove()).call(g => g.selectAll(".tick line").attr("stroke", C.linha));
      svg.append("g").attr("class", "eixo").attr("transform", `translate(0,${H - mB})`).call(d3.axisBottom(x).ticks(6).tickFormat(t => t + "%")).call(g => g.select(".domain").attr("stroke", C.linhaF));
      svg.append("text").attr("class", "rot").attr("x", W - 24).attr("y", H - 6).attr("text-anchor", "end").text("eleitores liberados por código (% do comparecimento) →");
      svg.append("text").attr("class", "rot").attr("x", mE + 4).attr("y", mT + 10).text("↑ votos em Lula (% dos válidos)");
      Object.entries(INV_BIOMETRIA_UF).forEach(([u, [l, v]]) => {
        invDica(svg.append("circle").attr("cx", x(l)).attr("cy", y(v)).attr("r", 5).attr("fill", C.tinta2).attr("stroke", C.papel).attr("stroke-width", 2),
          `<b>${u}</b><br>Liberados por código: ${invP(l, 2)}<br>Lula: ${invP(v)}`);
        if (W >= 520 || ["RS", "SC", "PI", "BA", "RR", "DF", "RJ", "SP"].includes(u)) svg.append("text").attr("class", "rot").attr("x", x(l) + 8).attr("y", y(v) + 4).text(u);
      });
    },
  },
  unanimes: {
    titulo: "Seções com mais de 90% dos votos válidos para um finalista",
    como: "Para cada eleição, a coluna vermelha conta as seções em que o candidato do PT teve mais de 90% dos votos válidos; a azul, as do candidato da direita. Em 2026 houve menos seções assim para o PT do que em 2018, eleição que o PT perdeu, e do que em 2022.",
    legenda: () => [[C.lula, "Candidato do PT"], [C.dir, "Candidato da direita"]],
    tabela: () => ({ cab: ["Eleição", "PT", "Seções > 90%", "Direita", "Seções > 90%", "Razão"],
      linhas: INV_UNANIMES.map(([a, p, d, np, nd]) => [a, p, fInt(np), d, fInt(nd), fNum(np / nd, 1) + " : 1"]) }),
    desenhar: el => invColunas(el, INV_UNANIMES.map(u => String(u[0])), [
      { nome: "Candidato do PT", cor: C.lula, valores: INV_UNANIMES.map(u => u[3]) },
      { nome: "Candidato da direita", cor: C.dir, valores: INV_UNANIMES.map(u => u[4]) }],
      { y1: 16000, fmt: fInt, rotY: "seções", rotular: () => true, H: 240,
        dicaCat: c => { const u = INV_UNANIMES.find(r => String(r[0]) === c); return `${c}: ${u[1]} × ${u[2]}`; } }),
  },
  benford1: {
    titulo: "Primeiro dígito dos votos por seção em 2026",
    como: "As colunas mostram em que porcentagem das seções a votação de cada candidato começa com cada dígito. Os pontos ligados são o que a lei de Benford prevê. Como as seções têm tamanho limitado, a maioria das contagens fica entre 100 e 199 e começa com 1: a lei de Benford não descreve esses números, com ou sem fraude.",
    legenda: () => [[C.lula, "Lula"], [C.dir, "Flávio"], [C.tinta2, "Previsto pela lei de Benford", "border-radius:50%"]],
    tabela: () => ({ cab: ["Primeiro dígito", "Lula", "Flávio", "Lei de Benford"], linhas: INV_DIG1.benford.map((b, i) => [i + 1, invP(INV_DIG1.lula[i]), invP(INV_DIG1.flavio[i]), invP(b)]) }),
    desenhar: el => invColunas(el, ["1", "2", "3", "4", "5", "6", "7", "8", "9"], [
      { nome: "Lula", cor: C.lula, valores: INV_DIG1.lula }, { nome: "Flávio", cor: C.dir, valores: INV_DIG1.flavio }],
      { y1: 70, fmt: v => invP(v, 0), rotY: "% das seções", marcas: { nome: "Lei de Benford", valores: INV_DIG1.benford }, rotular: (i, s, estreito) => i === 0 && !estreito, dicaCat: c => `Primeiro dígito ${c}` }),
  },
  benfordU: {
    titulo: "Último dígito dos votos por seção em 2026",
    como: "Teste proposto por Beber e Scacco: numa contagem honesta, cada dígito final de 0 a 9 aparece em cerca de 10% das seções; números inventados por pessoas costumam fugir disso. Os dois candidatos ficam em 10% em todos os dígitos.",
    legenda: () => [[C.lula, "Lula"], [C.dir, "Flávio"]],
    tabela: () => ({ cab: ["Último dígito", "Lula", "Flávio"], linhas: INV_DIGU.lula.map((v, i) => [i, invP(v, 2), invP(INV_DIGU.flavio[i], 2)]) }),
    desenhar: el => invColunas(el, ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"], [
      { nome: "Lula", cor: C.lula, valores: INV_DIGU.lula }, { nome: "Flávio", cor: C.dir, valores: INV_DIGU.flavio }],
      { y1: 15, fmt: v => invP(v, 2), fmtEixo: v => invP(v, 0), rotY: "% das seções", ref: { v: 10, rot: "esperado numa contagem honesta: 10%" }, dicaCat: c => `Último dígito ${c}`, H: 220 }),
  },
};

function invFigura(id) {
  const g = INV_GRAFICOS[id], t = g.tabela();
  return `<figure class="inv-fig">
    <figcaption><b>${esc(g.titulo)}</b><span class="nota">${esc(g.como)}</span></figcaption>
    ${g.legenda ? `<div class="legenda" id="invl-${id}"></div>` : ""}
    <div class="grafico" id="invg-${id}"></div>
    <details class="tecnico"><summary>Ver os números</summary><div><div class="tabela-wrap"><table>
      <thead><tr>${t.cab.map((h, j) => `<th class="${j ? "num" : ""}">${esc(h)}</th>`).join("")}</tr></thead>
      <tbody>${t.linhas.map(l => `<tr>${l.map((x, j) => `<td class="${j ? "num" : ""}">${esc(x)}</td>`).join("")}</tr>`).join("")}</tbody>
    </table></div></div></details>
  </figure>`;
}
/* desenha (ou redesenha, ao mudar o tamanho da tela ou o tema) todos os gráficos da aba */
function invGraficos() {
  Object.entries(INV_GRAFICOS).forEach(([id, g]) => {
    const el = $("#invg-" + id);
    if (!el) return;
    if (g.legenda) legenda($("#invl-" + id), g.legenda());
    g.desenhar(el);
  });
}

/* "28/10/2026, 22h21 (Brasília)" */
function invData(iso) {
  if (!iso) return "data não disponível";
  const p = Object.fromEntries(new Intl.DateTimeFormat("pt-BR", { timeZone: "America/Sao_Paulo", day: "2-digit", month: "2-digit",
    year: "numeric", hour: "2-digit", minute: "2-digit", hourCycle: "h23" }).formatToParts(new Date(iso)).map(x => [x.type, x.value]));
  return `${p.day}/${p.month}/${p.year}, ${p.hour}h${p.minute} (Brasília)`;
}
const invDia = d => d.split("-").reverse().join("/");
/* texto de verificação: uma frase só, ou uma lista em que cada string é um parágrafo
   e cada lista de pares [rótulo, texto] vira uma lista de itens */
const invTexto = v => (Array.isArray(v) ? v : [v]).map(b => typeof b === "string" ? `<p>${esc(b)}</p>`
  : `<ul class="inv-itens">${b.map(([r, t]) => `<li><b>${esc(r)}:</b> ${esc(t)}</li>`).join("")}</ul>`).join("");
const invPill = r => { const [c, t] = INV_RESULTADOS[r]; return `<span class="pill ${c}">${t}</span>`; };

function invCaso(c) {
  const A = c.arquivo, base = A.pasta;
  const pubs = c.publicacoes.map(p => `<li><b>${esc(p.plataforma)}</b> · ${esc(p.autor)} · ${esc(invData(p.publicado))}
      ${p.url ? `· <a href="${esc(p.url)}" rel="noopener">ver publicação</a>` : "· sem link disponível"}<br><span class="nota">${esc(p.papel)}</span></li>`).join("");
  const midia = A.video
    ? `<video class="inv-video" controls preload="none" poster="${base + A.capa}" src="${base + A.video}"></video>`
    : A.imagens ? `<div class="inv-galeria">${A.imagens.map((f, i) => `<a href="${base + f}" target="_blank" rel="noopener"><img src="${base + f}" loading="lazy" alt="Imagem ${i + 1} de ${A.imagens.length} da publicação arquivada"></a>`).join("")}</div>` : "";
  const refs = a => a.referencias ? a.referencias.map(g => `<div class="inv-refs"><b>${esc(g.grupo)}</b><ul>${g.itens.map(r =>
      `<li>${esc(r.texto)} <a href="${esc(r.url)}" rel="noopener">${esc(r.url.replace(/^https:\/\//, ""))}</a><br><span class="nota">${esc(r.resumo)}</span></li>`).join("")}</ul></div>`).join("") : "";
  const alegs = c.alegacoes.map((a, i) => `<li class="inv-aleg"><div class="inv-aleg-cab"><b>${i + 1}. ${esc(a.texto)}</b>${invPill(a.resultado)}</div>${invTexto(a.verificacao)}${(a.graficos || []).map(invFigura).join("")}${refs(a)}</li>`).join("");
  const fals = c.falacias.map(f => `<li><b>${esc(f.nome)}</b> <span class="nota">(<a href="${INV_FALACIA(f.n)}" rel="noopener">${esc(f.original)}</a> · ${esc(f.categoria)})</span><br>${esc(f.uso)}</li>`).join("");
  const resp = c.respostas.length ? `<div class="bloco"><h3>Respostas publicadas</h3><ul class="lista-lim">${c.respostas.map(r =>
      `<li><b>${esc(r.autor)}</b> · ${esc(invData(r.publicado))} · <a href="${esc(r.url)}" rel="noopener">ver resposta</a><br>“${esc(r.texto)}”${r.nota ? `<br><span class="nota">${esc(r.nota)}</span>` : ""}</li>`).join("")}</ul></div>` : "";
  return `<article class="inv-caso" id="caso-${c.id}">
    <div class="bloco">
      <div class="cab-bloco"><h3>${esc(c.titulo)}</h3>${invPill(c.resultado)}</div>
      <p class="nota">Registrado em ${invDia(c.registrado)}</p>
      <p>${esc(c.resumo)}</p>
    </div>
    <div class="grade-2">
      <div class="bloco"><h3>Publicações</h3><ul class="lista-lim">${pubs}</ul></div>
      <div class="bloco"><h3>Cópia arquivada</h3>${midia}
        <p class="nota">${esc(A.nota)} ${A.itens.map(([r, f]) => `<a href="${base + f}">${esc(r)}</a>`).join(" · ")}</p></div>
    </div>
    <div class="bloco"><h3>Contexto</h3>${c.contexto.map(p => `<p>${esc(p)}</p>`).join("")}</div>
    <div class="bloco"><h3>O que foi alegado e o que os dados mostram</h3><ol class="inv-alegs">${alegs}</ol></div>
    <div class="bloco"><h3>Análise</h3>${c.analise.map(p => `<p>${esc(p)}</p>`).join("")}</div>
    <div class="bloco"><h3>Falácias (classificação de Stephen Downes)</h3><ul class="lista-lim">${fals}</ul></div>
    ${resp}
  </article>`;
}

function invMontar() {
  const el = $("#inv-casos");
  if (!el.dataset.feito) invTextos(el);
  invGraficos();
}
function invTextos(el) {
  el.innerHTML = `<nav class="inv-indice" aria-label="Casos registrados"><ol>${INV_CASOS.map(c =>
      `<li><a href="#caso-${c.id}" data-caso="${c.id}">${esc(c.titulo)}</a> ${invPill(c.resultado)}</li>`).join("")}</ol></nav>` +
    INV_CASOS.map(invCaso).join("");
  // os links do índice rolam até o caso sem trocar a aba (o app.js trata "#id" como aba)
  el.querySelectorAll("a[data-caso]").forEach(a => a.addEventListener("click", e => {
    e.preventDefault(); $("#caso-" + a.dataset.caso).scrollIntoView({ behavior: "smooth", block: "start" });
  }));
  el.dataset.feito = "1";
}
