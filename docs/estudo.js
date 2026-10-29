/* Aba Resumo — explicação para estudantes do ensino fundamental.
   Carregado antes de app.js. As funções esMontar() e esVista() são chamadas por
   renderizar.resumo (app.js) e usam o que app.js define (D, $, fNum, fInt, segmentado).
   Todos os números vêm de window.DADOS (contas oficiais do TSE); as frases sobre o que
   não é possível saber seguem AUDITORIA_METODOLOGICA.md. As cores vêm das variáveis CSS,
   então o tema escuro não exige redesenhar. */
"use strict";

const ES = { passo: 0, grupo: null, elim: 50, troca: 0, resp: {} };
const ES_GRUPOS = [
  ["lula", "Lula"], ["flavio", "Flávio Bolsonaro"], ["elim", "Candidatos eliminados"],
  ["bn", "Votou em branco ou nulo"], ["abst", "Não foi votar"],
];
const ES_PASSOS = ["Quem votou", "A conta de Lula", "Votos a mais", "Duas histórias", "O que sabemos", "Teste rápido"];

/* "1,1 milhão", "10,4 milhões" */
function esMi(n, d = 1) {
  const v = Math.round(n / 10 ** (6 - d)) / 10 ** d;
  return fNum(v, d) + (Math.abs(v) < 2 ? " milhão" : " milhões");
}
/* arredonda percentuais para 100 bonequinhos sem perder nenhum (maiores restos) */
function esCem(pcts) {
  const base = pcts.map(p => Math.floor(p));
  const falta = 100 - base.reduce((a, b) => a + b, 0);
  pcts.map((p, i) => [p - Math.floor(p), i]).sort((a, b) => b[0] - a[0]).slice(0, falta).forEach(([, i]) => base[i]++);
  return base;
}
function esNumeros() {
  const R = Object.fromEntries(D.reconciliacao.map(r => [r.indicador, r]));
  const L = R["Lula"], F = R["Flávio Bolsonaro"], O = R["Outros candidatos"], V = R["Votos válidos"];
  const BR = R["Votos brancos"], NU = R["Votos nulos (inclui nulos técnicos)"], AB = R["Abstenções (aptos − comparecimento)"];
  const AP = R["Eleitores aptos"];
  return {
    L, F, O, V, BR, NU, AB, AP,
    bn1: BR.primeiro_turno + NU.primeiro_turno, bn2: BR.segundo_turno + NU.segundo_turno,
    t1: esCem([L.pct_aptos_t1, F.pct_aptos_t1, O.pct_aptos_t1, BR.pct_aptos_t1 + NU.pct_aptos_t1, AB.pct_aptos_t1]),
    t2: esCem([L.pct_aptos_t2, F.pct_aptos_t2, O.pct_aptos_t2, BR.pct_aptos_t2 + NU.pct_aptos_t2, AB.pct_aptos_t2]),
  };
}

/* ---------- ilustrações ---------- */
const ES_SIMBOLOS = `<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">
  <symbol id="es-pessoa" viewBox="0 0 24 26"><circle cx="12" cy="6" r="4.6"/><path d="M3.5 25v-5.5a7 7 0 0 1 7-7h3a7 7 0 0 1 7 7V25z"/></symbol>
  <pattern id="es-listra-f" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="6" height="6" class="es-listra-fundo"/><rect width="3" height="6" class="es-listra-f"/></pattern>
</svg>`;

function esUrna() {
  const teclas = [];
  for (let l = 0; l < 4; l++) for (let c = 0; c < 3; c++) {
    if (l === 3 && c !== 1) continue;
    teclas.push(`<rect x="${84 + c * 11}" y="${14 + l * 10}" width="9" height="7.5" rx="1.5" class="es-tecla"/>`);
  }
  return `<svg class="es-urna" viewBox="0 0 130 84" role="img" aria-label="Desenho de uma urna eletrônica">
    <rect x="2" y="4" width="126" height="76" rx="7" class="es-urna-corpo"/>
    <rect x="10" y="12" width="62" height="48" rx="3" class="es-urna-tela"/>
    <text x="41" y="33" text-anchor="middle" class="es-urna-txt">SEU VOTO</text>
    <text x="41" y="48" text-anchor="middle" class="es-urna-txt grande">FIM</text>
    ${teclas.join("")}
    <rect x="80" y="58" width="13" height="9" rx="1.5" fill="#f4f4f2" stroke="#9a9a96" stroke-width=".6"/>
    <rect x="96" y="58" width="13" height="9" rx="1.5" fill="#e8892b"/>
    <rect x="112" y="56" width="13" height="11" rx="1.5" fill="#2e9d4f"/>
    <rect x="10" y="66" width="62" height="6" rx="2" class="es-urna-faixa"/>
  </svg>`;
}

function esGrade(cont, rotulo) {
  let i = 0, s = "";
  ES_GRUPOS.forEach(([g], k) => {
    for (let j = 0; j < cont[k]; j++, i++) {
      s += `<use href="#es-pessoa" x="${(i % 10) * 26 + 1}" y="${Math.floor(i / 10) * 28 + 1}" width="24" height="26" class="es-p es-${g}"/>`;
    }
  });
  const desc = ES_GRUPOS.map(([, nome], k) => `${nome}: ${cont[k]}`).join("; ");
  return `<svg class="es-grade" viewBox="0 0 260 280" role="img" aria-label="${rotulo}. ${desc}.">${s}</svg>`;
}
const esIcone = g => `<svg class="es-ico" viewBox="0 0 24 26" aria-hidden="true"><use href="#es-pessoa" class="es-p es-${g}"/></svg>`;

/* ---------- passos ---------- */
function esPasso1(N) {
  const leg = ES_GRUPOS.map(([g, nome], k) => {
    const d = N.t2[k] - N.t1[k];
    return `<button type="button" class="es-leg" data-g="${g}" aria-pressed="false">${esIcone(g)}<span class="es-leg-nome">${nome}</span>
      <span class="es-leg-num mono">${N.t1[k]} → ${N.t2[k]}</span><span class="es-leg-dif mono">${d > 0 ? "+" : d < 0 ? "−" : ""}${Math.abs(d)}</span></button>`;
  }).join("");
  return `<h3>Se o Brasil tivesse só 100 eleitores</h3>
    <p class="es-lead">Em 2026, <b class="mono">${fInt(N.AP.primeiro_turno)}</b> pessoas podiam votar. Para enxergar melhor, vamos encolher esse número para 100: cada bonequinho abaixo representa cerca de <b>${esMi(N.AP.primeiro_turno / 100)}</b> de eleitores de verdade.</p>
    <div class="es-duas-grades" id="es-grades">
      <figure><figcaption><span class="es-turno">1º turno</span> 4 de outubro</figcaption>${esGrade(N.t1, "1º turno")}</figure>
      <figure><figcaption><span class="es-turno">2º turno</span> 25 de outubro</figcaption>${esGrade(N.t2, "2º turno")}</figure>
    </div>
    <div class="es-legenda" role="group" aria-label="Destacar um grupo nos dois desenhos">
      <div class="es-leg-cab"><span>Grupo</span><span>1º → 2º</span><span>Mudou</span></div>${leg}
    </div>
    <p class="es-info" id="es-info" aria-live="polite">Toque em um grupo para destacá-lo nos dois desenhos.</p>
    <div class="es-caixa">
      <h4>Por que houve 2º turno?</h4>
      <p>Para ganhar já no 1º turno, um candidato precisa de mais da metade dos <b>votos válidos</b> (os votos dados a algum candidato). Flávio teve <b class="mono">${fNum(N.F.pct_validos_t1, 1)}%</b> e Lula <b class="mono">${fNum(N.L.pct_validos_t1, 1)}%</b>: ninguém passou da metade. Os dois mais votados foram para o 2º turno, e Lula venceu com <b class="mono">${fNum(N.L.pct_validos_t2, 1)}%</b>.</p>
    </div>
    <p class="es-obs">Os bonequinhos estão arrumados por cor. O desenho mostra quantas pessoas havia em cada grupo em cada turno, mas não mostra quem mudou de grupo, porque o voto é secreto. Com só 100 bonequinhos os números ficam arredondados; no próximo passo a conta é feita com os votos exatos.</p>`;
}

function esPasso2(N) {
  const Ld = N.L.diferenca, Ot = N.O.primeiro_turno;
  return `<h3>Os eleitores dos candidatos eliminados bastavam para Lula?</h3>
    <div class="es-fatos">
      <div class="es-fato es-borda-lula"><span class="es-fato-num mono">+${esMi(Ld)}</span><span>de votos para Lula do 1º para o 2º turno</span></div>
      <div class="es-fato es-borda-elim"><span class="es-fato-num mono">${esMi(Ot)}</span><span>de votos tinham os 10 candidatos que saíram da disputa</span></div>
    </div>
    <p class="es-lead">Faça o teste: mova o controle e veja quanto do crescimento de Lula os eleitores dos eliminados conseguem cobrir.</p>
    <div class="es-controle">
      <label for="es-elim">Parte dos eleitores dos eliminados que votou em Lula: <output id="es-elim-val" class="mono"></output></label>
      <input type="range" id="es-elim" min="0" max="100" step="5" value="${ES.elim}">
      <div class="es-marcas mono" aria-hidden="true"><span>nenhum</span><span>metade</span><span>todos</span></div>
    </div>
    <div class="es-barra-box">
      <div class="es-barra-tit">Os ${esMi(Ld)} de votos a mais de Lula</div>
      <div class="es-barra" id="es-barra-elim">
        <span class="es-seg es-seg-elim" id="es-seg-elim"></span><span class="es-seg es-seg-falta" id="es-seg-falta"></span>
        <span class="es-marco" style="left:${100 * Ot / Ld}%"><span>se todos os eleitores dos eliminados fossem para Lula</span></span>
      </div>
      <div class="es-barra-leg"><span><i class="es-q es-q-elim"></i>vindos dos eliminados</span><span><i class="es-q es-q-falta"></i>ainda faltam</span></div>
    </div>
    <p class="es-resposta" id="es-elim-txt" aria-live="polite"></p>`;
}

function esPasso3(N) {
  const dBN = N.bn1 - N.bn2, dAB = -N.AB.diferenca, dV = N.V.diferenca, Ot = N.O.primeiro_turno;
  const Ld = N.L.diferenca, Fd = N.F.diferenca, tot = Ot + dV;
  const w = v => `${(100 * v / tot).toFixed(3)}%`;
  return `<h3>Quem passou a votar em alguém no 2º turno</h3>
    <p class="es-lead">Do 1º para o 2º turno, menos gente votou em branco ou nulo e menos gente deixou de ir votar. Essas pessoas passaram a escolher um candidato.</p>
    <div class="es-conta">
      <div class="es-termo"><span class="es-termo-ico">${esIcone("bn")}</span><span class="es-termo-num mono">${esMi(dBN)}</span><span>a menos votando em branco ou nulo<br><small class="mono">${esMi(N.bn1)} → ${esMi(N.bn2)}</small></span></div>
      <span class="es-op" aria-hidden="true">+</span>
      <div class="es-termo"><span class="es-termo-ico">${esIcone("abst")}</span><span class="es-termo-num mono">${esMi(dAB)}</span><span>a menos deixando de votar<br><small class="mono">${esMi(N.AB.primeiro_turno)} → ${esMi(N.AB.segundo_turno)}</small></span></div>
      <span class="es-op" aria-hidden="true">=</span>
      <div class="es-termo es-termo-res"><span class="es-termo-num mono">${esMi(dV)}</span><span>de votos válidos a mais</span></div>
    </div>
    <p class="es-obs">São saldos: algumas pessoas que votaram no 1º turno faltaram no 2º, e outras fizeram o caminho contrário. Os dados mostram só o resultado final dessas idas e vindas.</p>
    <h4 class="es-sub">A conta fecha exatamente</h4>
    <div class="es-fecha">
      <div class="es-fecha-lin"><span class="es-fecha-rot">Votos que precisavam de um novo candidato</span>
        <div class="es-barra"><span class="es-seg es-seg-elim" style="width:${w(Ot)}">${esMi(Ot)}</span><span class="es-seg es-seg-novos" style="width:${w(dV)}">${esMi(dV)}</span></div>
        <div class="es-barra-leg"><span><i class="es-q es-q-elim"></i>eleitores dos eliminados</span><span><i class="es-q es-q-novos"></i>votos válidos a mais</span></div></div>
      <div class="es-fecha-lin"><span class="es-fecha-rot">Quanto os dois finalistas cresceram</span>
        <div class="es-barra"><span class="es-seg es-seg-lula" style="width:${w(Ld)}">Lula +${esMi(Ld)}</span><span class="es-seg es-seg-flavio" style="width:${w(Fd)}">Flávio +${esMi(Fd)}</span></div></div>
    </div>
    <p class="es-resposta">As duas barras têm o mesmo tamanho: <b class="mono">${fInt(tot)}</b> votos. Todo voto que ficou sem candidato (porque o candidato saiu da disputa) ou que apareceu de novo foi parar em Lula ou em Flávio. O que os totais não dizem é <b>quem</b> foi para cada lado. Esse é o próximo passo.</p>`;
}

function esPasso4(N) {
  const pre = [[0, "Ninguém trocou"], [1, "1 milhão trocou"], [3, "3 milhões trocaram"], [6, "6 milhões trocaram"]];
  return `<h3>Duas histórias, o mesmo resultado</h3>
    <p class="es-lead">Os votos a mais de Lula podem ter vindo de pessoas que votaram em Flávio no 1º turno e mudaram de ideia. Ou podem ter vindo só dos eliminados e de quem passou a votar. Mova o controle e veja o que acontece com o resultado.</p>
    <div class="es-controle">
      <label for="es-troca">Eleitores de Flávio no 1º turno que votaram em Lula no 2º: <output id="es-troca-val" class="mono"></output></label>
      <input type="range" id="es-troca" min="0" max="6" step="0.1" value="${ES.troca}">
      <div class="es-atalhos" role="group" aria-label="Exemplos">${pre.map(([v, r]) => `<button type="button" data-v="${v}">${r}</button>`).join("")}</div>
    </div>
    <div class="es-historia">
      <div class="es-hist-lin"><span class="es-fecha-rot"><span class="cand l"><span class="n">13</span>Lula</span> ganhou</span>
        <div class="es-barra"><span class="es-seg es-seg-troca" id="es-h-lt"></span><span class="es-seg es-seg-elim" id="es-h-lo"></span></div>
        <p class="es-hist-txt" id="es-h-ltxt"></p></div>
      <div class="es-hist-lin"><span class="es-fecha-rot"><span class="cand f"><span class="n">22</span>Flávio</span> recebeu e perdeu</span>
        <div class="es-barra"><span class="es-seg es-seg-elim" id="es-h-fo"></span><span class="es-seg es-seg-perdeu" id="es-h-fp"></span></div>
        <p class="es-hist-txt" id="es-h-ftxt"></p></div>
      <div class="es-barra-leg"><span><i class="es-q es-q-troca"></i>eleitores de Flávio que mudaram para Lula</span><span><i class="es-q es-q-elim"></i>vindos dos eliminados e de quem passou a votar</span><span><i class="es-q es-q-perdeu"></i>saíram de Flávio</span></div>
    </div>
    <div class="es-placar-fixo" aria-live="polite"><span class="es-ok-ico" aria-hidden="true">✓</span><div><b>Placar final, em qualquer posição do controle:</b><br>
      <span class="cand l"><span class="n">13</span>Lula</span> <span class="mono">${fInt(N.L.segundo_turno)}</span> &nbsp;×&nbsp; <span class="cand f"><span class="n">22</span>Flávio</span> <span class="mono">${fInt(N.F.segundo_turno)}</span></div></div>
    <div class="es-caixa">
      <h4>Por que não dá para saber qual história aconteceu?</h4>
      <ul>
        <li><b>O voto é secreto.</b> A urna conta quantos votos cada candidato recebeu, mas nunca registra quem votou em quem.</li>
        <li><b>Os dados oficiais são totais.</b> O TSE divulga os resultados de cada seção eleitoral (cerca de 500 mil). Mesmo olhando seção por seção, as várias histórias combinam com os números.</li>
        <li><b>A auditoria do estudo fez a conta:</b> se pelo menos 9 em cada 10 eleitores de cada finalista repetiram o voto, a troca de Flávio para Lula pode ter sido de zero até cerca de 6 milhões de pessoas.</li>
        <li><b>Os modelos estatísticos</b> do estudo apontam para uma troca bem pequena, de cerca de 2 em cada 1.000 eleitores de Flávio. Mas esse número vem de uma suposição: a de que as pessoas se comportaram do mesmo jeito em todas as seções de um mesmo estado. Os próprios dados mostram que essa suposição não vale.</li>
      </ul>
    </div>
    <p class="es-obs">Conta simplificada: as barras juntam os eleitores dos eliminados e os votos válidos a mais, e não separam quem votou no 1º turno e faltou no 2º.</p>`;
}

function esPasso5(N) {
  const col = (cl, ico, tit, sub, itens) => `<div class="es-saber ${cl}"><div class="es-saber-cab"><span class="es-saber-ico" aria-hidden="true">${ico}</span><div><h4>${tit}</h4><span class="es-saber-sub">${sub}</span></div></div>
    <ul>${itens.map(t => `<li>${t}</li>`).join("")}</ul></div>`;
  return `<h3>O que sabemos e o que não sabemos</h3>
    <p class="es-lead">Uma boa pesquisa separa o que foi medido do que foi estimado e do que continua sem resposta.</p>
    <div class="es-saberes">
      ${col("es-certo", "✓", "Com certeza", "Contas com os dados oficiais", [
        `Lula venceu o 2º turno com <b class="mono">${fNum(N.L.pct_validos_t2, 1)}%</b> dos votos válidos; Flávio teve <b class="mono">${fNum(N.F.pct_validos_t2, 1)}%</b>.`,
        "Os arquivos oficiais do TSE foram conferidos uns com os outros e não apresentaram nenhuma diferença.",
        `Lula ganhou ${esMi(N.L.diferenca)} de votos e Flávio ${esMi(N.F.diferenca)} do 1º para o 2º turno.`,
        "Os eleitores dos candidatos eliminados não bastavam para explicar todo o crescimento de Lula.",
        `${esMi(N.V.diferenca)} de pessoas a mais votaram em algum candidato.`])}
      ${col("es-talvez", "≈", "Provável", "Estimativas de modelos estatísticos", [
        "Quase todos os eleitores de cada finalista repetiram o voto (cerca de 98 em cada 100).",
        "Quem tinha votado em branco ou nulo foi mais para Lula do que para Flávio. Os modelos discordam sobre quanto: de 3 a 6 em cada 10 foram para Lula.",
        "Os eleitores dos candidatos eliminados se dividiram entre os dois finalistas."])}
      ${col("es-aberto", "?", "Não dá para saber", "Os dados disponíveis não respondem", [
        "Quantos eleitores de Flávio no 1º turno votaram em Lula no 2º: pode ter sido quase nenhum ou alguns milhões.",
        "Quanto do crescimento de Lula veio de pessoas que trocaram de lado e quanto veio de pessoas que passaram a votar."])}
    </div>`;
}

const ES_TESTE = [
  ["Por que a eleição de 2026 teve 2º turno?", [
    ["Porque nenhum candidato teve mais da metade dos votos válidos no 1º turno.", true, "Isso mesmo. Flávio teve 47,0% e Lula 45,2%; para vencer no 1º turno era preciso passar de 50%."],
    ["Porque toda eleição para presidente tem dois turnos.", false, "Não é sempre assim. Se um candidato passa de 50% dos votos válidos no 1º turno, ele já vence."],
    ["Porque os dois primeiros empataram.", false, "Não houve empate: Flávio ficou 2,2 milhões de votos à frente no 1º turno. O 2º turno aconteceu porque ninguém passou de 50%."]]],
  ["Os votos dos candidatos eliminados bastavam para explicar todo o crescimento de Lula?", [
    ["Sim, e ainda sobravam votos.", false, "Lula ganhou 10,4 milhões e os eliminados tinham 9,3 milhões: mesmo se todos fossem para Lula, faltaria 1,1 milhão."],
    ["Não: mesmo se todos fossem para Lula, faltaria mais de 1 milhão.", true, "Isso mesmo. Os votos que faltam vieram de quem votou em Flávio, em branco ou nulo, ou não tinha ido votar no 1º turno."],
    ["Não dá para saber.", false, "Isso dá para saber com certeza, porque é uma conta com os totais oficiais: faltaria 1,1 milhão."]]],
  ["No 2º turno, o número de pessoas que votaram em branco ou nulo…", [
    ["aumentou.", false, "Diminuiu: passou de 6,0 milhões para 4,2 milhões."],
    ["diminuiu.", true, "Isso mesmo: 1,8 milhão a menos. Essas pessoas passaram a escolher um candidato."],
    ["ficou igual.", false, "Mudou: passou de 6,0 milhões para 4,2 milhões."]]],
  ["Dá para saber, com os dados oficiais, quantos eleitores de Flávio no 1º turno votaram em Lula no 2º?", [
    ["Sim, o TSE divulga essa informação.", false, "O TSE divulga só quantos votos cada candidato teve em cada seção. Como o voto é secreto, ninguém sabe em quem cada pessoa votou."],
    ["Sim, os modelos estatísticos medem esse número exatamente.", false, "Os modelos estimam, e o resultado depende das suposições de cada um. A auditoria mostrou que os dados combinam com troca de zero até alguns milhões."],
    ["Não, porque o voto é secreto e os dados mostram só totais.", true, "Isso mesmo. Várias histórias diferentes levam ao mesmo placar, como você viu no passo 4."]]],
];
function esPasso6() {
  return `<h3>Teste rápido</h3>
    <p class="es-lead">Escolha uma resposta em cada pergunta. Você pode tentar de novo quantas vezes quiser.</p>
    <div class="es-teste">${ES_TESTE.map(([perg, ops], q) => `<fieldset class="es-q-bloco" data-q="${q}"><legend><span class="es-q-n mono">${q + 1}</span>${perg}</legend>
      <div class="es-ops">${ops.map(([t], o) => `<button type="button" class="es-op-btn" data-q="${q}" data-o="${o}" aria-pressed="false">${t}</button>`).join("")}</div>
      <p class="es-retorno" aria-live="polite"></p></fieldset>`).join("")}</div>
    <p class="es-placar-teste" id="es-placar-teste" aria-live="polite"></p>`;
}

const ES_GLOSSARIO = [
  ["Eleitor apto", "pessoa que pode votar naquela eleição."],
  ["Abstenção", "quando o eleitor apto não vai votar."],
  ["Voto branco e voto nulo", "o eleitor vai à urna mas não escolhe candidato: aperta BRANCO ou digita um número que não existe."],
  ["Votos válidos", "os votos dados a algum candidato. São eles que decidem quem vence."],
  ["Seção eleitoral", "o grupo de eleitores que vota na mesma urna; em 2026 foram cerca de 500 mil seções, com pouco mais de 300 eleitores cada, em média."],
  ["Voto secreto", "ninguém pode saber em quem cada pessoa votou; a urna guarda só os totais."],
  ["Modelo estatístico", "um conjunto de contas que tenta estimar o que não pode ser medido diretamente. Sempre parte de suposições."],
];

/* ---------- montagem ---------- */
function esMontar() {
  const raiz = document.getElementById("resumo-estudo");
  if (raiz.dataset.pronto) return;      // estado fica em ES; cores vêm do CSS
  raiz.dataset.pronto = "1";
  const N = esNumeros();
  const corpos = [esPasso1(N), esPasso2(N), esPasso3(N), esPasso4(N), esPasso5(N), esPasso6(N)];
  raiz.innerHTML = `${ES_SIMBOLOS}
    <div class="es-cab">
      <div class="es-cab-txt"><span class="es-selo">Para estudantes</span>
        <h2>A eleição de 2026 em 6 passos</h2>
        <p>Flávio Bolsonaro ficou em 1º lugar no 1º turno, mas Lula venceu o 2º turno. De onde vieram os votos a mais? O que os números oficiais mostram, e o que eles não conseguem mostrar?</p></div>
      ${esUrna()}
    </div>
    <nav class="es-trilha" aria-label="Passos da explicação"><ol>${ES_PASSOS.map((p, i) =>
      `<li><button type="button" data-p="${i}"><span class="es-n mono">${i + 1}</span><span class="es-trilha-rot">${p}</span></button></li>`).join("")}</ol>
      <div class="es-progresso" aria-hidden="true"><span id="es-prog"></span></div></nav>
    ${corpos.map((c, i) => `<article class="es-passo" data-p="${i}" aria-label="Passo ${i + 1} de ${ES_PASSOS.length}: ${ES_PASSOS[i]}" hidden>
      <span class="es-passo-n mono">Passo ${i + 1} de ${ES_PASSOS.length}</span>${c}</article>`).join("")}
    <div class="es-nav">
      <button type="button" class="es-btn" id="es-ant">← Anterior</button>
      <span class="es-nav-pos mono" id="es-pos"></span>
      <button type="button" class="es-btn es-btn-principal" id="es-prox">Próximo →</button>
    </div>
    <details class="es-glossario"><summary>Palavras que aparecem aqui</summary>
      <dl>${ES_GLOSSARIO.map(([t, d]) => `<div><dt>${t}</dt><dd>${d}</dd></div>`).join("")}</dl></details>`;

  // passo 1: destacar grupo
  raiz.querySelectorAll(".es-leg").forEach(b => b.addEventListener("click", () => {
    ES.grupo = ES.grupo === b.dataset.g ? null : b.dataset.g; esGrupo(N);
  }));
  // passo 2
  const el = $("#es-elim", raiz);
  el.addEventListener("input", () => { ES.elim = +el.value; esElim(N); });
  // passo 4
  const tr = $("#es-troca", raiz);
  tr.addEventListener("input", () => { ES.troca = +tr.value; esTroca(N); });
  raiz.querySelectorAll(".es-atalhos button").forEach(b => b.addEventListener("click", () => {
    ES.troca = +b.dataset.v; tr.value = ES.troca; esTroca(N);
  }));
  // passo 6
  raiz.querySelectorAll(".es-op-btn").forEach(b => b.addEventListener("click", () => {
    ES.resp[b.dataset.q] = +b.dataset.o; esTeste();
  }));
  // navegação
  raiz.querySelectorAll(".es-trilha button").forEach(b => b.addEventListener("click", () => esIr(+b.dataset.p)));
  $("#es-ant", raiz).addEventListener("click", () => esIr(ES.passo - 1));
  $("#es-prox", raiz).addEventListener("click", () => esIr(ES.passo + 1 < ES_PASSOS.length ? ES.passo + 1 : 0));

  esGrupo(N); esElim(N); esTroca(N); esTeste(); esIr(ES.passo, false);
}

function esIr(p, rolar = true) {
  ES.passo = Math.max(0, Math.min(ES_PASSOS.length - 1, p));
  const raiz = document.getElementById("resumo-estudo");
  raiz.querySelectorAll(".es-passo").forEach(a => { a.hidden = +a.dataset.p !== ES.passo; });
  raiz.querySelectorAll(".es-trilha button").forEach(b => {
    const i = +b.dataset.p;
    if (i === ES.passo) b.setAttribute("aria-current", "step"); else b.removeAttribute("aria-current");
    b.classList.toggle("feito", i < ES.passo);
  });
  $("#es-prog").style.width = `${100 * (ES.passo + 1) / ES_PASSOS.length}%`;
  $("#es-pos").textContent = `${ES.passo + 1} de ${ES_PASSOS.length}`;
  $("#es-ant").disabled = ES.passo === 0;
  $("#es-prox").textContent = ES.passo === ES_PASSOS.length - 1 ? "Voltar ao início" : `Próximo: ${ES_PASSOS[ES.passo + 1]} →`;
  if (rolar) {
    const topo = raiz.querySelector(".es-trilha").getBoundingClientRect().top;
    if (topo < 0 || topo > window.innerHeight * 0.6) raiz.querySelector(".es-trilha").scrollIntoView({ block: "start", behavior: "smooth" });
  }
}

function esGrupo(N) {
  const g = $("#es-grades");
  if (ES.grupo) g.dataset.sel = ES.grupo; else delete g.dataset.sel;
  document.querySelectorAll("#resumo-estudo .es-leg").forEach(b => b.setAttribute("aria-pressed", String(b.dataset.g === ES.grupo)));
  const info = $("#es-info");
  if (!ES.grupo) { info.textContent = "Toque em um grupo para destacá-lo nos dois desenhos."; return; }
  const k = ES_GRUPOS.findIndex(x => x[0] === ES.grupo), a = N.t1[k], b = N.t2[k], d = b - a;
  const frases = {
    lula: `Lula tinha ${a} bonequinhos no 1º turno e ${b} no 2º: ganhou ${d}.`,
    flavio: `Flávio tinha ${a} bonequinhos no 1º turno e ${b} no 2º: ganhou ${d}. Ficou atrás de Lula no 2º turno.`,
    elim: `Os outros 10 candidatos tinham ${a} bonequinhos no 1º turno. No 2º turno eles não estavam mais na urna, então esses eleitores tiveram de escolher outra opção.`,
    bn: `${a} bonequinhos votaram em branco ou nulo no 1º turno; no 2º, ${b}.`,
    abst: `${a} bonequinhos não foram votar no 1º turno; no 2º, ${b}. Mais gente compareceu.`,
  };
  info.textContent = frases[ES.grupo];
}

function esElim(N) {
  const Ld = N.L.diferenca, Ot = N.O.primeiro_turno, p = ES.elim / 100;
  const vindos = p * Ot, falta = Ld - vindos;
  $("#es-elim-val").textContent = p === 0 ? "nenhum" : p === 1 ? "todos (100%)" : `${ES.elim}%`;
  $("#es-seg-elim").style.width = `${100 * vindos / Ld}%`;
  $("#es-seg-falta").style.width = `${100 * falta / Ld}%`;
  $("#es-seg-elim").textContent = vindos / Ld > 0.18 ? esMi(vindos) : "";
  $("#es-seg-falta").innerHTML = falta / Ld > 0.2 ? `<span class="es-etq">faltam ${esMi(falta)}</span>` : "";
  const t = $("#es-elim-txt");
  if (p === 1) {
    t.innerHTML = `<b>Mesmo com todos os eleitores dos eliminados votando em Lula, ainda faltariam ${fInt(falta)} votos</b> (cerca de ${esMi(falta)}). Esses votos só podem ter vindo de quem, no 1º turno, votou em Flávio, votou em branco ou nulo, ou não foi votar.`;
    t.classList.add("destaque");
  } else {
    t.innerHTML = `Se ${p === 0 ? "nenhum eleitor" : `${ES.elim} em cada 100 eleitores`} dos eliminados ${p === 0 ? "votasse" : "votassem"} em Lula, ${p === 0 ? "nenhum voto viria deles" : `viriam ${esMi(vindos)} de votos`}. Para chegar aos ${esMi(Ld)}, ainda faltariam ${esMi(falta)}. Leve o controle até o fim para ver o caso mais favorável.`;
    t.classList.remove("destaque");
  }
}

function esTroca(N) {
  const Ld = N.L.diferenca, Fd = N.F.diferenca, s = ES.troca * 1e6;
  const escala = Ld;                                // mesma escala nas duas barras
  $("#es-troca-val").textContent = s === 0 ? "nenhum" : esMi(s);
  const set = (id, v, txt) => { const e = $(id); e.style.width = `${100 * v / escala}%`; e.innerHTML = v / escala > 0.16 ? `<span class="es-etq">${txt}</span>` : ""; };
  set("#es-h-lt", s, esMi(s));
  set("#es-h-lo", Ld - s, esMi(Ld - s));
  // Flávio: a barra inteira é o que ele recebeu (Fd + s); a parte listrada saiu para Lula
  set("#es-h-fo", Fd, `saldo +${esMi(Fd)}`);
  set("#es-h-fp", s, `${esMi(s)} saíram`);
  $("#es-h-ltxt").innerHTML = s === 0
    ? `Todos os <b>${esMi(Ld)}</b> vieram dos eliminados e de quem passou a votar.`
    : `<b>${esMi(s)}</b> vieram de eleitores de Flávio e <b>${esMi(Ld - s)}</b> dos eliminados e de quem passou a votar. Total: <b>${esMi(Ld)}</b>.`;
  $("#es-h-ftxt").innerHTML = s === 0
    ? `Recebeu <b>${esMi(Fd)}</b> dos eliminados e de quem passou a votar, e não perdeu ninguém.`
    : `Recebeu <b>${esMi(Fd + s)}</b> dos eliminados e de quem passou a votar, mas perdeu <b>${esMi(s)}</b> para Lula. Saldo: <b>${esMi(Fd)}</b> a mais.`;
  document.querySelectorAll("#resumo-estudo .es-atalhos button").forEach(b => b.setAttribute("aria-pressed", String(+b.dataset.v === ES.troca)));
}

function esTeste() {
  let certas = 0, feitas = 0;
  document.querySelectorAll("#resumo-estudo .es-q-bloco").forEach(fs => {
    const q = +fs.dataset.q, r = ES.resp[q], ops = ES_TESTE[q][1];
    fs.querySelectorAll(".es-op-btn").forEach(b => {
      const o = +b.dataset.o, escolhida = o === r;
      b.setAttribute("aria-pressed", String(escolhida));
      b.classList.toggle("certa", escolhida && ops[o][1]);
      b.classList.toggle("errada", escolhida && !ops[o][1]);
    });
    const ret = fs.querySelector(".es-retorno");
    if (r == null) { ret.textContent = ""; ret.className = "es-retorno"; return; }
    feitas++; if (ops[r][1]) certas++;
    ret.className = "es-retorno " + (ops[r][1] ? "certa" : "errada");
    ret.innerHTML = `<b>${ops[r][1] ? "✓ Certo." : "✕ Ainda não."}</b> ${ops[r][2]}${ops[r][1] ? "" : " Tente outra resposta."}`;
  });
  $("#es-placar-teste").textContent = feitas === 0 ? "" :
    `Você acertou ${certas} de ${ES_TESTE.length} perguntas${feitas < ES_TESTE.length ? ` (respondeu ${feitas})` : ""}.${certas === ES_TESTE.length ? " Parabéns!" : ""}`;
}

/* seletor entre a explicação para estudantes e o resumo completo */
function esVista() {
  let v = "estudo";
  try { v = localStorage.getItem("eleicoes2026-vista-resumo") || "estudo"; } catch (e) { /* armazenamento indisponível */ }
  const aplicar = x => {
    $("#resumo-estudo").hidden = x !== "estudo";
    $("#resumo-completo").hidden = x === "estudo";
    try { localStorage.setItem("eleicoes2026-vista-resumo", x); } catch (e) { /* armazenamento indisponível */ }
  };
  segmentado($("#vista-resumo"), [["estudo", "Explicação Interativa"], ["completo", "Resumo completo"]], v, aplicar);
  aplicar(v);
}
