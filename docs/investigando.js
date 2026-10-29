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
    id: "reels-silva-jardim-1-voto",
    titulo: "Reels “Flávio ganhou apenas 1 voto” em Silva Jardim (RJ)",
    registrado: "2026-10-29",
    resultado: "falso",
    resumo: "Num vídeo com animações, um perfil que ensina a usar inteligência artificial em negócios afirma que, em Silva Jardim (RJ), Flávio teve só 1 voto a mais no 2º turno do que no 1º, enquanto Lula teve 984 a mais, com 104 eleitores a menos, e que uma simulação de Monte Carlo mostra que isso é mais difícil do que ganhar a Mega-Sena 61 vezes seguidas. Os números da cidade estão corretos. A probabilidade não: os 985 votos que os dois finalistas ganharam juntos são exatamente os votos dos candidatos eliminados mais a queda de brancos e nulos, menos os eleitores que deixaram de votar. E Flávio teve no máximo 1 voto a mais no 2º turno em 958 dos 5.571 municípios do país.",
    publicacoes: [
      { plataforma: "Instagram", autor: "Pedro Laterza (@soupedrolaterza)", url: "https://www.instagram.com/reels/DfDy8rEyVgW/",
        publicado: "2026-10-29T01:44:34Z", papel: "Publicação analisada. No arquivamento: 1,19 milhão de reproduções, 128.724 curtidas e 2.213 comentários." },
    ],
    arquivo: {
      pasta: "investigando/arquivo/instagram_DfDy8rEyVgW/",
      video: "video.mp4", capa: "capa.jpg",
      itens: [["Vídeo (MP4, 720×1280, 1min08s)", "video.mp4"], ["Transcrição do áudio", "transcricao.txt"], ["Legenda da publicação", "legenda.txt"],
        ["Metadados", "metadados.json"], ["Hashes SHA-256", "SHA256SUMS"]],
      nota: "Arquivado em 29/10/2026, com o vídeo na resolução original. Transcrição automática feita localmente (faster-whisper).",
    },
    contexto: [
      "O vídeo tem narração e animações: cartazes com os votos de cada turno, uma moeda, bolas da Mega-Sena e um gráfico de pontos com o rótulo “simulações”. A legenda da publicação só convida a seguir o perfil para “aprender a usar IA para prosperar seus negócios”. No fim, o narrador diz que fez os cálculos com “os dados oficiais do TSE e Inteligência Artificial” e convida quem quer usar inteligência artificial “no seu dia a dia, nos seus negócios” a segui-lo.",
      "O narrador diz que, em Silva Jardim, Flávio teve 8.932 votos no 1º turno e 8.933 no 2º, e Lula, 4.450 e 5.434; que houve 104 eleitores a menos; que, portanto, “quase 1000 votos se mexeram de lado”; e que, “usando o modelo de cálculo Monte Carlo”, é mais fácil ganhar a Mega-Sena 61 vezes seguidas ou acertar cara ou coroa 1.550 vezes do que “ganhar apenas 1 voto no seu segundo turno”.",
    ],
    alegacoes: [
      { texto: "Em Silva Jardim (RJ), Flávio passou de 8.932 para 8.933 votos e Lula, de 4.450 para 5.434, com 104 eleitores a menos.",
        verificacao: "Confere com os dados do TSE para as 61 seções do município. O comparecimento caiu de 14.909 para 14.805 eleitores, 104 a menos.",
        resultado: "correto" },
      { graficos: ["silvajardim_conta"], texto: "Como não houve mais gente votando, quase mil votos “se mexeram de lado”.",
        verificacao: [
          "Os números não exigem que algum eleitor tenha trocado Flávio por Lula. No 1º turno, 897 eleitores de Silva Jardim votaram nos candidatos eliminados (Augusto Cury, Ronaldo Caiado, Renan Santos e outros), e 630 votaram em branco ou nulo; no 2º turno, brancos e nulos foram 438, 192 a menos. Somando os votos dos eliminados e a queda de brancos e nulos, e descontando os 104 eleitores que deixaram de votar, chega-se a 985 votos, exatamente o que Lula e Flávio ganharam juntos (984 + 1).",
          "A parte que foi para Lula é comum no estado. Em Silva Jardim, Lula ganhou 1,10 voto para cada voto dado aos eliminados no 1º turno; essa razão é a mediana dos 92 municípios do Rio de Janeiro, e Silva Jardim é o 43º da lista. O que distingue a cidade é Flávio ter ganhado poucos votos, e isso também aconteceu em municípios próximos: em Tanguá, Flávio teve 4 votos a menos que no 1º turno; em Araruama, 11 a mais; em Casimiro de Abreu, 92 a mais.",
          "O “1 voto” é um saldo. Flávio teve mais votos que no 1º turno em 36 seções da cidade (161 a mais) e menos em 22 (160 a menos). O saldo combina eleitores dele que deixaram de votar ou mudaram de voto com eleitores que vieram dos candidatos eliminados.",
        ],
        resultado: "enganoso" },
      { graficos: ["silvajardim_municipios"], texto: "Pelo modelo de Monte Carlo, Flávio ganhar só 1 voto é mais difícil do que ganhar a Mega-Sena 61 vezes seguidas ou acertar cara ou coroa 1.550 vezes.",
        verificacao: [
          "Acertar cara ou coroa 1.550 vezes seguidas tem chance de 1 em 2 elevado a 1.550, um número de 467 algarismos; ganhar a Mega-Sena 61 vezes seguidas dá um número de tamanho parecido. Uma simulação de Monte Carlo estima uma probabilidade contando em quantos sorteios o evento acontece. Com cerca de 1 milhão de sorteios, como no contador “simulações” do vídeo (que chega a 999.041), a menor probabilidade que se consegue medir fica perto de 1 em 1 milhão. Uma chance de 1 em um número de 467 algarismos não pode ter saído dessa simulação. O vídeo não diz que modelo foi simulado. O gráfico de pontos com um quarto de círculo que ilustra a simulação é o exemplo usado em aulas para estimar o número π com o método de Monte Carlo e não tem relação com votos.",
          "Uma probabilidade desse tamanho só aparece se cada voto for tratado como um lançamento de moeda, independente dos outros. Eleitores de uma mesma cidade não votam assim, e os resultados mostram isso: Flávio teve no 2º turno no máximo 1 voto a mais que no 1º em 958 dos 5.571 municípios, e teve menos votos que no 1º turno em 938 deles. No Rio de Janeiro, isso aconteceu em 12 dos 92 municípios. O resultado que o vídeo diz ser mais raro que ganhar a Mega-Sena 61 vezes seguidas aconteceu em cerca de um de cada seis municípios do país.",
        ],
        resultado: "falso" },
    ],
    analise: [
      "O vídeo escolhe, entre 5.571 municípios, um em que Flávio quase não ganhou votos, e calcula a chance desse resultado depois de já saber que ele aconteceu. Procurando entre milhares de municípios, sempre se encontra algum com um resultado incomum. A pergunta que importa é se resultados assim são raros no conjunto, e não são: há 958 municípios em que Flávio teve no 2º turno no máximo 1 voto a mais que no 1º, e em 938 deles teve menos votos.",
      "A conta da cidade fecha sem troca de votos entre Lula e Flávio: os votos que os dois ganharam vêm dos candidatos eliminados e da queda de brancos e nulos. A probabilidade do vídeo vem de um modelo que não é mostrado e que trata cada eleitor como uma moeda. As animações da simulação, da moeda e da Mega-Sena e a menção a inteligência artificial dão aparência técnica a um cálculo que não é apresentado.",
    ],
    falacias: [
      { nome: "Falácia da exclusão", original: "Fallacy of Exclusion", n: 20, categoria: "Falácias indutivas",
        uso: "Deixa de fora os outros 957 municípios em que Flávio teve no 2º turno no máximo 1 voto a mais que no 1º, entre eles Tanguá, também no Rio de Janeiro, onde ele teve 4 votos a menos. Com esses municípios, o resultado de Silva Jardim deixa de parecer excepcional." },
      { nome: "Falsa analogia", original: "False Analogy", n: 18, categoria: "Falácias indutivas",
        uso: "Compara o voto dos eleitores a lançamentos de moeda e a sorteios da Mega-Sena, que são independentes entre si. Eleitores de uma mesma cidade votam de forma parecida, e por isso resultados como o de Silva Jardim se repetem em centenas de municípios." },
      { nome: "Equívoco", original: "Equivocation", n: 31, categoria: "Falácias de ambiguidade",
        uso: "Usa “ganhou apenas 1 voto” e “quase 1000 votos se mexeram de lado” para diferenças entre os totais dos dois turnos, como se fossem eleitores. O 1 voto a mais de Flávio é o saldo de 161 votos a mais em 36 seções e 160 a menos em 22." },
      { nome: "Estilo em vez de substância", original: "Style Over Substance", n: 15, categoria: "Mudança de assunto",
        uso: "Mostra animações de uma simulação, de bolas da Mega-Sena e de uma moeda, e cita inteligência artificial, mas não mostra o modelo nem o cálculo. O gráfico de pontos com o rótulo “simulações” é o exemplo usado em aulas para estimar o número π." },
    ],
    respostas: [],
  },
  {
    id: "reels-professor-curva-apuracao",
    titulo: "Reels “Fomos roubados!”: professor e a curva da apuração",
    registrado: "2026-10-29",
    resultado: "falso",
    resumo: "Um perfil de notícias republicou, com o título “Professor questiona apuração e levanta suspeitas sobre derrota de Flávio Bolsonaro”, um vídeo em que um homem que se apresenta como professor de matemática mostra a curva da apuração, diz que um “algoritmo” penaliza Bolsonaro sempre que ele tende a subir e estima que, sem isso, Bolsonaro teria entre 60% e 65% dos votos. A análise mostrada é da eleição de 2022, e não da de 2026: usa as 472 mil seções e o placar de 49% a 51% daquele ano. O argumento também não se sustenta em nenhum dos dois anos: o resultado final é a soma dos votos de todas as seções e é o mesmo em qualquer ordem de chegada; a ordem muda apenas o formato da curva até o resultado final.",
    publicacoes: [
      { plataforma: "Instagram", autor: "Apoio Vitória Fm 87,9 (@vitorianewsparacatu), com @vitorianewsbrasil como coautor",
        url: "https://www.instagram.com/reels/DfBTF4LtGzB/", publicado: "2026-10-28T01:54:35Z",
        papel: "Publicação analisada. No arquivamento: 2,29 milhões de reproduções, 225.766 curtidas e 8.550 comentários." },
      { plataforma: "Vídeo original", autor: "Marcelo Trindade (como se apresenta no vídeo)", url: null, publicado: null,
        papel: "Autor da análise. Pela fala (“eu quero que essa live chegue [a] mil pessoas”), o trecho vem de uma transmissão ao vivo. A gravação original não foi localizada." },
    ],
    arquivo: {
      pasta: "investigando/arquivo/instagram_DfBTF4LtGzB/",
      video: "video.mp4", capa: "capa.jpg",
      itens: [["Vídeo (MP4, 720×900, 2min54s)", "video.mp4"], ["Transcrição do áudio", "transcricao.txt"],
        ["Quadro com o caminho do caderno Jupyter (pasta “Eleições 2022”)", "quadro_caderno.jpg"], ["Legenda da publicação", "legenda.txt"],
        ["Metadados", "metadados.json"], ["Hashes SHA-256", "SHA256SUMS"]],
      nota: "Arquivado em 29/10/2026, com o vídeo na resolução original. Transcrição automática feita localmente (faster-whisper).",
    },
    contexto: [
      "A tela do vídeo é dividida. Em cima fica o título, em amarelo. Embaixo, à esquerda, um trecho ampliado de uma curva; à direita, o autor falando e a tela de um computador com um caderno Jupyter que desenha duas curvas, uma azul e uma vermelha, que começam afastadas, se aproximam e se cruzam uma vez perto do fim. Pela descrição do autor, cada ponto é a porcentagem de um candidato somando as urnas recebidas até ali, na ordem em que foram enviadas.",
      "O autor diz que um candidato que perdeu com 49% para outro que ganhou com 51% não poderia ter “apenas uma inversão” na apuração; que baixou “essas mesmas 472 urnas” e simulou outras ordens de envio, e que todas tinham alternância; e que, como o envio é aleatório, não pode haver “tendência linear parcial”. Mostrando trechos da curva, diz que “o algoritmo” detecta quando Bolsonaro tende a subir e o “penaliza linearmente”, e que, recolocando os trechos de subida no lugar dos trechos de queda, Bolsonaro teria vencido “com 60 a 65% dos votos”. Termina: “tenho a certeza de que fomos roubados em 2022, tenho a certeza de que estamos sendo roubados novamente em 2026”.",
      "A legenda da publicação apresenta o vídeo como questionamento dos gráficos da apuração de 2026 e diz que Flávio poderia ter alcançado entre 60% e 65%. Mais abaixo, a mesma legenda informa que não há comprovação independente de manipulação de votos e que os gráficos parciais mudam conforme a ordem de chegada dos boletins de urna.",
    ],
    alegacoes: [
      { texto: "O vídeo questiona a apuração de 2026 e a derrota de Flávio Bolsonaro (título e legenda da publicação).",
        verificacao: "A análise mostrada é da eleição de 2022. O autor fala em “472 urnas” baixadas do site oficial: a eleição de 2022 teve 472.075 seções, e a de 2026, 499.248. Descreve um candidato que perdeu com 49% para outro que ganhou com 51%: em 2022, Jair Bolsonaro teve 49,10% dos votos válidos e Lula, 50,90%; em 2026, Flávio teve 48,21% e Lula, 51,79%. O caminho do caderno Jupyter que aparece na tela inclui uma pasta chamada “Eleições 2022”. O autor se refere a “Bolsonaro” e conclui que “fomos roubados em 2022”; 2026 aparece só na última frase, sem nenhum dado. O título sobre a derrota de Flávio Bolsonaro e a legenda foram acrescentados por quem republicou o vídeo.",
        resultado: "falso" },
      { texto: "Numa disputa de 49% a 51%, só uma inversão na apuração é raríssima; nas outras ordens de envio simuladas, todas tinham alternância.",
        verificacao: "Este projeto repetiu o teste com as seções de 2022, somadas em 200 ordens sorteadas ao acaso. A liderança troca de candidato só no começo, quando ainda há poucas urnas somadas: em nenhuma das 200 ordens houve troca depois da 4.141ª seção, menos de 1% do total, e daí em diante Lula fica à frente até o fim. Depois de somados 10% das seções, a porcentagem acumulada não se afasta mais de 0,25 ponto do resultado final. Em ordem aleatória, portanto, o esperado é não haver inversão depois do começo. A apuração real teve uma inversão tardia (em 2022, Lula passou à frente com cerca de dois terços das urnas apuradas) justamente porque as urnas não chegam em ordem aleatória (alegação seguinte).",
        resultado: "falso" },
      { graficos: ["professor_ordens"], texto: "O envio das urnas é aleatório; por isso, uma tendência de queda num trecho da curva só pode ser obra de um algoritmo que penaliza o candidato.",
        verificacao: [
          "As urnas não chegam à totalização em ordem aleatória. A ordem depende da hora em que cada seção encerra a votação, do tempo de apuração e transmissão e do lugar onde ela fica: seções com fila fecham mais tarde, e algumas regiões transmitem antes de outras. Como o voto também varia de um lugar para outro, a porcentagem acumulada de cada candidato muda aos poucos ao longo da apuração, com trechos longos de subida ou de queda.",
          "O gráfico abaixo usa as seções de 2026, com os votos oficiais de cada uma, somadas em ordens diferentes. Na ordem em que as seções encerraram a votação, a porcentagem de Lula sobe quase em linha reta de 45,9% para 51,8%, e ele só passa à frente com metade das seções somadas. Na ordem dos estados (AC, AL, AM...), a curva sobe até 66% e depois desce. Em três ordens sorteadas, a curva fica em 51,8% quase desde o começo. As tendências aparecem só porque a ordem muda, e todas as curvas terminam no mesmo ponto: 51,79%.",
          "O vídeo não apresenta nenhum dado sobre o “algoritmo”; ele é deduzido apenas do formato da curva. Os votos de cada seção são publicados pelo TSE, e, somando as 499.248 seções de 2026, os votos válidos e o comparecimento de cada município são iguais aos totais que o TSE divulgou.",
        ],
        resultado: "falso" },
      { graficos: ["professor_zonas"], texto: "No trecho ampliado, Bolsonaro sobe e logo cai, “devolvendo” quase tudo o que subiu; esse padrão de subidas lentas e quedas rápidas indica um algoritmo que corrige a curva para baixo.",
        verificacao: [
          "Cada ponto da curva é a porcentagem de Bolsonaro nos votos somados até ali. Quando entra um novo grupo de seções, a curva se move de acordo com uma conta: a variação é o peso do grupo no total já somado multiplicado pela diferença entre a porcentagem de Bolsonaro no grupo e a porcentagem acumulada. Se o grupo deu a Bolsonaro mais que a média até ali, a curva sobe; se deu menos, desce. Três consequências dessa conta explicam o que o vídeo mostra:",
          [
            ["Cada queda é um grupo de seções que chegou junto", "Com cerca de 76 mil seções já somadas, como no ponto destacado no vídeo, uma seção sozinha pesa cerca de 1/76.000 do total e move a curva no máximo 0,0007 ponto. As quedas do trecho ampliado, de 0,1 a 0,15 ponto, exigem centenas de seções chegando juntas e votando de forma parecida, como as de uma zona eleitoral, que são apuradas e transmitidas na mesma região."],
            ["A curva tem de devolver o que sobe", "O último ponto é o resultado final, que é o mesmo em qualquer ordem de soma. Toda subida acima desse valor tem de ser seguida de uma descida. Isso vale até em ordem sorteada: pela teoria da amostragem sem reposição, a porcentagem acumulada se aproxima do resultado final à medida que mais seções são somadas e chega exatamente a ele na última."],
            ["As quedas são mais rápidas que as subidas", "Em 2022, nas 2.637 zonas eleitorais, as zonas em que Bolsonaro ficou abaixo da média nacional estavam, na mediana, 18,5 pontos abaixo dela; as zonas em que ficou acima estavam 10,8 pontos acima. Por seção somada, uma zona do primeiro grupo baixa a curva cerca de 1,7 vez mais depressa do que uma zona do segundo grupo a levanta. Por isso a curva tende a subir aos poucos e cair de uma vez."],
          ],
          "O gráfico abaixo usa as seções de 2022, sem nenhuma alteração nos votos. As zonas eleitorais foram somadas em ordem sorteada, cada uma com todas as suas seções em sequência, e o trecho de 70 mil a 80 mil seções foi ampliado como no vídeo. Aparecem as mesmas subidas seguidas de quedas: a zona 345 de São Paulo levanta a curva 0,07 ponto, e logo depois a zona 71 da Bahia a baixa 0,09. Este projeto repetiu o sorteio 100 vezes. Nesse trecho, a distância entre o ponto mais alto e o mais baixo da curva ficou entre 0,22 e 0,80 ponto (mediana de 0,40) e foi de pelo menos 0,3 ponto, a altura do eixo ampliado no vídeo, em 85 dos 100 sorteios. O gráfico mostra o sorteio com a distância mais próxima da mediana.",
          "O vídeo chama de normais os trechos de subida e atribui ao algoritmo os de queda. Com essa regra, qualquer curva confirma a explicação. Para testá-la, seria preciso identificar as seções que entraram em cada queda e mostrar que os votos delas foram alterados. Os votos de cada seção são publicados pelo TSE, e o boletim de cada seção é afixado no local de votação; o vídeo não aponta nenhuma seção.",
        ],
        resultado: "falso" },
      { texto: "Sem a “penalização”, Bolsonaro teria vencido com 60% a 65% dos votos.",
        verificacao: "A porcentagem final é a soma dos votos de todas as seções e não depende da ordem em que elas são somadas: como mostra o gráfico anterior, qualquer ordem termina no mesmo resultado. Colocar os trechos de subida no lugar dos trechos de queda não corresponde a nenhuma ordem de envio; equivale a deixar de contar as seções em que Lula teve mais votos. Para Jair Bolsonaro ter 60% em 2022, seria preciso que 12,9 milhões de votos de Lula tivessem ido para ele, ou que 21,5 milhões de votos de Lula (36% do que ele teve) não fossem contados. Em 2026, para Flávio ter 60%, 14,6 milhões de votos teriam de passar de Lula para ele. O vídeo não mostra como chegou à estimativa.",
        resultado: "falso" },
    ],
    analise: [
      "O vídeo trata o formato da curva da apuração como prova, mas esse formato depende da ordem em que as urnas são somadas, e não dos votos. Somando os mesmos votos em ordens diferentes, obtêm-se curvas que sobem, que descem, que cruzam 50% uma vez ou nenhuma, e todas terminam no mesmo resultado. Por isso, nenhuma leitura da curva pode mostrar que votos foram alterados. Isso só pode ser verificado comparando os votos de cada seção com o total, e eles conferem.",
      "O “algoritmo” que liga quando Bolsonaro tende a subir e desliga em seguida serve para explicar qualquer curva: toda subida é atribuída ao padrão normal, e toda queda, ao algoritmo. Não há formato de curva que contradiga essa explicação, e por isso ela não pode ser testada.",
      "A publicação usa uma análise da eleição de 2022 com um título sobre a derrota de Flávio Bolsonaro em 2026. A legenda reconhece que não há comprovação e que os gráficos parciais mudam conforme a ordem de chegada dos boletins, mas o título e o início da legenda apresentam a acusação como notícia.",
    ],
    falacias: [
      { nome: "Petição de princípio", original: "Begging the Question", n: 28, categoria: "Fuga ao assunto",
        uso: "Supõe que existe um algoritmo (“o algoritmo detecta”, “o algoritmo é desligado”) para explicar os trechos de queda da curva e depois usa esses mesmos trechos como prova de que o algoritmo existe." },
      { nome: "Intestabilidade", original: "Untestability", n: 48, categoria: "Falácias de explicação",
        uso: "Um algoritmo que liga quando Bolsonaro tende a subir e desliga logo depois explica qualquer formato de curva. Nenhum resultado de apuração poderia contradizer essa explicação." },
      { nome: "Efeito conjunto", original: "Joint Effect", n: 24, categoria: "Falácias causais",
        uso: "Atribui as tendências da curva a um algoritmo. A causa das tendências é a localização das seções, que determina ao mesmo tempo quando elas chegam à totalização e como votaram." },
      { nome: "Apelo à autoridade", original: "Appeal to Authority", n: 12, categoria: "Mudança de assunto",
        uso: "Apoia a conclusão no doutorado e nos anos de trabalho do autor com matemática e ciência de dados (“estou com a certeza absoluta”), e não num cálculo apresentado." },
      { nome: "Linguagem tendenciosa", original: "Prejudicial Language", n: 8, categoria: "Apelos a motivos em vez de razões",
        uso: "“Golpe” e “fomos roubados” são ditos antes de qualquer demonstração; a republicação põe “FOMOS ROUBADOS!” no título." },
    ],
    respostas: [],
  },
  {
    id: "video-whatsapp-vereador",
    titulo: "Vídeo de vereador no WhatsApp: “só existe um caminho” para os votos de Lula",
    registrado: "2026-10-29",
    resultado: "falso",
    resumo: "Num vídeo que circulou pelo WhatsApp, um vereador escreve num quadro os números dos dois turnos, supõe que nenhum eleitor de Flávio votou em Lula e conclui que, nesse caso, Lula só poderia ter crescido recebendo 100% dos brancos, dos nulos e das abstenções e 60% dos votos dos outros candidatos, o que ele considera impossível. Os números do quadro estão quase todos corretos. A conclusão não: a queda de brancos, nulos e abstenções é uma diferença entre os turnos, não um grupo de pessoas, e há muitos caminhos que fecham as contas sem nenhuma troca entre Lula e Flávio. O vídeo não demonstra que o resultado é impossível; mostra que o autor o considera improvável.",
    publicacoes: [
      { plataforma: "WhatsApp", autor: "Vereador Dr. Ranieri (nome na marca do vídeo; município não identificado)", url: null, publicado: null,
        papel: "Vídeo encaminhado, recebido em 26/10/2026 às 16h24. A publicação original não foi localizada." },
    ],
    arquivo: {
      pasta: "investigando/arquivo/whatsapp_2026-10-26_162443/",
      video: "video.mp4", capa: "quadro_numeros.jpg",
      itens: [["Vídeo (MP4, 720×1280, 3min52s)", "video.mp4"], ["Transcrição do áudio", "transcricao.txt"],
        ["Metadados e números do quadro", "metadados.json"], ["Hashes SHA-256", "SHA256SUMS"]],
      nota: "Arquivado em 29/10/2026 a partir do arquivo recebido pelo WhatsApp, sem alteração. Transcrição automática feita localmente (faster-whisper).",
    },
    contexto: [
      "Foi este vídeo que motivou o estudo de transferência de votos apresentado nas outras abas deste painel.",
      "O vereador apresenta a análise como feita “sem nenhum tipo de paixão”, com “aritmética e a lei da probabilidade”. Escreve num quadro os votos do 1º turno (Flávio 56.104.503, Lula 53.879.538, brancos 2.300.798, nulos 3.674.249, abstenções 33.000.000 e 9.316.747 votos dos outros candidatos) e do 2º turno (Flávio 59.818.887, Lula 64.241.786, brancos 1.430.039, nulos 2.722.289, abstenções 30.000.000). Depois pergunta: “Você acredita que algum eleitor do Flávio votou no Lula ou algum eleitor do Lula votou no Flávio numa eleição extremamente polarizada? Eu não acredito.” A partir dessa premissa, calcula o que Lula teria de receber dos outros grupos e termina: “Você acha factível isso? Eu não engulo essa.”",
    ],
    alegacoes: [
      { texto: "A soma do 2º turno (158.213.001) é 62 mil votos menor que a do 1º (158.275.835), uma diferença que “cabe ao TSE explicar”.",
        verificacao: "Os dois totais do quadro não são o eleitorado. As abstenções foram arredondadas para 33.000.000 e 30.000.000, quando os números oficiais são 33.469.667 e 30.509.428, e os votos do 2º turno são de uma apuração anterior à final (Lula 64.241.786 no quadro e 64.256.232 no resultado final). Com os números oficiais, os dois turnos somam exatamente o mesmo total: 158.745.502 eleitores aptos. Os 62.834 votos de diferença vêm só desses arredondamentos: faltam 469.667 eleitores na soma do 1º turno e 532.501 na do 2º. A conta votos + brancos + nulos + abstenções = eleitores aptos confere em cada uma das 499.248 seções, nos dois turnos.",
        resultado: "falso" },
      { texto: "Nenhum eleitor de Flávio votou em Lula, e nenhum eleitor de Lula votou em Flávio.",
        verificacao: "O voto é secreto, e os resultados por seção não permitem contar quantos eleitores trocaram de candidato. O vídeo apresenta a premissa como crença (“Eu não acredito”), sem dado. As estimativas deste projeto, feitas comparando as seções, ficam próximas de zero; a auditoria metodológica mostra que os dados permitem afirmar que essa troca ficou entre 0% e cerca de 11%. A premissa, portanto, é compatível com os dados. O problema está no que o vídeo conclui a partir dela (alegação seguinte).",
        resultado: "naoverificado" },
      { graficos: ["ranieri_fluxos"], texto: "Sem essa troca, só existe um caminho: Lula teria de receber 100% dos brancos, 100% dos nulos, 100% dos 3 milhões de abstenções e 60% dos votos dos outros candidatos, o que não é factível.",
        verificacao: [
          "A conta do vídeo usa as diferenças entre os turnos como se fossem grupos de pessoas. Brancos e nulos caíram 1,82 milhão, e a abstenção caiu 2,96 milhões, mas essas são diferenças líquidas. No 1º turno, 5,98 milhões de pessoas votaram em branco ou nulo e 33,47 milhões não votaram. O que o vídeo chama de “100% dos brancos e nulos” corresponde a 30% dessas 5,98 milhões de pessoas, e os “100% das abstenções”, a 9% das 33,47 milhões. As diferenças líquidas também escondem movimentos nos dois sentidos: parte de quem votou no 1º turno deixou de votar no 2º, e por isso mais gente do que a diferença indica passou a votar.",
          "Por isso existem muitos caminhos, e não um só, que fecham todas as contas sem troca entre Lula e Flávio. O gráfico abaixo compara o caminho do vídeo com a estimativa deste projeto feita a partir das 499 mil seções. Na estimativa, a troca entre Lula e Flávio fica perto de zero; Lula recebe 43% dos votos dos outros candidatos, 61% de quem votou em branco ou nulo e 10% de quem não votou no 1º turno; e uma pequena parte dos eleitores de cada um deixa de votar. A estimativa depende de hipóteses discutidas na aba “Para onde foram os votos” e na auditoria metodológica: é um exemplo de caminho compatível com os dados, não uma medida exata.",
          "O que a aritmética de fato exige é bem menos do que o vídeo afirma: Lula precisou de pelo menos 1,06 milhão de votos vindos de quem não votou nele nem nos eliminados no 1º turno (1,84 milhão somando município por município). O vídeo não calcula nenhuma probabilidade; a frase “não é factível” é a opinião do autor.",
        ],
        resultado: "falso" },
      { texto: "Os candidatos derrotados no 1º turno declararam apoio a Flávio, e o governo estava mal avaliado; por isso os eleitores deles não iriam para Lula.",
        verificacao: "Os apoios declarados e a avaliação do governo são contexto político e não foram verificados. Mesmo que sejam verdadeiros, o apoio de um candidato derrotado não determina o voto dos seus eleitores. Nas estimativas deste projeto, os votos dos candidatos eliminados se dividiram entre Lula (43%) e Flávio (39%), e o restante votou em branco, nulo ou deixou de votar.",
        resultado: "naoverificado" },
    ],
    analise: [
      "O vídeo se apresenta como uma demonstração matemática, mas a conta do quadro mostra apenas que os números fecham: com os próprios números do vereador, os votos a mais de Lula e de Flávio somam exatamente os votos dos eliminados mais a queda de brancos, nulos e abstenções. A impossibilidade vem de duas escolhas do autor, e não da aritmética: tratar diferenças líquidas como grupos inteiros de pessoas e supor que, fora o que ele atribui a Lula, todos os eleitores repetiram o que fizeram no 1º turno.",
      "No fim, o argumento se apoia em descrença: “Você acha factível isso? Eu não engulo essa.” Achar um resultado improvável não demonstra que ele é falso. Para isso seria preciso mostrar que nenhuma distribuição de votos compatível com os dados é plausível, e as estimativas feitas a partir das seções encontram distribuições compatíveis com os totais oficiais sem troca relevante entre Lula e Flávio.",
      "A diferença de 62 mil votos que o vídeo atribui ao TSE vem dos arredondamentos feitos no próprio quadro.",
    ],
    falacias: [
      { nome: "Equívoco", original: "Equivocation", n: 31, categoria: "Falácias de ambiguidade",
        uso: "Chama de brancos e nulos “convertidos” e de “abstenções” as diferenças líquidas entre os turnos (870 mil, 952 mil e 3 milhões) e depois as trata como grupos inteiros de pessoas: “100% dos brancos, 100% dos nulos”. Os grupos de pessoas eram de 5,98 milhões (brancos e nulos) e 33,47 milhões (abstenções)." },
      { nome: "Falso dilema", original: "False Dilemma", n: 1, categoria: "Falácias de distração",
        uso: "Afirma que “só existe um caminho” para Lula chegar a 64 milhões de votos, quando a aritmética admite muitas distribuições diferentes, inclusive com troca zero entre Lula e Flávio." },
      { nome: "Apelo à ignorância", original: "Argument From Ignorance", n: 2, categoria: "Falácias de distração",
        uso: "Conclui que o resultado não é verdadeiro porque o autor não vê como ele poderia ter acontecido (“Você acha factível isso? Eu não engulo essa”). Não saber explicar um resultado não demonstra que ele não ocorreu." },
      { nome: "Apelo à popularidade", original: "Appeal to Popularity", n: 9, categoria: "Apelos a motivos em vez de razões",
        uso: "Estabelece a premissa pedindo a concordância de quem assiste (“Você acredita...? Eu não acredito. Concorda comigo?”), e não com dados." },
    ],
    respostas: [],
  },
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
const INV_HORARIO = [ // minutos depois das 17h (Brasília), seções, votos de Lula, votos de Flávio
  ["0–1", 125624, 15001166, 15608268], ["1–2", 154492, 19373920, 18501023], ["2–5", 160346, 21254140, 18982974],
  ["5–10", 44053, 6369063, 5001529], ["10–15", 4288, 657873, 451156], ["15–30", 1482, 220460, 158099],
  ["30–60", 526, 79455, 55759], ["60–100", 329, 48186, 36177], ["100–130", 6662, 1037169, 848770], ["130 ou mais", 95, 14646, 10789]];
const INV_GRUPOS_17H = [ // grupos de seções do Brasil: seções, votos de Lula, votos de Flávio
  { rot: "AC, AM, MS, MT, RO e RR", sub: "fecharam às 15h ou 16h locais", n: 32026, lula: 2990337, flavio: 4433850, dossie: "“até 17h”" },
  { rot: "Demais estados, no 1º minuto", sub: "fecharam entre 17h00 e 17h01", n: 118716, lula: 14374258, flavio: 14679213, dossie: "“até 17h”" },
  { rot: "Demais seções", sub: "fecharam depois de 17h01", n: 347155, lula: 46691483, flavio: 40541481, dossie: "“depois das 17h”" },
];
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
/* % de Lula nos votos válidos acumulados (BWeb do 2º turno, 499.205 seções) quando 0,5%, 1,5%, ..., 98,5% e 100% das
   seções foram somadas, em cada ordem de soma; os sorteios usam numpy default_rng(2026) */
const INV_ORDENS_X = Array.from({ length: 99 }, (_, i) => i + .5).concat(100);
const INV_ORDENS = {
  encerramento: [45.9, 45.97, 46.21, 46.46, 46.73, 46.91, 47.18, 47.34, 47.52, 47.66, 47.79, 47.9, 48.01, 48.11, 48.22, 48.34, 48.4, 48.5, 48.57, 48.65, 48.73, 48.79, 48.85, 48.91, 48.97, 49.02, 49.07, 49.1, 49.16, 49.21, 49.27, 49.34, 49.4, 49.45, 49.48, 49.53, 49.58, 49.61, 49.65, 49.69, 49.73, 49.75, 49.78, 49.81, 49.85, 49.88, 49.91, 49.94, 49.98, 50.01, 50.04, 50.07, 50.1, 50.12, 50.16, 50.18, 50.21, 50.24, 50.28, 50.31, 50.33, 50.35, 50.38, 50.4, 50.43, 50.46, 50.49, 50.51, 50.54, 50.57, 50.59, 50.62, 50.65, 50.67, 50.7, 50.73, 50.76, 50.79, 50.82, 50.85, 50.89, 50.92, 50.95, 50.98, 51.02, 51.05, 51.09, 51.13, 51.18, 51.22, 51.27, 51.31, 51.36, 51.41, 51.46, 51.52, 51.58, 51.65, 51.72, 51.79],
  estados: [38.09, 53.17, 55.62, 54.83, 56.76, 59.58, 61.07, 62.08, 63.34, 64.58, 65.54, 65.75, 66.09, 65.7, 66.23, 66.53, 65.6, 64.4, 63.38, 62.25, 61.3, 60.23, 59.74, 60.17, 60.51, 60.77, 60.67, 60.26, 59.92, 59.65, 59.32, 59.04, 58.85, 58.5, 58.32, 58.11, 57.85, 57.4, 56.83, 56.36, 56.34, 56.35, 56.35, 56.23, 56.47, 56.65, 57.1, 57.37, 57.64, 57.81, 58.1, 58.41, 58.38, 57.99, 57.59, 57.21, 56.85, 56.5, 56.27, 56.05, 55.91, 55.71, 55.53, 55.46, 55.43, 55.45, 55.58, 55.36, 55.1, 54.86, 54.59, 54.53, 54.44, 54.23, 53.88, 53.57, 53.23, 53.2, 53.26, 53.1, 52.95, 52.84, 52.8, 52.73, 52.63, 52.47, 52.33, 52.23, 52.07, 51.94, 51.89, 51.79, 51.8, 51.77, 51.79, 51.89, 51.98, 51.94, 51.85, 51.79],
  sorteios: [
    [51.5, 51.62, 51.51, 51.47, 51.48, 51.44, 51.51, 51.6, 51.64, 51.62, 51.59, 51.58, 51.63, 51.62, 51.62, 51.61, 51.63, 51.65, 51.65, 51.69, 51.68, 51.7, 51.73, 51.74, 51.75, 51.74, 51.74, 51.74, 51.74, 51.75, 51.74, 51.75, 51.75, 51.76, 51.74, 51.73, 51.74, 51.73, 51.74, 51.74, 51.75, 51.75, 51.75, 51.74, 51.75, 51.76, 51.76, 51.76, 51.76, 51.75, 51.75, 51.75, 51.74, 51.74, 51.74, 51.73, 51.73, 51.73, 51.73, 51.74, 51.75, 51.75, 51.76, 51.76, 51.76, 51.76, 51.76, 51.76, 51.76, 51.76, 51.76, 51.76, 51.76, 51.76, 51.76, 51.76, 51.76, 51.76, 51.76, 51.76, 51.77, 51.77, 51.77, 51.77, 51.77, 51.77, 51.77, 51.78, 51.78, 51.78, 51.78, 51.79, 51.78, 51.79, 51.79, 51.79, 51.79, 51.78, 51.78, 51.79],
    [51.92, 51.81, 51.97, 51.85, 51.77, 51.74, 51.72, 51.74, 51.7, 51.73, 51.77, 51.78, 51.8, 51.8, 51.82, 51.82, 51.79, 51.79, 51.81, 51.78, 51.77, 51.77, 51.77, 51.77, 51.78, 51.78, 51.77, 51.79, 51.77, 51.77, 51.77, 51.78, 51.78, 51.79, 51.8, 51.81, 51.8, 51.8, 51.79, 51.79, 51.79, 51.78, 51.78, 51.77, 51.78, 51.79, 51.79, 51.79, 51.79, 51.8, 51.8, 51.79, 51.79, 51.79, 51.79, 51.79, 51.79, 51.79, 51.78, 51.77, 51.77, 51.77, 51.77, 51.77, 51.77, 51.77, 51.77, 51.77, 51.77, 51.77, 51.78, 51.78, 51.78, 51.79, 51.79, 51.79, 51.79, 51.79, 51.8, 51.79, 51.79, 51.79, 51.78, 51.78, 51.78, 51.78, 51.78, 51.78, 51.78, 51.78, 51.77, 51.78, 51.78, 51.78, 51.77, 51.78, 51.78, 51.78, 51.78, 51.79],
    [51.55, 51.99, 51.92, 51.84, 51.86, 51.89, 51.92, 51.92, 51.89, 51.88, 51.87, 51.84, 51.86, 51.87, 51.84, 51.82, 51.84, 51.82, 51.81, 51.8, 51.79, 51.8, 51.8, 51.8, 51.82, 51.82, 51.82, 51.82, 51.81, 51.81, 51.79, 51.8, 51.79, 51.78, 51.79, 51.79, 51.78, 51.77, 51.77, 51.75, 51.76, 51.76, 51.76, 51.76, 51.75, 51.76, 51.76, 51.76, 51.77, 51.77, 51.77, 51.77, 51.77, 51.77, 51.77, 51.77, 51.77, 51.77, 51.77, 51.77, 51.78, 51.78, 51.78, 51.79, 51.79, 51.8, 51.8, 51.79, 51.79, 51.79, 51.79, 51.78, 51.78, 51.78, 51.78, 51.78, 51.78, 51.78, 51.78, 51.78, 51.78, 51.78, 51.78, 51.78, 51.78, 51.78, 51.78, 51.78, 51.78, 51.78, 51.78, 51.78, 51.78, 51.78, 51.78, 51.78, 51.78, 51.79, 51.79, 51.79],
  ],
};
/* variação dos votos de Flávio do 1º para o 2º turno, por município (votacao_secao, 5.571 municípios) */
const INV_FLAVIO_MUN = [["menos de −5%", 314], ["−5% a −2%", 335], ["−2% a 0%", 289], ["0% a 2%", 435], ["2% a 5%", 997],
  ["5% a 8%", 1694], ["8% a 12%", 1199], ["12% ou mais", 308]];
/* % de Bolsonaro nos votos válidos acumulados (seções de 2022, 2º turno) com as 2.637 zonas eleitorais somadas em ordem
   sorteada (numpy default_rng(34), o sorteio de amplitude mais próxima da mediana entre 100), cada zona com todas as suas seções
   em sequência; de 70.000 a 80.000 seções somadas, a cada 20 seções. Zonas: início, fim, UF, zona, seções, % de Bolsonaro, variação */
const INV_ZONAS_Y = [48.846, 48.846, 48.846, 48.847, 48.848, 48.847, 48.846, 48.842, 48.841, 48.839, 48.838, 48.838, 48.837, 48.836, 48.833, 48.833, 48.831, 48.831, 48.832, 48.833, 48.835, 48.836, 48.839, 48.843, 48.848, 48.855, 48.859, 48.863, 48.867, 48.864, 48.862, 48.859, 48.856, 48.854, 48.85, 48.845, 48.841, 48.836, 48.834, 48.831, 48.825, 48.821, 48.816, 48.811, 48.806, 48.801, 48.797, 48.799, 48.804, 48.809, 48.813, 48.817, 48.819, 48.822, 48.823, 48.824, 48.824, 48.826, 48.824, 48.825, 48.829, 48.834, 48.841, 48.847, 48.853, 48.857, 48.86, 48.864, 48.866, 48.866, 48.868, 48.868, 48.869, 48.869, 48.87, 48.871, 48.871, 48.869, 48.865, 48.863, 48.861, 48.858, 48.856, 48.853, 48.85, 48.847, 48.843, 48.84, 48.838, 48.834, 48.832, 48.826, 48.82, 48.812, 48.804, 48.798, 48.791, 48.784, 48.775, 48.767, 48.761, 48.755, 48.749, 48.742, 48.736, 48.729, 48.728, 48.727, 48.727, 48.726, 48.725, 48.725, 48.724, 48.723, 48.721, 48.72, 48.716, 48.711, 48.709, 48.706, 48.705, 48.702, 48.697, 48.693, 48.689, 48.683, 48.677, 48.67, 48.665, 48.659, 48.654, 48.65, 48.646, 48.651, 48.653, 48.658, 48.663, 48.669, 48.673, 48.676, 48.678, 48.681, 48.684, 48.687, 48.697, 48.707, 48.718, 48.728, 48.74, 48.75, 48.752, 48.753, 48.755, 48.755, 48.757, 48.758, 48.758, 48.759, 48.76, 48.761, 48.76, 48.76, 48.76, 48.759, 48.756, 48.749, 48.745, 48.741, 48.735, 48.729, 48.723, 48.717, 48.712, 48.707, 48.702, 48.697, 48.691, 48.686, 48.685, 48.685, 48.685, 48.685, 48.685, 48.685, 48.687, 48.693, 48.698, 48.702, 48.705, 48.706, 48.708, 48.71, 48.712, 48.714, 48.717, 48.719, 48.72, 48.723, 48.725, 48.726, 48.722, 48.717, 48.71, 48.703, 48.697, 48.692, 48.687, 48.683, 48.679, 48.676, 48.673, 48.673, 48.675, 48.676, 48.678, 48.68, 48.682, 48.684, 48.687, 48.689, 48.691, 48.694, 48.697, 48.7, 48.703, 48.706, 48.702, 48.697, 48.693, 48.689, 48.685, 48.681, 48.672, 48.665, 48.66, 48.654, 48.646, 48.64, 48.633, 48.627, 48.619, 48.612, 48.606, 48.607, 48.614, 48.619, 48.623, 48.626, 48.629, 48.63, 48.631, 48.632, 48.633, 48.634, 48.635, 48.635, 48.636, 48.637, 48.637, 48.638, 48.639, 48.639, 48.64, 48.641, 48.64, 48.632, 48.627, 48.624, 48.619, 48.613, 48.606, 48.6, 48.594, 48.589, 48.584, 48.589, 48.596, 48.599, 48.605, 48.612, 48.618, 48.623, 48.629, 48.635, 48.639, 48.642, 48.646, 48.65, 48.652, 48.656, 48.662, 48.669, 48.677, 48.679, 48.681, 48.683, 48.685, 48.687, 48.688, 48.69, 48.691, 48.693, 48.696, 48.696, 48.698, 48.7, 48.7, 48.703, 48.705, 48.706, 48.706, 48.706, 48.705, 48.699, 48.692, 48.685, 48.677, 48.67, 48.663, 48.66, 48.661, 48.663, 48.664, 48.665, 48.666, 48.666, 48.663, 48.659, 48.656, 48.65, 48.644, 48.638, 48.637, 48.638, 48.64, 48.642, 48.645, 48.647, 48.649, 48.652, 48.656, 48.658, 48.661, 48.663, 48.668, 48.673, 48.678, 48.682, 48.686, 48.691, 48.697, 48.703, 48.71, 48.715, 48.72, 48.725, 48.73, 48.734, 48.728, 48.723, 48.716, 48.709, 48.702, 48.695, 48.687, 48.681, 48.675, 48.669, 48.664, 48.659, 48.652, 48.648, 48.647, 48.646, 48.645, 48.643, 48.642, 48.64, 48.639, 48.638, 48.637, 48.636, 48.635, 48.633, 48.632, 48.631, 48.63, 48.629, 48.628, 48.626, 48.624, 48.623, 48.622, 48.62, 48.618, 48.615, 48.615, 48.612, 48.61, 48.606, 48.604, 48.603, 48.602, 48.603, 48.605, 48.607, 48.608, 48.61, 48.612, 48.61, 48.608, 48.604, 48.6, 48.597, 48.594, 48.591, 48.588, 48.585, 48.582, 48.58, 48.577, 48.575, 48.571, 48.568, 48.566, 48.567, 48.57, 48.57, 48.567, 48.564, 48.56, 48.556, 48.554, 48.551, 48.549, 48.546, 48.543, 48.541, 48.541, 48.541, 48.541, 48.541, 48.542, 48.543, 48.545, 48.546, 48.547, 48.55, 48.553, 48.556, 48.558, 48.558, 48.558, 48.558, 48.559, 48.56, 48.561, 48.561, 48.562, 48.561, 48.557, 48.552, 48.547, 48.543, 48.539, 48.533, 48.527, 48.519, 48.514, 48.506, 48.5, 48.495, 48.49, 48.488, 48.487, 48.482, 48.48, 48.479, 48.477, 48.477, 48.478, 48.477, 48.477, 48.477, 48.477, 48.48, 48.481, 48.484, 48.489, 48.494, 48.501, 48.508, 48.513, 48.519, 48.525, 48.528, 48.535, 48.541, 48.545, 48.54, 48.535];
const INV_ZONAS_SEG = [[69989, 70282, "MG", 132, 293, 45.7, -0.013], [70282, 70423, "RS", 53, 141, 50.8, 0.003], [70423, 70558, "SC", 45, 135, 63.9, 0.032], [70558, 70724, "AL", 10, 166, 36.1, -0.027], [70724, 70922, "MG", 101, 198, 30.1, -0.044], [70922, 71184, "SP", 306, 262, 56.1, 0.028], [71184, 71292, "SP", 130, 108, 70.2, 0.031], [71292, 71362, "RS", 133, 70, 59.6, 0.01], [71362, 71530, "AL", 55, 168, 51.1, 0.005], [71530, 71810, "CE", 95, 280, 40.4, -0.041], [71810, 71882, "PB", 52, 72, 19.9, -0.027], [71882, 72109, "BA", 59, 227, 19.8, -0.077], [72109, 72283, "SP", 382, 174, 46.2, -0.006], [72283, 72347, "TO", 22, 64, 31.9, -0.011], [72347, 72415, "MG", 3, 68, 39.5, -0.006], [72415, 72640, "CE", 9, 225, 29.1, -0.057], [72640, 72856, "SP", 49, 216, 63.5, 0.039], [72856, 72987, "SC", 32, 131, 82.5, 0.068], [72987, 73152, "ES", 30, 165, 51.9, 0.006], [73152, 73278, "MG", 190, 126, 47.8, -0.001], [73278, 73552, "BA", 171, 274, 31.9, -0.073], [73552, 73675, "MG", 267, 123, 49.2, 0.001], [73675, 73755, "RO", 15, 80, 68.7, 0.019], [73755, 73988, "GO", 40, 233, 54.9, 0.022], [73988, 74125, "BA", 193, 137, 20.1, -0.041], [74125, 74209, "AM", 12, 84, 34.8, -0.013], [74209, 74499, "RJ", 110, 290, 57.3, 0.033], [74499, 74616, "AL", 5, 117, 33.1, -0.023], [74616, 74847, "MA", 18, 231, 20.6, -0.079], [74847, 74951, "SP", 312, 104, 65.6, 0.025], [74951, 75277, "RJ", 162, 326, 51.5, 0.014], [75277, 75483, "PI", 11, 206, 23.4, -0.058], [75483, 75677, "RJ", 147, 194, 68.2, 0.055], [75677, 75841, "RO", 1, 164, 70.5, 0.038], [75841, 76237, "RN", 50, 396, 53.7, 0.029], [76237, 76372, "CE", 18, 135, 12.5, -0.047], [76372, 76494, "PR", 12, 122, 53.5, 0.008], [76494, 76627, "AL", 47, 133, 29.8, -0.031], [76627, 76872, "RJ", 218, 245, 56.1, 0.028], [76872, 77140, "SP", 345, 268, 65.8, 0.069], [77140, 77415, "BA", 71, 275, 22.4, -0.086], [77415, 77880, "SP", 359, 465, 43.8, -0.03], [77880, 77962, "MG", 201, 82, 39.9, -0.008], [77962, 78169, "MG", 218, 207, 49.6, 0.002], [78169, 78486, "PE", 4, 317, 38.5, -0.046], [78486, 78535, "SP", 232, 49, 56.7, 0.005], [78535, 78739, "MG", 244, 204, 33.2, -0.03], [78739, 78926, "MG", 246, 187, 50.9, 0.006], [78926, 79194, "MG", 35, 268, 51.3, 0.012], [79194, 79285, "MG", 120, 91, 24.6, -0.021], [79285, 79404, "MA", 106, 119, 14.6, -0.039], [79404, 79503, "RN", 8, 99, 34.5, -0.017], [79503, 79671, "PR", 38, 168, 45.2, -0.005], [79671, 79774, "GO", 31, 103, 60.1, 0.015], [79774, 79956, "RS", 118, 182, 70.5, 0.054], [79956, 80092, "MA", 49, 136, 25.5, -0.031]];

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

/* para cada grupo, uma barra para Lula e outra para Flávio, a partir de zero */
function invBarrasPares(el, grupos, fmt = invCompacto) {
  const W = larg(el), estreito = W < 520, bh = 16, gap = 4;
  const mE = estreito ? 6 : Math.min(250, W * .38), cab = estreito ? 30 : 0, passo = cab + 2 * bh + gap + 22;
  const H = grupos.length * passo;
  const vmax = d3.max(grupos, g => Math.max(g.lula, g.flavio));
  const x = d3.scaleLinear().domain([0, vmax * (estreito ? 1.32 : 1.25)]).range([mE, W - 8]);
  const svg = d3.select(el).html("").append("svg").attr("viewBox", `0 0 ${W} ${H}`).attr("role", "img");
  grupos.forEach((g, i) => {
    const y = i * passo + cab, dif = g.lula - g.flavio;
    const quem = dif >= 0 ? `Lula +${fmt(dif)}` : `Flávio +${fmt(-dif)}`;
    const dica = `<b>${esc(g.rot)}</b> · ${fInt(g.n)} seções<br>Lula: ${fInt(g.lula)}<br>Flávio: ${fInt(g.flavio)}<br>Diferença: ${quem}`;
    if (estreito) {
      svg.append("text").attr("class", "rot-forte").attr("x", mE).attr("y", y - 17).text(g.rot);
      svg.append("text").attr("class", "rot").attr("x", mE).attr("y", y - 4).text(`${fInt(g.n)} seções · ${g.sub}`);
    } else {
      svg.append("text").attr("class", "rot-forte").attr("x", mE - 10).attr("y", y + 12).attr("text-anchor", "end").text(g.rot);
      svg.append("text").attr("class", "rot").attr("x", mE - 10).attr("y", y + 26).attr("text-anchor", "end").text(`${fInt(g.n)} seções`);
      svg.append("text").attr("class", "rot").attr("x", mE - 10).attr("y", y + 40).attr("text-anchor", "end").text(g.sub);
    }
    [["Lula", g.lula, C.lula, 0], ["Flávio", g.flavio, C.dir, bh + gap]].forEach(([nome, v, cor, dy]) => {
      invDica(svg.append("path").attr("d", invBarra(x(0), y + dy, Math.max(2, x(v) - x(0)), bh, "d")).attr("fill", cor), dica);
      svg.append("text").attr("class", "rot-medio").attr("x", x(v) + 6).attr("y", y + dy + 12).text(`${nome} ${fmt(v)}`);
    });
    svg.append("text").attr("class", "rot-forte").attr("x", x(0)).attr("y", y + 2 * bh + gap + 15).text(`Diferença: ${quem}`);
  });
  svg.append("line").attr("x1", x(0)).attr("x2", x(0)).attr("y1", cab).attr("y2", H - 22).attr("stroke", C.linhaF);
}

/* para cada grupo, barras de 0 a 100% divididas entre Lula, Flávio e o restante;
   grupos: [{rot, sub, barras: [{rot, partes: [lula, flavio, resto]}]}] */
function invBarras100(el, grupos) {
  const W = larg(el), estreito = W < 520, mE = estreito ? 76 : 250, bh = 16, gap = 4, cab = estreito ? 32 : 0;
  const nb = grupos[0].barras.length, passo = cab + nb * bh + (nb - 1) * gap + 20, H = grupos.length * passo + 4;
  const x = d3.scaleLinear().domain([0, 100]).range([mE, W - 8]);
  const cores = [C.lula, C.dir, C.bn], nomes = ["Lula", "Flávio", "Branco, nulo ou não votou"];
  const svg = d3.select(el).html("").append("svg").attr("viewBox", `0 0 ${W} ${H}`).attr("role", "img");
  const dentro = (xx, y, txt, ancora) => svg.append("text").attr("x", xx).attr("y", y + 12).attr("text-anchor", ancora).attr("fill", "#fff")
    .style("font-size", "11px").style("font-family", "var(--f-numero)").style("pointer-events", "none").text(txt);
  grupos.forEach((g, i) => {
    const y0 = i * passo + 4;
    svg.append("text").attr("class", "rot-forte").attr("x", 4).attr("y", y0 + 12).text(g.rot);
    svg.append("text").attr("class", "rot").attr("x", 4).attr("y", y0 + 26).text(g.sub);
    g.barras.forEach((b, j) => {
      const y = y0 + cab + j * (bh + gap);
      svg.append("text").attr("class", "rot").attr("x", mE - 6).attr("y", y + 12).attr("text-anchor", "end").text(b.rot);
      const dica = `<b>${esc(g.rot)}</b> · ${esc(b.rot)}<br>` + b.partes.map((v, k) => `${nomes[k]}: ${invP(v)}`).join("<br>");
      let acum = 0;
      b.partes.forEach((v, k) => {
        if (v <= 0) return;
        const xa = x(acum), xb = x(acum + v), w = Math.max(1, xb - xa - (acum + v < 100 ? 2 : 0));
        const fim = acum === 0 && acum + v >= 100 ? null : acum === 0 ? "e" : acum + v >= 100 ? "d" : null;
        invDica(svg.append("path").attr("d", fim ? invBarra(xa, y, w, bh, fim) : `M${xa},${y}h${w}v${bh}h${-w}Z`).attr("fill", cores[k]), dica);
        if (k < 2 && w > 40) dentro(k === 0 ? xa + 5 : xa + w - 5, y, fNum(v, 0) + "%", k === 0 ? "start" : "end");
        acum += v;
      });
    });
  });
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

/* linhas sobre um eixo horizontal de x0 a x1 (por padrão, 0 a 100%); series: [{nome, cor, valores, fina}]. Ao passar
   o mouse, uma linha vertical mostra o valor de todas as séries naquele ponto. extra(svg, x, y) desenha marcações. */
function invLinhas(el, xs, series, { y0, y1, x0 = 0, x1 = 100, fmtX = t => t + "%", fmtY = t => t + "%", ref, rotX, rotY, fmtDica, extra, H = 280 } = {}) {
  const W = larg(el), mE = 52, mD = 10, mT = rotY ? 26 : 12, mB = 40;
  const x = d3.scaleLinear().domain([x0, x1]).range([mE, W - mD]), y = d3.scaleLinear().domain([y0, y1]).range([H - mB, mT]);
  const svg = d3.select(el).html("").append("svg").attr("viewBox", `0 0 ${W} ${H}`).attr("role", "img");
  svg.append("g").attr("class", "eixo").attr("transform", `translate(${mE},0)`).call(d3.axisLeft(y).ticks(6).tickSize(-(W - mE - mD)).tickFormat(fmtY))
    .call(g => g.select(".domain").remove()).call(g => g.selectAll(".tick line").attr("stroke", C.linha));
  svg.append("g").attr("class", "eixo").attr("transform", `translate(0,${H - mB})`).call(d3.axisBottom(x).ticks(W < 520 ? 4 : 10).tickFormat(fmtX))
    .call(g => g.select(".domain").attr("stroke", C.linhaF));
  if (extra) extra(svg, x, y);
  if (rotY) svg.append("text").attr("class", "rot").attr("x", mE).attr("y", 9).text(rotY);
  if (rotX) svg.append("text").attr("class", "rot").attr("x", W - mD).attr("y", H - 4).attr("text-anchor", "end").text(rotX);
  if (ref) {
    svg.append("line").attr("x1", mE).attr("x2", W - mD).attr("y1", y(ref.v)).attr("y2", y(ref.v)).attr("stroke", C.tinta2).attr("stroke-dasharray", "4 4");
    svg.append("text").attr("class", "rot").attr("x", W - mD - 4).attr("y", y(ref.v) + 14).attr("text-anchor", "end").text(ref.rot);
  }
  series.forEach(s => svg.append("path").attr("d", d3.line()(xs.map((v, i) => [x(v), y(s.valores[i])]))).attr("fill", "none")
    .attr("stroke", s.cor).attr("stroke-width", s.fina ? 1.5 : 2.5).attr("stroke-linejoin", "round"));
  const guia = svg.append("line").attr("y1", mT).attr("y2", H - mB).attr("stroke", C.linhaF).style("display", "none");
  svg.append("rect").attr("x", mE).attr("y", mT).attr("width", W - mE - mD).attr("height", H - mT - mB).attr("fill", "transparent")
    .on("mousemove", ev => {
      const i = d3.minIndex(xs, v => Math.abs(x(v) - d3.pointer(ev)[0]));
      guia.attr("x1", x(xs[i])).attr("x2", x(xs[i])).style("display", null);
      mostrarDica(fmtDica(i), ev);
    })
    .on("mouseleave", () => { guia.style("display", "none"); esconderDica(); });
}

const INV_FLUXO_GRUPOS = [ // grupo no 1º turno: eleitores e divisão no 2º turno pelo caminho do vídeo (Lula, Flávio, resto)
  { o: "a_1", rot: "Votou em Lula", n: 53879538, video: [100, 0, 0] },
  { o: "b_1", rot: "Votou em Flávio", n: 56104503, video: [0, 100, 0] },
  { o: "o_1", rot: "Votou em outros candidatos", n: 9316747, video: [60.1, 39.9, 0] },
  { o: "bn_1", rot: "Votou em branco ou nulo", n: 5975047, video: [30.5, 0, 69.5] },
  { o: "abst_1", rot: "Não votou", n: 33469667, video: [8.8, 0, 91.2] },
];
/* estimativa do painel (Modelo A, seções, 2026), lida de dados.js */
function invFluxoModelo(o) {
  const t = c => 100 * D.matrizes.find(m => m.ano === 2026 && m.nivel === "secao" && m.origens === "base" && m.origem === o && m.destino === c).taxa;
  const l = t("a_2"), f = t("b_2");
  return [l, f, 100 - l - f];
}

const INV_GRAFICOS = {
  silvajardim_conta: {
    titulo: "Silva Jardim: de onde vêm os 985 votos que Lula e Flávio ganharam juntos",
    como: "As três primeiras barras mostram de onde podem vir votos novos para os finalistas no 2º turno: os votos dados no 1º turno aos candidatos eliminados, a diminuição de brancos e nulos e, com sinal negativo, a diminuição do número de eleitores que votaram. A soma das três (quarta barra) é igual ao que Lula e Flávio ganharam juntos (duas últimas barras). A conta fecha sem que nenhum eleitor precise ter trocado Flávio por Lula. São saldos entre os turnos: não dizem quantas pessoas fizeram cada movimento.",
    tabela: () => ({ cab: ["Parcela", "1º turno", "2º turno", "Diferença"], linhas: [
      ["Votos dos candidatos eliminados", "897", "—", "+897"], ["Brancos e nulos", "630", "438", "+192 (queda)"],
      ["Eleitores que votaram", "14.909", "14.805", "−104"], ["Soma das três parcelas", "", "", "985"],
      ["Lula", "4.450", "5.434", "+984"], ["Flávio", "8.932", "8.933", "+1"]] }),
    desenhar: el => invBarrasH(el, [
      { rot: "Votos dos eliminados", sub: "no 1º turno", v: 897, cor: C.outros, txt: "+897" },
      { rot: "Queda de brancos e nulos", sub: "de 630 para 438", v: 192, cor: C.bn, txt: "+192" },
      { rot: "Eleitores a menos", sub: "de 14.909 para 14.805", v: -104, cor: C.abst, txt: "−104" },
      { rot: "Soma", sub: "897 + 192 − 104", v: 985, cor: C.tinta2, txt: "985" },
      { rot: "Votos a mais de Lula", sub: "de 4.450 para 5.434", v: 984, cor: C.lula, txt: "+984" },
      { rot: "Votos a mais de Flávio", sub: "de 8.932 para 8.933", v: 1, cor: C.dir, txt: "+1" },
    ]),
  },
  silvajardim_municipios: {
    titulo: "Variação dos votos de Flávio do 1º para o 2º turno nos 5.571 municípios",
    como: "Cada coluna conta os municípios em que os votos de Flávio variaram na faixa indicada. Em 938 municípios Flávio teve menos votos no 2º turno do que no 1º (as três primeiras colunas). Silva Jardim, com 0,01% a mais, está na faixa de 0% a 2%, junto com outros 434 municípios.",
    tabela: () => ({ cab: ["Variação dos votos de Flávio", "Municípios"], linhas: INV_FLAVIO_MUN.map(([f, n]) => [f, fInt(n)]) }),
    desenhar: el => invColunas(el, INV_FLAVIO_MUN.map(f => f[0]), [{ nome: "Municípios", cor: C.dir, valores: INV_FLAVIO_MUN.map(f => f[1]) }],
      { y1: 1800, fmt: fInt, rotY: "municípios", rotular: () => true, dicaCat: c => `Votos de Flávio: ${c}` }),
  },
  professor_ordens: {
    titulo: "Os mesmos votos de 2026 somados em ordens diferentes",
    como: "Cada linha mostra a porcentagem de Lula nos votos válidos somados até aquele ponto, à medida que as seções são incluídas. O eixo horizontal é a porcentagem das seções já somadas. Os votos de cada seção são os oficiais em todas as linhas; só muda a ordem da soma. Na ordem em que as seções encerraram a votação, Lula começa atrás e sobe quase em linha reta; na ordem dos estados, a curva sobe e depois desce; nas ordens sorteadas, fica em 51,8% quase desde o início. Todas terminam em 51,79%. A linha tracejada marca 50%.",
    legenda: () => [[C.roxo, "Ordem de encerramento das seções"], [C.outros, "Ordem dos estados (AC, AL, AM...)"], [C.tinta3, "Três ordens sorteadas"]],
    tabela: () => ({ cab: ["Seções somadas", "Ordem de encerramento", "Ordem dos estados", "Sorteio 1", "Sorteio 2", "Sorteio 3"],
      linhas: INV_ORDENS_X.map((x, i) => [x, i]).filter(([x]) => x % 10 === .5 || x === 100).map(([x, i]) =>
        [invP(x), invP(INV_ORDENS.encerramento[i], 2), invP(INV_ORDENS.estados[i], 2), ...INV_ORDENS.sorteios.map(s => invP(s[i], 2))]) }),
    desenhar: el => invLinhas(el, INV_ORDENS_X, [
      ...INV_ORDENS.sorteios.map((v, k) => ({ nome: `Sorteio ${k + 1}`, cor: C.tinta3, valores: v, fina: true })),
      { nome: "Ordem dos estados", cor: C.outros, valores: INV_ORDENS.estados },
      { nome: "Ordem de encerramento", cor: C.roxo, valores: INV_ORDENS.encerramento }],
      { y0: 36, y1: 68, ref: { v: 50, rot: "50%" }, rotY: "Lula (% dos válidos já somados)", rotX: "seções já somadas →",
        fmtDica: i => `<b>${invP(INV_ORDENS_X[i])} das seções somadas</b><br>Lula na ordem de encerramento: ${invP(INV_ORDENS.encerramento[i], 2)}<br>` +
          `Na ordem dos estados: ${invP(INV_ORDENS.estados[i], 2)}<br>Nos sorteios: ${INV_ORDENS.sorteios.map(s => invP(s[i], 2)).join(" · ")}` }),
  },
  professor_zonas: {
    titulo: "Subidas e quedas sem nenhum voto alterado: seções de 2022 somadas por zona eleitoral",
    como: "A linha é a porcentagem de Bolsonaro nos votos válidos somados até cada ponto, com as seções de 2022 somadas zona eleitoral por zona eleitoral, em ordem sorteada. Cada zona entra inteira, com todas as suas seções em sequência, como acontece quando uma região apura e transmite junto. O trecho vai de 70 mil a 80 mil seções somadas, com o eixo vertical ampliado como no vídeo. A faixa de baixo mostra cada zona que entrou: vermelha se Lula teve mais votos nela, azul se Bolsonaro teve. As quedas maiores coincidem com zonas vermelhas e as subidas maiores com zonas azuis. A linha tracejada marca a zona 345 de São Paulo, que levanta a curva 0,07 ponto, seguida da zona 71 da Bahia, que a derruba 0,09.",
    legenda: () => [[C.dir, "Linha: % de Bolsonaro somada até o ponto"], [C.lula, "Faixa: zona onde Lula teve mais votos"], [C.dir, "Faixa: zona onde Bolsonaro teve mais votos"]],
    tabela: () => ({ cab: ["Seções somadas", "Zona", "Seções da zona", "Bolsonaro na zona", "Variação da curva (ponto)"],
      linhas: INV_ZONAS_SEG.map(([a, b, uf, z, n, p, dv]) => [`${fInt(a + 1)} a ${fInt(b)}`, `${z} (${uf})`, fInt(n), invP(p), fSin(dv, 3)]) }),
    desenhar: el => {
      const xs = INV_ZONAS_Y.map((_, i) => 70000 + 20 * i), estreito = larg(el) < 520;
      invLinhas(el, xs, [{ nome: "Bolsonaro", cor: C.dir, valores: INV_ZONAS_Y }], {
        x0: 70000, x1: 80000, y0: 48.3, y1: 49, fmtX: t => fNum(t / 1000, 0) + " mil", fmtY: t => fNum(t, 1) + "%",
        rotY: "Bolsonaro (% dos válidos já somados)", rotX: "seções já somadas →",
        extra: (svg, x, y) => {
          const yb = y(48.3) - 12;
          INV_ZONAS_SEG.forEach(([a, b, , , , p]) => {
            const xa = x(Math.max(a, 70000)), xb = x(Math.min(b, 80000));
            svg.append("rect").attr("x", xa).attr("y", yb).attr("width", Math.max(1, xb - xa - 1)).attr("height", 8).attr("fill", p < 50 ? C.lula : C.dir);
          });
          const xm = x(77140);
          svg.append("line").attr("x1", xm).attr("x2", xm).attr("y1", y(49)).attr("y2", yb - 2).attr("stroke", C.tinta2).attr("stroke-dasharray", "3 3");
          [estreito ? "SP 345: +0,07" : "zona 345 de SP: +0,07 ponto (268 seções)", estreito ? "BA 71: −0,09" : "em seguida, zona 71 da BA: −0,09 ponto (275 seções)"]
            .forEach((t, k) => svg.append("text").attr("class", "rot").attr("x", xm - 6).attr("y", y(49) + 12 + 14 * k).attr("text-anchor", "end").text(t));
        },
        fmtDica: i => {
          const s = xs[i], z = INV_ZONAS_SEG.find(r => s > r[0] && s <= r[1]);
          return `<b>${fInt(s)} seções somadas</b><br>Bolsonaro: ${invP(INV_ZONAS_Y[i], 3)}` +
            (z ? `<br>Entrando: zona ${z[3]} de ${z[2]} (${fInt(z[4])} seções, Bolsonaro ${invP(z[5])})` : "");
        },
      });
    },
  },
  ranieri_fluxos: {
    titulo: "Para onde foi cada grupo de eleitores do 1º turno: o caminho do vídeo e a estimativa do projeto",
    como: "Cada grupo de eleitores do 1º turno tem duas barras, que mostram como ele votou no 2º: vermelho, em Lula; azul, em Flávio; cinza, em branco, nulo ou não votou. A barra de cima é o caminho do vídeo, refeito com os números oficiais; a de baixo, a estimativa deste projeto a partir das 499 mil seções (aba “Para onde foram os votos”). Nas duas, praticamente nenhum eleitor de Flávio vai para Lula. Os “100% dos brancos e nulos” do vídeo aparecem como 30% das pessoas que votaram em branco ou nulo, e os “100% das abstenções”, como 9% de quem não votou.",
    legenda: () => [[C.lula, "Lula"], [C.dir, "Flávio"], [C.bn, "Branco, nulo ou não votou"]],
    tabela: () => ({ cab: ["Grupo no 1º turno", "Eleitores", "Caminho", "Lula", "Flávio", "Branco, nulo ou não votou"],
      linhas: INV_FLUXO_GRUPOS.flatMap(g => [["vídeo", g.video], ["estimativa", invFluxoModelo(g.o)]].map(([c, v], j) =>
        [j ? "" : g.rot, j ? "" : fInt(g.n), c, invP(v[0]), invP(v[1]), invP(v[2])])) }),
    desenhar: el => invBarras100(el, INV_FLUXO_GRUPOS.map(g => ({ rot: g.rot, sub: invCompacto(g.n) + " de eleitores",
      barras: [{ rot: "vídeo", partes: g.video }, { rot: "estimativa", partes: invFluxoModelo(g.o) }] }))),
  },
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
    titulo: "Votos de Lula e de Flávio pela hora em que a seção fechou",
    como: "As seções foram agrupadas pelo tempo que levaram para fechar depois das 17h, já no horário de Brasília. Em cada faixa, a coluna vermelha soma os votos de Lula nessas seções, e a azul, os de Flávio. Nenhuma seção fechou antes das 17h: a mais rápida fechou 9 segundos depois, e a maioria fechou nos primeiros 5 minutos, depois de atender quem estava na fila. Na primeira faixa Flávio tem mais votos porque é nela que estão as seções dos estados com fuso diferente de Brasília (gráfico seguinte). Perto de 120 minutos estão as seções que ficaram abertas até as 19h.",
    legenda: () => [[C.lula, "Lula"], [C.dir, "Flávio"]],
    tabela: () => ({ cab: ["Minutos depois das 17h", "Seções", "Votos de Lula", "Votos de Flávio"],
      linhas: INV_HORARIO.map(([f, n, l, b]) => [f, fInt(n), fInt(l), fInt(b)]) }),
    desenhar: el => invColunas(el, INV_HORARIO.map(h => h[0]), [
      { nome: "Lula", cor: C.lula, valores: INV_HORARIO.map(h => h[2]) }, { nome: "Flávio", cor: C.dir, valores: INV_HORARIO.map(h => h[3]) }],
      { y1: 24e6, fmt: invCompacto, fmtEixo: v => v ? fNum(v / 1e6, 0) + " mi" : "0", rotY: "votos", dicaCat: c => `Seções que fecharam ${c} minutos depois das 17h` }),
  },
  fuso: {
    titulo: "As três partes da divisão “até 17h / depois das 17h”",
    como: "O dossiê dividiu as seções pela hora local gravada no boletim. Separadas em três grupos, fica visível de onde vem cada número dele. As seções dos estados com fuso diferente de Brasília fecham às 15h ou 16h locais, que são 17h em Brasília, e dão a Flávio 1,44 milhão de votos a mais. As dos demais estados que fecharam no primeiro minuto ficam quase empatadas. As que fecharam depois do primeiro minuto, a maior parte do país, dão a Lula 6,15 milhões a mais. Os dois primeiros grupos formam as “urnas encerradas até as 17h” do dossiê; o terceiro, as “encerradas depois”.",
    legenda: () => [[C.lula, "Lula"], [C.dir, "Flávio"]],
    tabela: () => ({ cab: ["Grupo de seções", "No dossiê", "Seções", "Votos de Lula", "Votos de Flávio", "Diferença"],
      linhas: INV_GRUPOS_17H.map(g => [g.rot, g.dossie, fInt(g.n), fInt(g.lula), fInt(g.flavio), (g.lula >= g.flavio ? "Lula +" : "Flávio +") + fInt(Math.abs(g.lula - g.flavio))]) }),
    desenhar: el => invBarrasPares(el, INV_GRUPOS_17H),
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
    como: "Para cada estado há duas barras com a divisão dos votos válidos entre Lula (vermelho) e Flávio (azul): a de cima é das seções que ficaram abertas até perto das 19h; a de baixo, das outras seções das mesmas zonas eleitorais, que fecharam no horário normal. Barras parecidas querem dizer que as seções votaram igual às vizinhas. A linha clara no meio marca 50%. “Abertas até perto das 19h” são as seções que fecharam 100 minutos ou mais depois das 17h (horário de Brasília); a contagem difere um pouco da do dossiê, que usa a hora local gravada no boletim.",
    legenda: () => [[C.lula, "Lula"], [C.dir, "Flávio"]],
    tabela: () => ({ cab: ["UF", "Seções abertas até perto das 19h", "Lula no estado", "Lula nessas seções", "Lula nas vizinhas", "Diferença (p.p.)"],
      linhas: INV_VIZINHAS.map(([u, n, e, a, v]) => [u, fInt(n), invP(e), invP(a), invP(v), fSin(a - v, 1)]) }),
    desenhar: el => {
      const W = larg(el), estreito = W < 520, mE = estreito ? 150 : 190, mD = 64, bh = 16, gap = 4, passo = 2 * bh + gap + 18;
      const H = INV_VIZINHAS.length * passo + 14;
      const x = d3.scaleLinear().domain([0, 100]).range([mE, W - mD]);
      const svg = d3.select(el).html("").append("svg").attr("viewBox", `0 0 ${W} ${H}`).attr("role", "img");
      svg.append("text").attr("class", "rot").attr("x", W - 8).attr("y", 10).attr("text-anchor", "end").text("Lula: dif.");
      const dentro = (xx, y, txt, ancora) => svg.append("text").attr("x", xx).attr("y", y + 12).attr("text-anchor", ancora).attr("fill", "#fff")
        .style("font-size", "11px").style("font-family", "var(--f-numero)").style("pointer-events", "none").text(txt);
      INV_VIZINHAS.forEach(([u, n, e, a, v], i) => {
        const y = i * passo + 18;
        const dica = `<b>${u}</b> · ${fInt(n)} seç${n === 1 ? "ão" : "ões"} abertas até perto das 19h<br>Nessas seções: Lula ${invP(a)}, Flávio ${invP(100 - a)}<br>Vizinhas da mesma zona: Lula ${invP(v)}, Flávio ${invP(100 - v)}<br>Estado: Lula ${invP(e)}`;
        svg.append("text").attr("class", "rot-forte").attr("x", 4).attr("y", y + 12).text(u);
        svg.append("text").attr("class", "rot").attr("x", 4).attr("y", y + 2 * bh + gap - 2).text(`${fInt(n)} seç${n === 1 ? "ão" : "ões"}`);
        [[a, estreito ? "abertas" : "abertas até 19h", 0], [v, "vizinhas", bh + gap]].forEach(([pl, rot, dy]) => {
          const yy = y + dy, xm = x(pl);
          svg.append("text").attr("class", "rot").attr("x", mE - 6).attr("y", yy + 12).attr("text-anchor", "end").text(rot);
          invDica(svg.append("path").attr("d", invBarra(x(0), yy, xm - x(0) - 1, bh, "e")).attr("fill", C.lula), dica);
          invDica(svg.append("path").attr("d", invBarra(xm + 1, yy, x(100) - xm - 1, bh, "d")).attr("fill", C.dir), dica);
          if (xm - x(0) > 34) dentro(x(0) + 5, yy, fNum(pl, 0) + "%", "start");
          if (x(100) - xm > 34) dentro(x(100) - 5, yy, fNum(100 - pl, 0) + "%", "end");
        });
        svg.append("text").attr("class", "rot-medio").attr("x", W - 8).attr("y", y + bh + 6).attr("text-anchor", "end").text(`${fSin(a - v, 1)} p.p.`);
      });
      svg.append("line").attr("x1", x(50)).attr("x2", x(50)).attr("y1", 12).attr("y2", H - 6).attr("stroke", C.papel).attr("stroke-width", 2);
    },
  },
  biometria: {
    titulo: "Liberação por código e votação de Lula e Flávio, por estado",
    como: "Cada ponto é um estado. Para a direita, mais eleitores liberados por código (digital não reconhecida); para cima, mais votos em Lula. Pontos vermelhos são estados onde Lula venceu; azuis, onde Flávio venceu. Se a liberação favorecesse Lula, os pontos subiriam da esquerda para a direita e os vermelhos se concentrariam à direita. RS e SC, onde Flávio venceu, estão entre os que mais liberaram. Em telas estreitas, só alguns estados têm nome; os demais aparecem ao passar o mouse e na tabela.",
    legenda: () => [[C.lula, "Estado onde Lula venceu", "border-radius:50%"], [C.dir, "Estado onde Flávio venceu", "border-radius:50%"]],
    tabela: () => ({ cab: ["UF", "Liberados por código (% do comparecimento)", "Lula (% dos válidos)", "Flávio (% dos válidos)"],
      linhas: Object.entries(INV_BIOMETRIA_UF).sort((p, q) => q[1][0] - p[1][0]).map(([u, [l, v]]) => [u, invP(l, 2), invP(v), invP(100 - v)]) }),
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
        invDica(svg.append("circle").attr("cx", x(l)).attr("cy", y(v)).attr("r", 5).attr("fill", v > 50 ? C.lula : C.dir).attr("stroke", C.papel).attr("stroke-width", 2),
          `<b>${u}</b><br>Liberados por código: ${invP(l, 2)}<br>Lula: ${invP(v)} · Flávio: ${invP(100 - v)}`);
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
