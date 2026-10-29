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
      { texto: "Se três seções deram 167 votos a mais para Flávio, a cidade não poderia ter dado só 93; portanto houve roubo.",
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
      { texto: "Nas urnas encerradas até as 17h, Flávio venceu com 52,39% e vantagem de quase 1,8 milhão; nas encerradas depois, Lula teve mais de 6,1 milhões de vantagem.",
        verificacao: "Os números se reproduzem com o BWeb usando a hora gravada no boletim, que é a hora local da seção: 150.742 seções “até 17h00”, Flávio 52,40%, vantagem de 1,75 milhão. Convertendo para a hora de Brasília, nenhuma seção fechou antes das 17h00: a primeira fechou 9 segundos depois e a mediana, 1,7 minuto depois. O grupo “até 17h00” reúne as seções que fecharam no primeiro minuto e todas as 32.026 seções de AC, AM, MS, MT, RO e RR, que fecham às 15h ou 16h locais (17h em Brasília); só essas dão 1,44 milhão da vantagem de Flávio. Dentro de cada estado, a diferença de votação entre seções que fecharam no primeiro minuto e as que fecharam de 1 a 15 minutos depois é de 0,4 ponto percentual (mediana).",
        resultado: "falso" },
      { texto: "Os 34 mil votos depois das 17h são um mito: mais de 2,5 milhões de eleitores votaram em urnas que passaram do limite.",
        verificacao: "O relatório compara coisas diferentes. Os 34.393 votos do TSE foram dados depois das 17h (a hora de cada voto vem do log da urna). Os 2,5 milhões são todos os eleitores, desde as 8h, das seções que fecharam depois das 17h15. O BWeb não registra a hora de cada voto. Das 6.757 seções que fecharam perto das 19h, o comparecimento foi 80,6%, contra 80,8% nas demais seções dos mesmos estados. Sem essas seções, Lula venceria por 4,24 milhões; mesmo que todos os votos delas fossem de Flávio, Lula venceria por 2,33 milhões.",
        resultado: "falso" },
      { texto: "Nas seções que entraram na noite, Lula teve índices avassaladores (Bahia 72,31%, Pernambuco 65,70%, Maranhão 83,31%, São Paulo 57,46%).",
        verificacao: "Os percentuais conferem, mas a tabela omite o Rio de Janeiro, o estado com mais seções fechadas perto das 19h (2.998), onde Lula teve 45,7%. O número do Maranhão vem de 3 seções com 634 eleitores. A votação nessas seções segue a de cada estado.",
        resultado: "enganoso" },
      { texto: "8.632.488 eleitores foram liberados sem biometria, quase o dobro da margem de 4.430.191; os votos de Lula sobem com a taxa de liberação manual.",
        verificacao: "O número é correto (campo QT_ELEI_BIOM_SEM_HABILITACAO do BWeb). Liberação por código é o procedimento para o eleitor com biometria cadastrada cuja digital não foi reconhecida: ele é identificado pelo mesário com documento. Comparar esse total com a margem só faria sentido se esses votos fossem irregulares e todos de Lula, e o relatório não apresenta indício de nenhuma das duas coisas. A correlação entre a taxa de liberação da seção e o voto em Lula é 0,06 no país e 0,01 entre seções do mesmo município. Estados onde Flávio venceu têm taxas altas (RS 8,5%, SC 7,5%). As faixas de liberação acima de 30% somam 348 seções.",
        resultado: "enganoso" },
      { texto: "Lula teve 100% dos votos em 106 seções e mais de 90% em 6.899, contra 4 e 384 de Flávio (18 para 1): uma anomalia concentrada em zonas rurais com pouca fiscalização.",
        verificacao: "As contagens conferem (6.816 e 378 com “mais de 90%”). Comparando com as eleições anteriores, pelo mesmo cálculo: em 2018, quando o PT perdeu por 10,8 milhões, Haddad teve 14.958 seções acima de 90% contra 1.298 de Bolsonaro (11,5 para 1); em 2022, Lula teve 9.433 contra 213 (44 para 1). Em 2026 houve menos seções quase unânimes para o PT do que nas duas eleições anteriores. A assimetria acontece porque o voto no PT é geograficamente concentrado. O relatório não apresenta dado sobre fiscalização nessas seções.",
        resultado: "enganoso" },
      { texto: "Os microdados de horários e biometria ficaram 72 horas em sigilo e só foram liberados na manhã de 28/10.",
        verificacao: "O BWeb do 2º turno foi gerado em 26/10 às 07h42 e está no CDN do TSE desde 26/10 por volta das 9h (Brasília). Os boletins de urna de cada seção, com os mesmos campos, estavam no site de resultados do TSE em 26/10: este projeto baixou 50.821 deles naquele dia. O boletim impresso de cada seção é afixado no local de votação ao fim da apuração.",
        resultado: "falso" },
      { texto: "O teste de Benford aplicado às 499.205 seções indica manipulação.",
        verificacao: "O relatório não mostra o resultado do teste: diz que os gráficos não foram incluídos. Para avaliar a alegação, este projeto aplicou às seções de 2018, 2022 e 2026 o teste usado no dossiê e os dois testes de dígitos propostos pelos pesquisadores que defendem esse tipo de análise. (1) Primeiro dígito, o teste do dossiê: rejeita a lei de Benford com valor-p praticamente zero para os dois finalistas das três eleições, inclusive em 2018, quando o PT perdeu. A causa é o tamanho limitado das seções: em 2026, 90% delas tiveram entre 161 e 334 votantes, então a maior parte das contagens de cada candidato fica entre 100 e 199 e começa com 1 (61% das seções para Lula e 62% para Flávio, contra 30% pela lei de Benford). Críticos e defensores dos testes de dígitos concordam que, nessas condições, o primeiro dígito não serve para o propósito. (2) Segundo dígito, defendido por Mebane e por Pericchi e Torres: também rejeita a lei nas três eleições, para os dois finalistas. Com quase 500 mil seções, desvios pequenos produzem valor-p próximo de zero, e os próprios defensores dizem que esse desvio, sozinho, não é evidência de fraude e pede estudo adicional. (3) Último dígito, proposto por Beber e Scacco para detectar números inventados por pessoas: em 2026, cada dígito de 0 a 9 aparece em 10,0% das seções, tanto para Lula (p = 0,84) quanto para Flávio (p = 0,19). Por estado, 3 de 56 testes rejeitam a uniformidade ao nível de 5% (Lula em MT e RO, Flávio no DF), o que se espera do acaso em 56 testes; nenhum rejeita após a correção para múltiplos testes. O estudo adicional que um alarme pediria é o que este painel faz nas outras alegações e abas: conferência dos boletins de urna, das contas oficiais e da votação por seção.",
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
        uso: "Apresenta as seções quase unânimes de 2026 sem compará-las com 2018 e 2022, que têm mais seções desse tipo para o PT. Na tabela de estados com seções abertas à noite, omite o Rio de Janeiro, onde Flávio venceu nessas seções." },
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

/* "28/10/2026, 22h21 (Brasília)" */
function invData(iso) {
  if (!iso) return "data não disponível";
  const p = Object.fromEntries(new Intl.DateTimeFormat("pt-BR", { timeZone: "America/Sao_Paulo", day: "2-digit", month: "2-digit",
    year: "numeric", hour: "2-digit", minute: "2-digit", hourCycle: "h23" }).formatToParts(new Date(iso)).map(x => [x.type, x.value]));
  return `${p.day}/${p.month}/${p.year}, ${p.hour}h${p.minute} (Brasília)`;
}
const invDia = d => d.split("-").reverse().join("/");
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
  const alegs = c.alegacoes.map((a, i) => `<li class="inv-aleg"><div class="inv-aleg-cab"><b>${i + 1}. ${esc(a.texto)}</b>${invPill(a.resultado)}</div><p>${esc(a.verificacao)}</p>${refs(a)}</li>`).join("");
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
  if (el.dataset.feito) return;
  el.innerHTML = `<nav class="inv-indice" aria-label="Casos registrados"><ol>${INV_CASOS.map(c =>
      `<li><a href="#caso-${c.id}" data-caso="${c.id}">${esc(c.titulo)}</a> ${invPill(c.resultado)}</li>`).join("")}</ol></nav>` +
    INV_CASOS.map(invCaso).join("");
  // os links do índice rolam até o caso sem trocar a aba (o app.js trata "#id" como aba)
  el.querySelectorAll("a[data-caso]").forEach(a => a.addEventListener("click", e => {
    e.preventDefault(); $("#caso-" + a.dataset.caso).scrollIntoView({ behavior: "smooth", block: "start" });
  }));
  el.dataset.feito = "1";
}
