/* Painel "Transferência de Votos 2026".
   Dados: window.DADOS (dados.js) e window.MAPA (mapa.js), gerados por
   src/analise_10_dashboard.py a partir das tabelas do projeto. */
"use strict";
const D = window.DADOS, M = window.MAPA;

/* ---------------- utilidades ---------------- */
const $ = (s, el = document) => el.querySelector(s);
const cssv = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
function cores() {
  return {
    lula: cssv("--lula"), dir: cssv("--direita"), lulaC: cssv("--lula-claro"), dirC: cssv("--direita-claro"),
    outros: cssv("--outros"), bn: cssv("--bn"), abst: cssv("--abst"), tinta: cssv("--tinta"),
    tinta2: cssv("--tinta-2"), tinta3: cssv("--tinta-3"), linha: cssv("--linha"), linhaF: cssv("--linha-forte"),
    papel: cssv("--papel"), fundo: cssv("--fundo"), meio: cssv("--div-meio"), roxo: cssv("--roxo"),
    verde: cssv("--verde-dado"), realce: cssv("--realce"),
  };
}
let C = cores();
const loc = "pt-BR";
const fInt = n => n == null ? "—" : Math.round(n).toLocaleString(loc);
const fNum = (x, d = 1) => x == null || !isFinite(x) ? "—" : x.toLocaleString(loc, { minimumFractionDigits: d, maximumFractionDigits: d });
const fPct = (x, d = 1) => x == null || !isFinite(x) ? "—" : fNum(x, d) + "%";
const fMi = (n, d = 2) => n == null ? "—" : fNum(n / 1e6, d) + " mi";
const fSin = (x, d = 1) => x == null || !isFinite(x) ? "—" : (x > 0 ? "+" : x < 0 ? "−" : "") + fNum(Math.abs(x), d);
const fP = p => p == null ? "—" : p < 0.0001 ? "< 0,0001" : fNum(p, p < 0.01 ? 4 : 3);
const larg = el => Math.max(280, el.clientWidth || el.parentElement.clientWidth || 600);
const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

const dica = $("#dica");
function mostrarDica(html, ev) {
  dica.innerHTML = html; dica.style.display = "block";
  const r = dica.getBoundingClientRect();
  let x = ev.clientX + 14, y = ev.clientY + 14;
  if (x + r.width > window.innerWidth - 8) x = ev.clientX - r.width - 14;
  if (y + r.height > window.innerHeight - 8) y = ev.clientY - r.height - 14;
  dica.style.left = Math.max(8, x) + "px"; dica.style.top = Math.max(8, y) + "px";
}
const esconderDica = () => { dica.style.display = "none"; };

function segmentado(el, opcoes, valor, aoMudar) {
  el.innerHTML = "";
  opcoes.forEach(([v, rot]) => {
    const b = document.createElement("button");
    b.type = "button"; b.textContent = rot; b.setAttribute("aria-pressed", String(v === valor));
    b.addEventListener("click", () => {
      el.querySelectorAll("button").forEach(x => x.setAttribute("aria-pressed", "false"));
      b.setAttribute("aria-pressed", "true"); aoMudar(v);
    });
    el.appendChild(b);
  });
}
function legenda(el, itens) {
  el.innerHTML = itens.map(([cor, rot, extra = ""]) => `<span><i style="background:${cor};${extra}"></i>${rot}</span>`).join("");
}
function tabela(el, cab, linhas, classes = []) {
  el.innerHTML = `<thead><tr>${cab.map((h, i) => `<th class="${classes[i] || ""}">${h}</th>`).join("")}</tr></thead>` +
    `<tbody>${linhas.map(l => `<tr>${l.map((c, i) => `<td class="${classes[i] || ""}">${c}</td>`).join("")}</tr>`).join("")}</tbody>`;
}

const NOMES = { 2026: ["Lula", "Flávio"], 2022: ["Lula", "J. Bolsonaro"], 2018: ["Haddad", "J. Bolsonaro"] };
const NOMES_LONGOS = { 2026: ["Lula", "Flávio Bolsonaro"], 2022: ["Lula", "Jair Bolsonaro"], 2018: ["Haddad", "Jair Bolsonaro"] };
const ORIG = ["a_1", "b_1", "o_1", "bn_1", "abst_1"], DEST = ["a_2", "b_2", "bn_2", "abst_2"];
function nomeCat(cod, ano = 2026) {
  const [a, b] = NOMES[ano];
  return ({ a_1: a, b_1: b, o_1: "Eliminados", bn_1: "Brancos e nulos", abst_1: "Abstenção",
    a_2: a, b_2: b, bn_2: "Brancos e nulos", abst_2: "Abstenção",
    cury_1: "Augusto Cury", renan_1: "Renan Santos", caiado_1: "Ronaldo Caiado", demais_1: "Zema e demais" })[cod] || cod;
}
function corCat(cod) {
  const k = cod.split("_")[0];
  return ({ a: C.lula, b: C.dir, o: C.outros, bn: C.bn, abst: C.abst, cury: C.outros, renan: C.outros, caiado: C.outros, demais: C.outros })[k] || C.tinta3;
}
const matriz = (ano, nivel, origens = "base") => D.matrizes.filter(m => m.ano === ano && m.nivel === nivel && m.origens === origens);

/* ---------------- abas ---------------- */
const ABAS = ["resumo", "contas", "mapa", "comparecimento", "transferencias", "migracao", "legislativo", "anomalias", "historico", "investigando", "fontes"];
const renderizar = {}, feitos = new Set();
let abaAtual = "resumo";
function abrir(id, foco = false) {
  if (!ABAS.includes(id)) id = "resumo";
  abaAtual = id;
  ABAS.forEach(a => {
    $("#" + a).hidden = a !== id;
    const b = $("#aba-" + a);
    b.setAttribute("aria-selected", String(a === id)); b.tabIndex = a === id ? 0 : -1;
  });
  if (foco) $("#aba-" + id).focus();
  $("#abas-select").value = id;
  try { history.replaceState(null, "", "#" + id); } catch (e) { /* sem histórico */ }
  if (renderizar[id]) { renderizar[id](); feitos.add(id); }
  esconderDica();
}
// seletor de seção para telas estreitas: mesmas opções e mesmos nomes das abas
$("#abas-select").innerHTML = ABAS.map(a => `<option value="${a}">${$("#aba-" + a).textContent}</option>`).join("");
$("#abas-select").addEventListener("change", e => { abrir(e.target.value); window.scrollTo({ top: 0 }); });
document.querySelectorAll("#abas button").forEach(b => {
  b.addEventListener("click", () => abrir(b.getAttribute("aria-controls")));
  b.addEventListener("keydown", e => {
    const i = ABAS.indexOf(abaAtual);
    if (e.key === "ArrowRight") abrir(ABAS[(i + 1) % ABAS.length], true);
    if (e.key === "ArrowLeft") abrir(ABAS[(i - 1 + ABAS.length) % ABAS.length], true);
  });
});
document.addEventListener("click", e => {
  const a = e.target.closest("a[href^='#']");
  if (a && ABAS.includes(a.getAttribute("href").slice(1))) { e.preventDefault(); abrir(a.getAttribute("href").slice(1)); window.scrollTo({ top: 0 }); }
});

/* ---------------- RESUMO ---------------- */
renderizar.resumo = function () {
  $("#gerado-em").textContent = D.gerado_em;
  esMontar(); esVista();   // explicação para estudantes (estudo.js)
  const R = Object.fromEntries(D.reconciliacao.map(r => [r.indicador, r]));
  const L = R["Lula"], F = R["Flávio Bolsonaro"], O = R["Outros candidatos"];
  const cand = (cl, n, nome) => `<span class="cand ${cl}"><span class="n">${n}</span>${nome}</span>`;
  const turno = (data, titulo, linhas, barras) => `<div class="turno"><div class="data">${data}</div><h3>${titulo}</h3>
    ${linhas.map(l => `<div class="linha-cand">${l[0]}<span><span class="pct">${fPct(l[1], 2)}</span> <span class="votos">${fInt(l[2])} votos</span></span></div>`).join("")}
    <div class="barra-empilhada" role="img" aria-label="${titulo}">${barras.map(b => `<span style="width:${b[0]}%;background:${b[1]}"></span>`).join("")}</div></div>`;
  $("#placar").innerHTML =
    turno("Domingo, 4 de outubro", "1º turno", [[cand("f", 22, "Flávio Bolsonaro"), F.pct_validos_t1, F.primeiro_turno],
      [cand("l", 13, "Lula"), L.pct_validos_t1, L.primeiro_turno], [`<span class="cand">Outros 10 candidatos</span>`, O.pct_validos_t1, O.primeiro_turno]],
      [[L.pct_validos_t1, C.lula], [O.pct_validos_t1, C.outros], [F.pct_validos_t1, C.dir]]) +
    turno("Domingo, 25 de outubro", "2º turno", [[cand("l", 13, "Lula"), L.pct_validos_t2, L.segundo_turno],
      [cand("f", 22, "Flávio Bolsonaro"), F.pct_validos_t2, F.segundo_turno]],
      [[L.pct_validos_t2, C.lula], [F.pct_validos_t2, C.dir]]);
  const qm = D.quantidades_minimas.find(q => q.nivel === "nacional");
  const fl = matriz(2026, "secao").find(m => m.origem === "b_1" && m.destino === "a_2");
  const bl = matriz(2026, "secao").find(m => m.origem === "bn_1" && m.destino === "a_2");
  const ach = [
    [fMi(qm.lula_2T_alem_de_lula1T_e_outros1T), "votos de Lula no 2º turno que, pela aritmética, não podem ter vindo nem dos seus eleitores nem dos candidatos eliminados.", "oficial", "Cálculo exato"],
    [fPct(100 * fl.taxa, 1), `dos eleitores de Flávio no 1º turno votaram em Lula no 2º, segundo o modelo principal (intervalo ${fPct(100 * fl.taxa_ic95_inf, 2)} a ${fPct(100 * fl.taxa_ic95_sup, 2)}; todos os modelos: abaixo de 1%).`, "estimativa", "Estimativa"],
    [fPct(100 * bl.taxa, 0), "de quem votou em branco ou nulo no 1º turno votou em Lula no 2º, segundo o modelo. Para Flávio: cerca de 1,5%.", "estimativa", "Estimativa"],
    ["0", "divergências entre os boletins de urna de 52.335 seções e os demais arquivos oficiais do TSE.", "oficial", "Verificação"],
  ];
  $("#achados").innerHTML = ach.map(a => `<div class="bloco achado"><span class="natureza ${a[2]}">${a[3]}</span><div class="grande">${a[0]}</div><p>${a[1]}</p></div>`).join("");
  const P = [
    ["Os votos válidos a mais apareceram principalmente onde Lula já liderava?", "Apareceram em todo o país, um pouco mais onde Lula liderava, por causa da queda maior de brancos e nulos nesses lugares. Considerando outros fatores, a vantagem inicial de Lula quase não pesa.", [["parcial", "Parcialmente sustentada"]], "comparecimento"],
    ["Os votos dos candidatos eliminados bastam para explicar o crescimento dos finalistas?", "Não. O crescimento de Lula supera todos os votos dos eliminados. Somados ao aumento de votos válidos, explicam a conta. Os eliminados se dividiram: cerca de 42% para Lula e 39% para Flávio.", [["nao", "Só os eliminados: não sustentada"], ["ok", "Eliminados + mobilização: sustentada"]], "contas"],
    ["É possível explicar o resultado sem troca relevante de eleitores de Flávio para Lula?", "Sim. Todos os modelos estimam troca abaixo de 1%. Para isso, é preciso que quem votou em branco, nulo ou não votou no 1º turno tenha ido muito mais para Lula. Exceção localizada: Macapá e Santana (AP). A aritmética sozinha não permite separar troca de lado e mobilização.", [["ok", "Sustentada (sob as hipóteses dos modelos)"], ["indet", "Sem essas hipóteses: indeterminada"]], "migracao"],
    ["A queda de abstenções, brancos e nulos está associada ao crescimento de Lula?", "Sim. Onde os votos válidos mais aumentaram, Lula mais cresceu (correlação de 0,78 entre municípios). É uma associação entre lugares, não entre pessoas.", [["ok", "Sustentada"]], "comparecimento"],
    ["O PL ter ido bem para deputado e Lula ter vencido para presidente é compatível com voto dividido?", "Sim. Flávio teve cerca do dobro dos votos do PL, diferença menor que em 2022 e 2018. Estima-se que cerca de 5% dos eleitores do PL votaram em Lula.", [["ok", "Sustentada"]], "legislativo"],
    ["Existem padrões fora do comum que resistem a controles e testes?", "Dois: a mobilização de brancos, nulos e abstencionistas a favor de Lula, maior que em 2018 e 2022; e Macapá/Santana. Nenhum corresponde a inconsistência nos dados, e ambos têm explicações possíveis que os dados agregados não permitem separar.", [["parcial", "Parcialmente sustentada"]], "anomalias"],
    ["2026 foi diferente de 2018 e 2022?", "Na fidelidade aos finalistas e nos desvios dos modelos, não. No aumento de votos válidos e na queda de brancos e nulos, sim.", [["parcial", "Parcialmente sustentada"]], "historico"],
  ];
  $("#perguntas").innerHTML = P.map((p, i) => `<article><span class="idx">${i + 1}</span><div><h4>${p[0]}</h4><p class="resp">${p[1]}</p>
    <div class="meta">${p[2].map(s => `<span class="pill ${s[0]}">${s[1]}</span>`).join("")}<a href="#${p[3]}">ver</a></div></div></article>`).join("");
};

/* ---------------- CONTAS ---------------- */
function barrasHorizontais(el, linhas, opt = {}) {
  /* linhas: [{rotulo, partes:[{v, cor, rot}]}] — barras empilhadas */
  const W = larg(el), mE = opt.margemEsq ?? Math.min(170, W * .4), alt = opt.alt ?? 34, gap = opt.gap ?? 16;
  const H = linhas.length * (alt + gap) + 26;
  const max = opt.max ?? d3.max(linhas, l => d3.sum(l.partes, p => p.v));
  const x = d3.scaleLinear().domain([0, max]).range([mE, W - 10]);
  const svg = d3.select(el).html("").append("svg").attr("viewBox", `0 0 ${W} ${H}`);
  svg.append("g").attr("class", "eixo").attr("transform", `translate(0,${H - 20})`)
    .call(d3.axisBottom(x).ticks(Math.max(3, W / 110)).tickFormat(opt.fmtEixo || (v => fNum(v / 1e6, 0) + " mi")));
  linhas.forEach((l, i) => {
    const y = i * (alt + gap) + 4;
    svg.append("text").attr("class", "rot-forte").attr("x", mE - 8).attr("y", y + alt / 2 + 4).attr("text-anchor", "end").text(l.rotulo);
    let acc = 0;
    l.partes.forEach(p => {
      const x0 = x(acc), x1 = x(acc + p.v); acc += p.v;
      const g = svg.append("g");
      g.append("rect").attr("x", x0).attr("y", y).attr("width", Math.max(0, x1 - x0 - 2)).attr("height", alt).attr("rx", 2).attr("fill", p.cor)
        .on("mousemove", ev => mostrarDica(p.dica || `<b>${p.rot}</b><br><span class="mono">${fInt(p.v)}</span>`, ev)).on("mouseleave", esconderDica);
      if (p.rot && x1 - x0 > (p.curto || p.rot).length * 6.8 + 14) g.append("text").attr("x", x0 + 8).attr("y", y + alt / 2 + 4).attr("fill", "#fff")
        .style("font", "700 12px var(--f-texto)").style("pointer-events", "none").text(p.curto || p.rot);
    });
  });
}

renderizar.contas = function () {
  const R = D.reconciliacao;
  tabela($("#tab-reconc"), ["", "1º turno", "2º turno", "Diferença"],
    R.map(r => [r.indicador, fInt(r.primeiro_turno), fInt(r.segundo_turno), fSin(r.diferenca, 0)]), ["", "num", "num", "num"]);
  const g = Object.fromEntries(R.map(r => [r.indicador, r]));
  const dL = g["Lula"].diferenca, dF = g["Flávio Bolsonaro"].diferenca, O = g["Outros candidatos"].primeiro_turno, dV = g["Votos válidos"].diferenca;
  barrasHorizontais($("#g-identidade"), [
    { rotulo: "Ganho dos finalistas", partes: [{ v: dL, cor: C.lula, rot: "Lula +" + fMi(dL), curto: "Lula +" + fMi(dL) }, { v: dF, cor: C.dir, rot: "Flávio +" + fMi(dF), curto: "Flávio +" + fMi(dF) }] },
    { rotulo: "Origem possível", partes: [{ v: O, cor: C.outros, rot: "Votos dos eliminados " + fMi(O), curto: "Eliminados " + fMi(O) }, { v: dV, cor: C.bn, rot: "Aumento de votos válidos " + fMi(dV), curto: "Novos válidos " + fMi(dV) }] },
  ]);
  legenda($("#leg-identidade"), [[C.lula, "Lula"], [C.dir, "Flávio"], [C.outros, "Votos dos eliminados no 1º turno"], [C.bn, "Aumento dos votos válidos (menos brancos, nulos e abstenções)"]]);

  const QM = D.quantidades_minimas;
  const rot = { "nacional": "Brasil (1 conta)", "UF": "Por estado (28)", "município": "Por município (5.757)", "seção (todas; sem divisão por candidato no 2T)": "Por seção (499.248)", "seção (todas; votacao_secao do 2T)": "Por seção (499.248)", "seção (amostra de BUs, sem expansão)": "Por seção, só a amostra de BUs (50.821)" };
  tabela($("#tab-minimos"), ["Somando", "Votos de Lula que não vêm de Lula nem dos eliminados", "Válidos do 2º turno sem voto válido no 1º", "Troca mínima Flávio → Lula"],
    QM.map(q => [rot[q.nivel] || q.nivel, fInt(q.lula_2T_alem_de_lula1T_e_outros1T), fInt(q.validos_2T_sem_origem_valida_1T), q.min_flavio1T_para_lula2T == null ? "—" : fInt(q.min_flavio1T_para_lula2T)]),
    ["", "num", "num", "num"]);

  // ganhos e perdas estimados
  const m = matriz(2026, "secao");
  const v = (o, d) => m.find(x => x.origem === o && x.destino === d);
  const blocos = [["a", "Lula", C.lula], ["b", "Flávio", C.dir]];
  const el = $("#g-decomp"); el.innerHTML = "";
  blocos.forEach(([k, nome]) => {
    const outro = k === "a" ? "b" : "a";
    const itens = [
      { r: "Eleitores dos eliminados", c: v("o_1", k + "_2") },
      { r: "Brancos e nulos no 1º turno", c: v("bn_1", k + "_2") },
      { r: "Não votaram no 1º turno", c: v("abst_1", k + "_2") },
      { r: `Eleitores de ${nomeCat(outro + "_1")}`, c: v(outro + "_1", k + "_2") },
      { r: "Perdidos para brancos e nulos", c: v(k + "_1", "bn_2"), neg: true },
      { r: "Perdidos para a abstenção", c: v(k + "_1", "abst_2"), neg: true },
      { r: `Perdidos para ${nomeCat(outro + "_2")}`, c: v(k + "_1", outro + "_2"), neg: true },
    ];
    const div = document.createElement("div"); el.appendChild(div);
    const W = larg(el), mE = Math.min(210, W * .42), alt = 22, H = itens.length * (alt + 8) + 52;
    const max = 4.2e6, x = d3.scaleLinear().domain([-1e6, max]).range([mE, W - 50]);
    const svg = d3.select(div).append("svg").attr("viewBox", `0 0 ${W} ${H}`);
    const liq = d3.sum(itens, i => (i.neg ? -1 : 1) * i.c.votos);
    svg.append("text").attr("class", "rot-forte").attr("x", 0).attr("y", 14).style("font-size", "14px")
      .text(`${nome}: ${fSin(liq / 1e6, 2)} mi estimados (oficial: ${fSin((k === "a" ? 10376694 : 3721538) / 1e6, 2)} mi)`);
    svg.append("line").attr("x1", x(0)).attr("x2", x(0)).attr("y1", 22).attr("y2", H - 22).attr("stroke", C.linhaF);
    itens.forEach((it, i) => {
      const y = 26 + i * (alt + 8), val = (it.neg ? -1 : 1) * it.c.votos;
      svg.append("text").attr("class", "rot-medio").attr("x", mE - 8).attr("y", y + alt / 2 + 4).attr("text-anchor", "end").text(it.r);
      svg.append("rect").attr("x", Math.min(x(0), x(val))).attr("y", y).attr("height", alt).attr("rx", 2)
        .attr("width", Math.max(1.5, Math.abs(x(val) - x(0)))).attr("fill", it.neg ? C.tinta3 : corCat(it.c.origem))
        .on("mousemove", ev => mostrarDica(`<b>${it.r}</b><br><span class="mono">${fInt(it.c.votos)}</span><br>intervalo de 95%: <span class="mono">${fInt(it.c.votos_ic95_inf)} a ${fInt(it.c.votos_ic95_sup)}</span><br>taxa: ${fPct(100 * it.c.taxa, 2)} do grupo de origem`, ev))
        .on("mouseleave", esconderDica);
      // perdas: valor escrito à direita da linha do zero, para não cobrir o nome da categoria
      svg.append("text").attr("class", "rot").attr("x", val >= 0 ? x(val) + 5 : x(0) + 5).attr("y", y + alt / 2 + 4)
        .attr("text-anchor", "start").text(fSin(val / 1e6, 2) + " mi");
    });
  });
  legenda($("#leg-decomp"), [[C.outros, "Eliminados"], [C.bn, "Brancos e nulos"], [C.abst, "Abstenção"], [C.lula, "Lula"], [C.dir, "Flávio"], [C.tinta3, "Perdas"]]);

  // limites aritméticos
  const L = D.limites_municipio;
  const lin = [["b_1", "a_2", "Eleitores de Flávio que votaram em Lula"], ["a_1", "b_2", "Eleitores de Lula que votaram em Flávio"]].map(([o, d, r]) => {
    const l = L.find(x => x.origem === o && x.destino === d); const e = m.find(x => x.origem === o && x.destino === d);
    return { r, min: l.min_taxa, max: l.max_taxa, est: e.taxa };
  });
  const elL = $("#g-limites"), W = larg(elL), mE = Math.min(250, W * .4), H = lin.length * 46 + 34;
  const x = d3.scaleLinear().domain([0, 1]).range([mE, W - 12]);
  const svg = d3.select(elL).html("").append("svg").attr("viewBox", `0 0 ${W} ${H}`);
  svg.append("g").attr("class", "eixo").attr("transform", `translate(0,${H - 24})`).call(d3.axisBottom(x).ticks(5).tickFormat(t => fPct(100 * t, 0)));
  lin.forEach((l, i) => {
    const y = 10 + i * 46;
    svg.append("text").attr("class", "rot-forte").attr("x", mE - 8).attr("y", y + 14).attr("text-anchor", "end").text(l.r);
    svg.append("rect").attr("x", x(l.min)).attr("y", y + 4).attr("width", x(l.max) - x(l.min)).attr("height", 14).attr("rx", 7).attr("fill", C.linhaF);
    svg.append("circle").attr("cx", x(l.est)).attr("cy", y + 11).attr("r", 6).attr("fill", C.tinta);
    svg.append("text").attr("class", "rot").attr("x", x(l.max) - 4).attr("y", y + 32).attr("text-anchor", "end").text(`possível pela aritmética: ${fPct(100 * l.min, 0)} a ${fPct(100 * l.max, 1)} · ● estimativa do modelo: ${fPct(100 * l.est, 2)}`);
  });
};

/* ---------------- MAPA ---------------- */
const MC = D.municipios.colunas, MUN = D.municipios.linhas.map(l => Object.fromEntries(MC.map((c, i) => [c, l[i]])));
const MUN_ID = Object.fromEntries(MUN.map(m => [m.id, m]));
const VARS = {
  dM: { rot: "Variação da margem Lula − Flávio (pontos percentuais)", tipo: "div", neg: () => C.dir, pos: () => C.lula, sim: true, fmt: v => fSin(v, 1) + " p.p.", nota: "Vermelho: a margem de Lula melhorou; azul: a de Flávio melhorou." },
  dL: { rot: "Votos a mais para Lula (por 100 aptos)", tipo: "div", neg: () => C.roxo, pos: () => C.lula, fmt: v => fSin(v, 1), nota: "Diferença entre os votos de Lula no 2º e no 1º turno, a cada 100 eleitores." },
  dF: { rot: "Votos a mais para Flávio (por 100 aptos)", tipo: "div", neg: () => C.roxo, pos: () => C.dir, fmt: v => fSin(v, 1), nota: "Roxo: Flávio teve menos votos no 2º turno do que no 1º." },
  dV: { rot: "Variação dos votos válidos (por 100 aptos)", tipo: "div", neg: () => C.roxo, pos: () => C.verde, fmt: v => fSin(v, 1), nota: "Verde: mais votos válidos no 2º turno; roxo: menos." },
  dC: { rot: "Variação do comparecimento (pontos percentuais)", tipo: "div", neg: () => C.roxo, pos: () => C.verde, fmt: v => fSin(v, 1) + " p.p.", nota: "Diferença entre a parcela de eleitores que foi votar no 2º e no 1º turno." },
  o1: { rot: "Votos dos candidatos eliminados no 1º turno (% dos válidos)", tipo: "seq", pos: () => C.outros, fmt: v => fPct(v, 1), nota: "Onde estavam os eleitores que precisaram escolher outro candidato no 2º turno." },
  l2: { rot: "Lula no 2º turno (% dos válidos)", tipo: "div", neg: () => C.dir, pos: () => C.lula, centro: 50, fmt: v => fPct(v, 1), nota: "Acima de 50%: Lula venceu no município; abaixo: Flávio." },
  z: { rot: "Desvio em relação ao modelo (votos de Lula no 2º turno)", tipo: "div", neg: () => C.dir, pos: () => C.lula, sim: true, dom: 4, fmt: v => fSin(v, 2), nota: "Estimativa (Modelo D). Vermelho: Lula acima do esperado; azul: abaixo. Valores além de ±3 são raros. Brasília aparece por limitação do modelo municipal." },
};
let varMapa = "dM", munFixo = null, mapaFeito = false;
function escalaVar(k) {
  const v = VARS[k], vals = MUN.map(m => m[k]).filter(x => x != null);
  if (v.tipo === "seq") {
    const lo = d3.quantile(vals.slice().sort(d3.ascending), .01), hi = d3.quantile(vals.slice().sort(d3.ascending), .99);
    return d3.scaleSequential(d3.interpolateRgb(C.meio, v.pos())).domain([lo, hi]).clamp(true);
  }
  const c = v.centro ?? 0, s = vals.slice().sort(d3.ascending);
  let lo = d3.quantile(s, .01), hi = d3.quantile(s, .99);
  if (v.dom) { lo = -v.dom; hi = v.dom; }
  if (v.sim) { const a = Math.max(Math.abs(lo - c), Math.abs(hi - c)); lo = c - a; hi = c + a; }
  lo = Math.min(lo, c - 0.1); hi = Math.max(hi, c + 0.1);
  return d3.scaleDiverging(d3.interpolateRgbBasis([v.neg(), C.meio, v.pos()])).domain([lo, c, hi]).clamp(true);
}
function fichaHTML(m) {
  if (!m) return `<p class="nota">Passe o mouse ou toque em um município para ver os números. Clique para fixar.</p>`;
  const lin = [["Eleitores aptos", fInt(m.aptos)], ["Lula 1º turno", fPct(m.l1)], ["Lula 2º turno", fPct(m.l2)], ["Flávio 1º turno", fPct(m.f1)], ["Flávio 2º turno", fPct(m.f2)],
    ["Eliminados no 1º turno", fPct(m.o1)], ["Lula: votos a mais por 100 aptos", fSin(m.dL)], ["Flávio: votos a mais por 100 aptos", fSin(m.dF)],
    ["Válidos: variação por 100 aptos", fSin(m.dV)], ["Comparecimento: variação", fSin(m.dC) + " p.p."], ["Desvio do modelo (estimativa)", fSin(m.z, 2)]];
  return `<h3>${esc(m.nome)} · ${m.uf}</h3><dl>${lin.map(l => `<dt>${l[0]}</dt><dd>${l[1]}</dd>`).join("")}</dl>${munFixo ? `<p class="nota">Fixado. Clique de novo para soltar.</p>` : ""}`;
}
function pintarMapa() {
  const s = escalaVar(varMapa), v = VARS[varMapa];
  d3.selectAll("#mapa-svg path.mun").attr("fill", function () { const m = MUN_ID[this.dataset.id]; return m && m[varMapa] != null ? s(m[varMapa]) : C.linha; });
  // legenda
  const el = $("#mapa-legenda"), W = Math.min(520, larg(el)), dom = s.domain();
  const x = d3.scaleLinear().domain([dom[0], dom[dom.length - 1]]).range([10, W - 10]);
  const svg = d3.select(el).html("").append("svg").attr("viewBox", `0 0 ${W} 46`).style("max-width", W + "px");
  const id = "grad-mapa", gr = svg.append("defs").append("linearGradient").attr("id", id);
  d3.range(0, 1.0001, .1).forEach(t => gr.append("stop").attr("offset", t).attr("stop-color", s(dom[0] + t * (dom[dom.length - 1] - dom[0]))));
  svg.append("rect").attr("x", 10).attr("y", 4).attr("width", W - 20).attr("height", 10).attr("rx", 2).attr("fill", `url(#${id})`);
  svg.append("g").attr("class", "eixo").attr("transform", "translate(0,16)").call(d3.axisBottom(x).ticks(5).tickFormat(t => v.fmt(t)));
  $("#mapa-nota").textContent = v.nota;
}
renderizar.mapa = function () {
  const sel = $("#sel-var");
  if (!mapaFeito) {
    sel.innerHTML = Object.entries(VARS).map(([k, v]) => `<option value="${k}">${v.rot}</option>`).join("");
    sel.value = varMapa;
    sel.addEventListener("change", () => { varMapa = sel.value; pintarMapa(); });
    $("#lista-mun").innerHTML = MUN.map(m => `<option value="${esc(m.nome)} (${m.uf})"></option>`).join("");
    // busca tolerante: ignora acentos, maiúsculas e espaços extras; aceita "Nome (UF)" ou só o nome
    const norm = s => s.normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/\s+/g, " ").trim().toUpperCase();
    const buscar = valor => {
      const t = norm(valor), msg = $("#busca-msg");
      if (!t) { msg.textContent = ""; return; }
      const exatos = MUN.filter(x => norm(`${x.nome} (${x.uf})`) === t || norm(x.nome) === t);
      const achados = exatos.length ? exatos : MUN.filter(x => norm(x.nome).startsWith(t));
      if (!achados.length) { msg.textContent = `Nenhum município começa com "${valor.trim()}". Confira a grafia.`; return; }
      if (achados.length > 1 && !exatos.length) { msg.textContent = `${achados.length} municípios começam assim; escolha um na lista.`; return; }
      if (achados.length > 1) { msg.textContent = `Há ${achados.length} municípios com esse nome (${achados.map(a => a.uf).join(", ")}); mostrando o de ${achados[0].uf}. Para outro, escolha na lista com a UF.`; }
      else msg.textContent = "";
      const m = achados[0];
      munFixo = m.id; d3.selectAll("#mapa-svg path.mun").classed("sel", function () { return this.dataset.id === m.id; });
      $("#ficha").innerHTML = fichaHTML(m);
    };
    $("#busca-mun").addEventListener("change", e => buscar(e.target.value));
    $("#busca-mun").addEventListener("keydown", e => { if (e.key === "Enter") buscar(e.target.value); });
    const svg = d3.select("#g-mapa").append("svg").attr("id", "mapa-svg").attr("viewBox", `0 0 ${M.largura} ${M.altura}`)
      .attr("role", "img").attr("aria-label", "Mapa dos municípios do Brasil");
    const g = svg.append("g");
    Object.entries(M.municipios).forEach(([id, d]) => { if (d) g.append("path").attr("class", "mun").attr("d", d).attr("data-id", id); });
    Object.values(M.ufs).forEach(d => svg.append("path").attr("class", "uf").attr("d", d));
    g.selectAll("path.mun")
      .on("mousemove", function (ev) {
        const m = MUN_ID[this.dataset.id]; if (!m) return;
        mostrarDica(`<b>${esc(m.nome)} · ${m.uf}</b><br>${VARS[varMapa].rot}: <span class="mono">${VARS[varMapa].fmt(m[varMapa])}</span>`, ev);
        if (!munFixo) $("#ficha").innerHTML = fichaHTML(m);
      })
      .on("mouseleave", esconderDica)
      .on("click", function () {
        const id = this.dataset.id; munFixo = munFixo === id ? null : id;
        d3.selectAll("#mapa-svg path.mun").classed("sel", function () { return this.dataset.id === munFixo; });
        $("#ficha").innerHTML = fichaHTML(munFixo ? MUN_ID[id] : null);
      });
    const su = $("#sel-uf");
    const MET = { var_comparecimento_pp: "Variação do comparecimento (p.p.)", var_validos_por_100_aptos: "Variação dos votos válidos (por 100 aptos)",
      var_lula_por_100_aptos: "Votos a mais para Lula (por 100 aptos)", var_flavio_por_100_aptos: "Votos a mais para Flávio (por 100 aptos)",
      lula_2T_pct_validos: "Lula no 2º turno (% dos válidos)" };
    su.innerHTML = Object.entries(MET).map(([k, v]) => `<option value="${k}">${v}</option>`).join("");
    su.addEventListener("change", () => rankingUF(su.value));
    mapaFeito = true;
  }
  sel.value = varMapa;
  pintarMapa();
  rankingUF($("#sel-uf").value);
};
function rankingUF(k) {
  const el = $("#g-ufs"), dados = D.ufs.slice().sort((a, b) => b[k] - a[k]);
  const W = larg(el), mE = 40, alt = 14, H = dados.length * (alt + 5) + 30;
  const ext = d3.extent(dados, d => d[k]), lo = Math.min(0, ext[0]), hi = Math.max(0, ext[1]);
  const x = d3.scaleLinear().domain(k === "lula_2T_pct_validos" ? [0, 100] : [lo, hi]).nice().range([mE, W - 60]);
  const cor = d => k.includes("lula") ? C.lula : k.includes("flavio") ? C.dir : d[k] < 0 ? C.roxo : C.verde;
  const svg = d3.select(el).html("").append("svg").attr("viewBox", `0 0 ${W} ${H}`);
  svg.append("g").attr("class", "eixo").attr("transform", `translate(0,${H - 22})`).call(d3.axisBottom(x).ticks(6).tickFormat(t => fNum(t, 0)));
  const x0 = k === "lula_2T_pct_validos" ? x(0) : x(0);
  dados.forEach((d, i) => {
    const y = i * (alt + 5);
    svg.append("text").attr("class", "rot-forte").attr("x", mE - 6).attr("y", y + alt - 2).attr("text-anchor", "end").text(d.uf);
    svg.append("rect").attr("x", Math.min(x0, x(d[k]))).attr("y", y).attr("width", Math.max(1, Math.abs(x(d[k]) - x0))).attr("height", alt).attr("rx", 2).attr("fill", cor(d))
      .on("mousemove", ev => mostrarDica(`<b>${d.uf}</b> (${d.regiao})<br>${$("#sel-uf").selectedOptions[0].text}: <span class="mono">${fSin(d[k], 2)}</span><br>Comparecimento: ${fPct(d.comparecimento_1T_pct)} → ${fPct(d.comparecimento_2T_pct)}<br>Lula: ${fPct(d.lula_1T_pct_validos)} → ${fPct(d.lula_2T_pct_validos)}`, ev))
      .on("mouseleave", esconderDica);
    const xv = x(d[k]);
    svg.append("text").attr("class", "rot").attr("x", d[k] >= 0 ? xv + 4 : xv - 4).attr("y", y + alt - 3).attr("text-anchor", d[k] >= 0 ? "start" : "end")
      .text(fSin(d[k], 1) + (D.governador_2t.includes(d.uf) ? "  ●" : ""));
  });
  if (k === "lula_2T_pct_validos") svg.append("line").attr("x1", x(50)).attr("x2", x(50)).attr("y1", 0).attr("y2", H - 22).attr("stroke", C.tinta3).attr("stroke-dasharray", "4 3");
}

/* ---------------- COMPARECIMENTO ---------------- */
const FAIXAS = ["b ≥ +20 pp", "b +10 a +20", "b 0 a +10", "a 0 a +10", "a +10 a +20", "a ≥ +20 pp"];
function rotFaixa(f, ano) {
  const [a, b] = NOMES[ano];
  return ({ "b ≥ +20 pp": `${b} +20 ou mais`, "b +10 a +20": `${b} +10 a +20`, "b 0 a +10": `${b} 0 a +10`,
    "a 0 a +10": `${a} 0 a +10`, "a +10 a +20": `${a} +10 a +20`, "a ≥ +20 pp": `${a} +20 ou mais` })[f];
}
let anoComp = 2026, dispSel = "dV|dL";
function barrasAgrupadas(el, grupos, series, opt = {}) {
  /* grupos: [{rot, cor}] ; series: [{chave, rot, cor(g), valores[]}] */
  const W = larg(el), H = opt.alt ?? 280, mB = 64, mT = 14, mL = 40;
  const vals = series.flatMap(s => s.valores);
  const y = d3.scaleLinear().domain([Math.min(0, d3.min(vals)), Math.max(0, d3.max(vals))]).nice().range([H - mB, mT]);
  const x0 = d3.scaleBand().domain(grupos.map((g, i) => i)).range([mL, W - 6]).padding(.22);
  const x1 = d3.scaleBand().domain(series.map((s, i) => i)).range([0, x0.bandwidth()]).padding(.08);
  const svg = d3.select(el).html("").append("svg").attr("viewBox", `0 0 ${W} ${H}`);
  svg.append("g").attr("class", "grade").attr("transform", `translate(${mL},0)`).call(d3.axisLeft(y).ticks(5).tickSize(-(W - mL - 6)).tickFormat("")).select(".domain").remove();
  svg.append("g").attr("class", "eixo").attr("transform", `translate(${mL},0)`).call(d3.axisLeft(y).ticks(5).tickFormat(t => fNum(t, 0)));
  svg.append("line").attr("x1", mL).attr("x2", W - 6).attr("y1", y(0)).attr("y2", y(0)).attr("stroke", C.tinta3);
  grupos.forEach((g, gi) => {
    series.forEach((s, si) => {
      const v = s.valores[gi], xx = x0(gi) + x1(si);
      svg.append("rect").attr("x", xx).attr("width", x1.bandwidth()).attr("y", Math.min(y(0), y(v))).attr("height", Math.max(1, Math.abs(y(v) - y(0)))).attr("rx", 2)
        .attr("fill", typeof s.cor === "function" ? s.cor(g, gi) : s.cor)
        .on("mousemove", ev => mostrarDica(`<b>${g.rot}</b><br>${s.rot}: <span class="mono">${opt.fmt ? opt.fmt(v) : fNum(v, 2)}</span>`, ev)).on("mouseleave", esconderDica);
    });
    const t = svg.append("text").attr("class", "rot-medio").attr("text-anchor", "middle").attr("x", x0(gi) + x0.bandwidth() / 2).attr("y", H - mB + 16).style("font-size", "11px");
    const l1 = g.l1 ?? g.rot, l2 = g.l2 ?? "";
    t.append("tspan").attr("x", x0(gi) + x0.bandwidth() / 2).attr("dy", 0).attr("fill", g.cor).style("font-weight", 700).text(l1);
    t.append("tspan").attr("x", x0(gi) + x0.bandwidth() / 2).attr("dy", 14).text(l2);
  });
  if (opt.rotY) svg.append("text").attr("class", "rot").attr("x", mL).attr("y", mT - 4).text(opt.rotY);
}
renderizar.comparecimento = function () {
  segmentado($("#seg-ano-comp"), [[2026, "2026"], [2022, "2022"], [2018, "2018"]], anoComp, v => { anoComp = v; desenharFaixas(); });
  desenharFaixas();
  const PRE = { "dV|dL": ["Votos válidos: variação por 100 aptos", "Lula: votos a mais por 100 aptos"], "dV|dF": ["Votos válidos: variação por 100 aptos", "Flávio: votos a mais por 100 aptos"],
    "o1|dL": ["Eliminados no 1º turno (% dos válidos)", "Lula: votos a mais por 100 aptos"], "o1|dF": ["Eliminados no 1º turno (% dos válidos)", "Flávio: votos a mais por 100 aptos"],
    "mar|dV": ["Margem Lula − Flávio no 1º turno (p.p.)", "Votos válidos: variação por 100 aptos"], "dBN|dL": ["Brancos e nulos: variação por 100 aptos", "Lula: votos a mais por 100 aptos"] };
  const sd = $("#sel-disp");
  if (!sd.options.length) {
    sd.innerHTML = Object.entries(PRE).map(([k, v]) => `<option value="${k}">${v[1]} × ${v[0]}</option>`).join("");
    sd.addEventListener("change", () => { dispSel = sd.value; dispersao(PRE); });
  }
  sd.value = dispSel; dispersao(PRE);
  bnRegiao();
};
function desenharFaixas() {
  const f = D.faixas.filter(x => x.ano === anoComp && x.nivel === "secao");
  const por = Object.fromEntries(f.map(x => [x.faixa, x]));
  const grupos = FAIXAS.map(k => {
    const rot = rotFaixa(k, anoComp), nome = NOMES[anoComp][k.startsWith("a") ? 0 : 1];
    return { rot, l1: nome, l2: rot.slice(nome.length + 1), cor: k.startsWith("a") ? C.lula : C.dir, k };
  });
  barrasAgrupadas($("#g-faixas"), grupos, [
    { rot: "% dos eleitores do país", cor: g => g.k.startsWith("a") ? C.lulaC : C.dirC, valores: FAIXAS.map(k => por[k].pct_aptos) },
    { rot: "% do aumento de votos válidos", cor: g => g.k.startsWith("a") ? C.lula : C.dir, valores: FAIXAS.map(k => por[k].pct_dV_nacional) },
  ], { fmt: v => fPct(v, 1), rotY: "% do total nacional" });
  barrasAgrupadas($("#g-faixas2"), grupos, [
    { rot: "Votos válidos", cor: C.verde, valores: FAIXAS.map(k => por[k].dV_por_100_aptos) },
    { rot: "Comparecimento", cor: C.realce, valores: FAIXAS.map(k => por[k].dC_por_100_aptos) },
    { rot: "Brancos e nulos", cor: C.bn, valores: FAIXAS.map(k => por[k].dBN_por_100_aptos) },
  ], { fmt: v => fSin(v, 2), rotY: "por 100 eleitores aptos" });
  legenda($("#leg-faixas2"), [[C.verde, "Votos válidos"], [C.realce, "Comparecimento"], [C.bn, "Brancos e nulos"]]);
}
function dispersao(PRE) {
  const [kx, ky] = dispSel.split("|"), [rx, ry] = PRE[dispSel];
  const pts = MUN.map(m => ({ m, x: kx === "mar" ? m.l1 - m.f1 : m[kx], y: m[ky], w: m.aptos })).filter(p => p.x != null && p.y != null);
  const q = (arr, p) => d3.quantile(arr.slice().sort(d3.ascending), p);
  const xs = pts.map(p => p.x), ys = pts.map(p => p.y);
  const el = $("#g-disp"), W = larg(el), H = Math.min(520, Math.max(320, W * .6)), m = { l: 46, r: 10, t: 10, b: 40 };
  const x = d3.scaleLinear().domain([q(xs, .005), q(xs, .995)]).nice().range([m.l, W - m.r]);
  const y = d3.scaleLinear().domain([q(ys, .005), q(ys, .995)]).nice().range([H - m.b, m.t]);
  const r = d3.scaleSqrt().domain([0, d3.max(pts, p => p.w)]).range([1.2, 16]);
  el.innerHTML = "";
  const dpr = window.devicePixelRatio || 1;
  const cv = document.createElement("canvas"); cv.width = W * dpr; cv.height = H * dpr; cv.style.height = H + "px"; el.appendChild(cv);
  const ctx = cv.getContext("2d"); ctx.scale(dpr, dpr);
  const svg = d3.select(el).append("svg").attr("viewBox", `0 0 ${W} ${H}`).style("position", "absolute").style("left", 0).style("top", 0);
  svg.append("g").attr("class", "grade").attr("transform", `translate(${m.l},0)`).call(d3.axisLeft(y).ticks(6).tickSize(-(W - m.l - m.r)).tickFormat("")).select(".domain").remove();
  svg.append("g").attr("class", "eixo").attr("transform", `translate(0,${H - m.b})`).call(d3.axisBottom(x).ticks(7));
  svg.append("g").attr("class", "eixo").attr("transform", `translate(${m.l},0)`).call(d3.axisLeft(y).ticks(6));
  svg.append("text").attr("class", "rot-medio").attr("x", W - m.r).attr("y", H - 6).attr("text-anchor", "end").text(rx);
  svg.append("text").attr("class", "rot-medio").attr("x", m.l + 6).attr("y", m.t + 12).text(ry);
  const visiveis = pts.filter(p => p.x >= x.domain()[0] && p.x <= x.domain()[1] && p.y >= y.domain()[0] && p.y <= y.domain()[1]).sort((a, b) => b.w - a.w);
  visiveis.forEach(p => {
    ctx.beginPath(); ctx.arc(x(p.x), y(p.y), r(p.w), 0, 2 * Math.PI);
    ctx.fillStyle = d3.color(p.m.l1 >= p.m.f1 ? C.lula : C.dir).copy({ opacity: .35 }) + ""; ctx.fill();
  });
  // tendência ponderada
  const sw = d3.sum(pts, p => p.w), mx = d3.sum(pts, p => p.w * p.x) / sw, my = d3.sum(pts, p => p.w * p.y) / sw;
  const sxy = d3.sum(pts, p => p.w * (p.x - mx) * (p.y - my)), sxx = d3.sum(pts, p => p.w * (p.x - mx) ** 2), syy = d3.sum(pts, p => p.w * (p.y - my) ** 2);
  const b = sxy / sxx, a = my - b * mx, corr = sxy / Math.sqrt(sxx * syy);
  const [d0, d1] = x.domain();
  svg.append("line").attr("x1", x(d0)).attr("x2", x(d1)).attr("y1", y(a + b * d0)).attr("y2", y(a + b * d1)).attr("stroke", C.tinta).attr("stroke-width", 2)
    .attr("clip-path", null);
  $("#disp-legenda").innerHTML = `Correlação ponderada pelo eleitorado: <b class="mono">${fNum(corr, 2)}</b> · inclinação da reta: <b class="mono">${fNum(b, 2)}</b>. Correlação mostra que as duas coisas variam juntas entre lugares; não mostra causa.`;
  const qt = d3.quadtree().x(p => x(p.x)).y(p => y(p.y)).addAll(visiveis);
  svg.on("mousemove", ev => {
    const [px, py] = d3.pointer(ev, svg.node());
    const sx = W / svg.node().getBoundingClientRect().width;
    const p = qt.find(px, py, 14 * sx);
    if (!p) return esconderDica();
    mostrarDica(`<b>${esc(p.m.nome)} · ${p.m.uf}</b><br>${rx}: <span class="mono">${fNum(p.x, 2)}</span><br>${ry}: <span class="mono">${fNum(p.y, 2)}</span><br>Eleitores: ${fInt(p.w)}`, ev);
  }).on("mouseleave", esconderDica);
}
function bnRegiao() {
  const el = $("#g-bn"), W = larg(el), anos = [2026, 2022, 2018], regs = ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"];
  const painel = Math.max(220, (W - 20) / 3), colunas = Math.max(1, Math.floor(W / painel)), linhas = Math.ceil(3 / colunas);
  const pw = W / colunas, ph = 190, H = linhas * ph;
  const svg = d3.select(el).html("").append("svg").attr("viewBox", `0 0 ${W} ${H}`);
  const x = d3.scaleLinear().domain([0, 13]).range([90, pw - 16]);
  anos.forEach((ano, i) => {
    const g = svg.append("g").attr("transform", `translate(${(i % colunas) * pw},${Math.floor(i / colunas) * ph})`);
    g.append("text").attr("class", "rot-forte").attr("x", 0).attr("y", 14).style("font-size", "14px").text(ano);
    g.append("g").attr("class", "eixo").attr("transform", `translate(0,${ph - 30})`).call(d3.axisBottom(x).ticks(4).tickFormat(t => t + "%"));
    regs.forEach((rg, j) => {
      const d = D.bn_regiao.find(b => b.ano === ano && b.regiao === rg), yy = 34 + j * 26;
      const cor = d.bn2 < d.bn1 ? C.verde : C.roxo;
      g.append("text").attr("class", "rot-medio").attr("x", 84).attr("y", yy + 4).attr("text-anchor", "end").text(rg);
      g.append("line").attr("x1", x(d.bn1)).attr("x2", x(d.bn2)).attr("y1", yy).attr("y2", yy).attr("stroke", cor).attr("stroke-width", 3);
      g.append("circle").attr("cx", x(d.bn1)).attr("cy", yy).attr("r", 4).attr("fill", C.papel).attr("stroke", cor).attr("stroke-width", 2);
      g.append("circle").attr("cx", x(d.bn2)).attr("cy", yy).attr("r", 5).attr("fill", cor)
        .on("mousemove", ev => mostrarDica(`<b>${rg} · ${ano}</b><br>Brancos e nulos: ${fPct(d.bn1, 2)} no 1º turno → ${fPct(d.bn2, 2)} no 2º`, ev)).on("mouseleave", esconderDica);
    });
  });
  svg.append("text").attr("class", "rot").attr("x", W - 4).attr("y", H - 4).attr("text-anchor", "end").text("○ 1º turno  ● 2º turno · verde: caiu · roxo: subiu");
}

/* ---------------- TRANSFERÊNCIAS ---------------- */
let anoTr = 2026, nivelTr = "secao", soMudou = false, celulaSel = "b_1|a_2";
renderizar.transferencias = function () {
  segmentado($("#seg-ano-tr"), [[2026, "2026"], [2022, "2022"], [2018, "2018"]], anoTr, v => { anoTr = v; desenharTransf(); });
  segmentado($("#seg-nivel-tr"), [["secao", "Seções"], ["municipio", "Municípios"]], nivelTr, v => { nivelTr = v; desenharTransf(); });
  const ch = $("#chk-mudou"); ch.checked = soMudou; ch.onchange = () => { soMudou = ch.checked; sankey(); };
  const sc = $("#sel-celula");
  if (!sc.options.length) {
    sc.innerHTML = [["b_1|a_2", "Eleitores de Flávio que votaram em Lula"], ["a_1|b_2", "Eleitores de Lula que votaram em Flávio"],
      ["bn_1|a_2", "Brancos e nulos do 1º turno que votaram em Lula"], ["bn_1|b_2", "Brancos e nulos do 1º turno que votaram em Flávio"],
      ["abst_1|a_2", "Quem não votou no 1º turno e votou em Lula"], ["abst_1|b_2", "Quem não votou no 1º turno e votou em Flávio"],
      ["o_1|a_2", "Eleitores dos eliminados que votaram em Lula"], ["o_1|b_2", "Eleitores dos eliminados que votaram em Flávio"]]
      .map(([k, v]) => `<option value="${k}">${v}</option>`).join("");
    sc.addEventListener("change", () => { celulaSel = sc.value; modelos(); });
  }
  sc.value = celulaSel;
  desenharTransf(); eliminados(); modelos();
};
function desenharTransf() { sankey(); matrizCalor(); }
function sankey() {
  const mm = matriz(anoTr, nivelTr);
  const fluxos = mm.filter(f => !(soMudou && f.origem.split("_")[0] === f.destino.split("_")[0]));
  const el = $("#g-sankey"), W = larg(el), H = Math.min(560, Math.max(380, W * .5)), pad = 12, nw = 14;
  const estreito = W < 600;  // celular: nomes abreviados e nome + valor numa linha
  const mE = estreito ? W * .3 : Math.min(150, W * .26), mD = mE;
  const nomeNo = (cod) => { const n = nomeCat(cod, anoTr); return estreito ? ({ "Brancos e nulos": "Br./nulos", "Abstenção": "Abst.", "Eliminados": "Elimin." })[n] || n : n; };
  const totO = ORIG.map(o => d3.sum(fluxos.filter(f => f.origem === o), f => f.votos));
  const totD = DEST.map(d => d3.sum(fluxos.filter(f => f.destino === d), f => f.votos));
  const tot = d3.sum(totO), k = (H - 20 - pad * (ORIG.length - 1)) / tot, kD = (H - 20 - pad * (DEST.length - 1)) / d3.sum(totD);
  const kk = Math.min(k, kD);
  const posO = [], posD = []; let y = 10;
  totO.forEach(t => { posO.push(y); y += t * kk + pad; });
  y = 10; totD.forEach(t => { posD.push(y); y += t * kk + pad; });
  const svg = d3.select(el).html("").append("svg").attr("viewBox", `0 0 ${W} ${H}`);
  const xl = mE, xr = W - mD - nw;
  const offO = posO.slice(), offD = posD.slice();
  const ordem = fluxos.slice().sort((a, b) => ORIG.indexOf(a.origem) - ORIG.indexOf(b.origem) || DEST.indexOf(a.destino) - DEST.indexOf(b.destino));
  const gl = svg.append("g");
  ordem.forEach(f => {
    const i = ORIG.indexOf(f.origem), j = DEST.indexOf(f.destino), h = f.votos * kk;
    const y0 = offO[i], y1 = offD[j]; offO[i] += h; offD[j] += h;
    if (h < 0.15) return;
    const xm = (xl + nw + xr) / 2;
    const path = `M${xl + nw},${y0} C${xm},${y0} ${xm},${y1} ${xr},${y1} L${xr},${y1 + h} C${xm},${y1 + h} ${xm},${y0 + h} ${xl + nw},${y0 + h} Z`;
    gl.append("path").attr("d", path).attr("fill", corCat(f.origem)).attr("fill-opacity", .38)
      .on("mousemove", function (ev) {
        d3.select(this).attr("fill-opacity", .7);
        mostrarDica(`<b>${nomeCat(f.origem, anoTr)} (1º) → ${nomeCat(f.destino, anoTr)} (2º)</b><br><span class="mono">${fInt(f.votos)}</span> eleitores<br>${fPct(100 * f.taxa, 2)} do grupo de origem<br>intervalo de 95%: ${fPct(100 * f.taxa_ic95_inf, 2)} a ${fPct(100 * f.taxa_ic95_sup, 2)}`, ev);
      })
      .on("mouseleave", function () { d3.select(this).attr("fill-opacity", .38); esconderDica(); });
  });
  ORIG.forEach((o, i) => {
    if (totO[i] * kk < 0.5) return;
    svg.append("rect").attr("x", xl).attr("y", posO[i]).attr("width", nw).attr("height", Math.max(1, totO[i] * kk)).attr("fill", corCat(o));
    rotuloNo(svg, xl - 6, posO[i], estreito ? 0 : totO[i] * kk, nomeNo(o), fMi(totO[i], 1), "end", totO[i] * kk);
  });
  DEST.forEach((d, j) => {
    if (totD[j] * kk < 0.5) return;
    svg.append("rect").attr("x", xr).attr("y", posD[j]).attr("width", nw).attr("height", Math.max(1, totD[j] * kk)).attr("fill", corCat(d));
    rotuloNo(svg, xr + nw + 6, posD[j], estreito ? 0 : totD[j] * kk, nomeNo(d), fMi(totD[j], 1), "start", totD[j] * kk);
  });
  svg.append("text").attr("class", "rot").attr("x", xl).attr("y", H - 2).text("1º turno");
  svg.append("text").attr("class", "rot").attr("x", xr + nw).attr("y", H - 2).attr("text-anchor", "end").text("2º turno");
}
function rotuloNo(svg, x, y0, h, nome, valor, ancora, hReal = h) {
  // nós baixos (ou tela estreita, h = 0): nome e valor na mesma linha, centrados no nó
  if (h < 30) {
    svg.append("text").attr("class", "rot-forte").attr("x", x).attr("y", y0 + hReal / 2 + 4).attr("text-anchor", ancora)
      .style("font-size", h === 0 ? "11px" : null).text(`${nome} · ${valor}`);
  } else {
    svg.append("text").attr("class", "rot-forte").attr("x", x).attr("y", y0 + h / 2).attr("text-anchor", ancora).text(nome);
    svg.append("text").attr("class", "rot").attr("x", x).attr("y", y0 + h / 2 + 14).attr("text-anchor", ancora).text(valor);
  }
}
function matrizCalor() {
  const mm = matriz(anoTr, nivelTr), el = $("#g-matriz"), W = larg(el);
  const estreito = W < 520;  // celular: nomes curtos; intervalo só na dica
  const curto = c => estreito ? ({ "Brancos e nulos": "Br./nulos", "Abstenção": "Abst.", "Eliminados": "Elimin.", "J. Bolsonaro": "J. Bols." })[nomeCat(c, anoTr)] || nomeCat(c, anoTr) : nomeCat(c, anoTr);
  const mE = estreito ? 70 : 120, mT = 34, cw = (W - mE - 4) / 4, ch = estreito ? 40 : 52, H = mT + ch * 5 + 4;
  const svg = d3.select(el).html("").append("svg").attr("viewBox", `0 0 ${W} ${H}`);
  DEST.forEach((d, j) => svg.append("text").attr("class", "rot-forte").attr("x", mE + j * cw + cw / 2).attr("y", 14).attr("text-anchor", "middle").text(curto(d)));
  svg.append("text").attr("class", "rot").attr("x", mE + 2 * cw).attr("y", 28).attr("text-anchor", "middle").text("2º turno →");
  ORIG.forEach((o, i) => {
    svg.append("text").attr("class", "rot-forte").attr("x", mE - 8).attr("y", mT + i * ch + ch / 2 + 4).attr("text-anchor", "end").text(curto(o));
    DEST.forEach((d, j) => {
      const c = mm.find(f => f.origem === o && f.destino === d);
      const a = Math.min(1, Math.sqrt(c.taxa));
      svg.append("rect").attr("x", mE + j * cw + 1).attr("y", mT + i * ch + 1).attr("width", cw - 2).attr("height", ch - 2).attr("rx", 3)
        .attr("fill", corCat(d)).attr("fill-opacity", .08 + .85 * a)
        .on("mousemove", ev => mostrarDica(`<b>${nomeCat(o, anoTr)} (1º) → ${nomeCat(d, anoTr)} (2º)</b><br>${fPct(100 * c.taxa, 2)}<br>intervalo de 95%: ${fPct(100 * c.taxa_ic95_inf, 2)} a ${fPct(100 * c.taxa_ic95_sup, 2)}`, ev))
        .on("mouseleave", esconderDica);
      const escuro = a > .6;
      svg.append("text").attr("x", mE + j * cw + cw / 2).attr("y", mT + i * ch + ch / 2 + (estreito ? 5 : -1)).attr("text-anchor", "middle").style("pointer-events", "none")
        .style("font", `500 ${estreito ? 12 : 14}px var(--f-numero)`).attr("fill", escuro && d !== "abst_2" ? "#fff" : C.tinta).text(fPct(100 * c.taxa, 1));
      if (!estreito) svg.append("text").style("pointer-events", "none").attr("x", mE + j * cw + cw / 2).attr("y", mT + i * ch + ch / 2 + 14).attr("text-anchor", "middle")
        .style("font", "11px var(--f-numero)").attr("fill", escuro && d !== "abst_2" ? "#fff" : C.tinta2).text(`${fNum(100 * c.taxa_ic95_inf, 1)}–${fNum(100 * c.taxa_ic95_sup, 1)}`);
    });
  });
}
function barras100(el, linhas, destinos, opt = {}) {
  const W = larg(el), mE = Math.min(opt.mE ?? 190, W * .4), alt = 26, gap = 10, H = linhas.length * (alt + gap) + 24;
  const x = d3.scaleLinear().domain([0, 1]).range([mE, W - 8]);
  const svg = d3.select(el).html("").append("svg").attr("viewBox", `0 0 ${W} ${H}`);
  svg.append("g").attr("class", "eixo").attr("transform", `translate(0,${H - 20})`).call(d3.axisBottom(x).ticks(5).tickFormat(t => fPct(100 * t, 0)));
  linhas.forEach((l, i) => {
    const y = i * (alt + gap); let acc = 0;
    svg.append("text").attr("class", "rot-forte").attr("x", mE - 8).attr("y", y + alt / 2 + 4).attr("text-anchor", "end").text(l.rot);
    destinos.forEach(d => {
      const c = l.celulas[d]; if (!c) return;
      const x0 = x(acc), x1 = x(acc + c.taxa); acc += c.taxa;
      svg.append("rect").attr("x", x0).attr("y", y).attr("width", Math.max(0, x1 - x0 - 1.5)).attr("height", alt).attr("fill", corCat(d))
        .on("mousemove", ev => mostrarDica(`<b>${l.rot} → ${opt.nomeDest ? opt.nomeDest(d) : nomeCat(d)}</b><br>${fPct(100 * c.taxa, 1)}${c.ic95_inf != null ? ` (intervalo de 95%: ${fPct(100 * c.ic95_inf, 1)} a ${fPct(100 * c.ic95_sup, 1)})` : ""}`, ev))
        .on("mouseleave", esconderDica);
      if (x1 - x0 > 38) svg.append("text").attr("x", x0 + 5).attr("y", y + alt / 2 + 4).style("font", "500 11px var(--f-numero)")
        .attr("fill", d.startsWith("abst") ? C.tinta : "#fff").style("pointer-events", "none").text(fPct(100 * c.taxa, 0));
    });
  });
}
function eliminados() {
  const mm = D.matrizes.filter(m => m.ano === 2026 && m.nivel === "secao" && m.origens === "detalhada");
  const linhas = ["cury_1", "renan_1", "caiado_1", "demais_1"].map(o => {
    const v = { "cury_1": " (3,45 mi)", "renan_1": " (2,68 mi)", "caiado_1": " (2,61 mi)", "demais_1": " (0,59 mi)" }[o];
    return { rot: nomeCat(o) + v, celulas: Object.fromEntries(DEST.map(d => { const c = mm.find(f => f.origem === o && f.destino === d); return [d, { taxa: c.taxa, ic95_inf: c.taxa_ic95_inf, ic95_sup: c.taxa_ic95_sup }]; })) };
  });
  barras100($("#g-elim"), linhas, DEST);
  legenda($("#leg-elim"), [[C.lula, "Lula"], [C.dir, "Flávio"], [C.bn, "Branco ou nulo"], [C.abst, "Não votou"]]);
}
function modelos() {
  const [o, d] = celulaSel.split("|");
  const pega = (ano, nivel) => D.matrizes.find(m => m.ano === ano && m.nivel === nivel && m.origens === "base" && m.origem === o && m.destino === d);
  const sens = n => D.sensibilidade.find(s => s.ano === 2026 && s.estratificacao === n && s.origem === o && s.destino === d);
  const bay = p => D.bayes.find(b => b.prior === p && b.origem === o && b.destino === d);
  const a1 = pega(2026, "secao"), a2 = pega(2026, "municipio");
  const lin = [
    ["Modelo A · seções (principal)", a1.taxa, a1.taxa_ic95_inf, a1.taxa_ic95_sup],
    ["Modelo A · municípios", a2.taxa, a2.taxa_ic95_inf, a2.taxa_ic95_sup],
    ["Modelo A · região × vantagem", sens("região × faixa de margem").taxa],
    ["Modelo A · estado × urbanização", sens("UF × tercil de urbanização").taxa],
    ["Modelo A · municípios grandes", sens("município grande ou UF").taxa],
    ["Modelo B · prior neutra", bay("neutra").media, bay("neutra").ic95_inf, bay("neutra").ic95_sup],
    ["Modelo B · prior fidelidade alta", bay("fidelidade_alta").media, bay("fidelidade_alta").ic95_inf, bay("fidelidade_alta").ic95_sup],
    ["Modelo B · prior troca alta (15%)", bay("troca_alta").media, bay("troca_alta").ic95_inf, bay("troca_alta").ic95_sup],
  ];
  const el = $("#g-modelos"), W = larg(el), mE = Math.min(240, W * .45), alt = 30, H = lin.length * alt + 34;
  const max = d3.max(lin, l => l[3] ?? l[1]) * 1.15 || 0.01;
  const x = d3.scaleLinear().domain([0, max]).nice().range([mE, W - 60]);
  const svg = d3.select(el).html("").append("svg").attr("viewBox", `0 0 ${W} ${H}`);
  svg.append("g").attr("class", "grade").attr("transform", `translate(0,${H - 24})`).call(d3.axisBottom(x).ticks(6).tickSize(-(H - 30)).tickFormat("")).select(".domain").remove();
  svg.append("g").attr("class", "eixo").attr("transform", `translate(0,${H - 24})`).call(d3.axisBottom(x).ticks(6).tickFormat(t => fPct(100 * t, max < .05 ? 1 : 0)));
  const cor = corCat(d);
  lin.forEach((l, i) => {
    const y = 8 + i * alt;
    svg.append("text").attr("class", "rot-medio").attr("x", mE - 8).attr("y", y + 4).attr("text-anchor", "end").text(l[0]);
    if (l[2] != null) svg.append("line").attr("x1", x(l[2])).attr("x2", x(l[3])).attr("y1", y).attr("y2", y).attr("stroke", cor).attr("stroke-width", 3).attr("stroke-linecap", "round");
    svg.append("circle").attr("cx", x(l[1])).attr("cy", y).attr("r", 6).attr("fill", cor).attr("stroke", C.papel).attr("stroke-width", 2)
      .on("mousemove", ev => mostrarDica(`<b>${l[0]}</b><br>${fPct(100 * l[1], 2)}${l[2] != null ? `<br>intervalo: ${fPct(100 * l[2], 2)} a ${fPct(100 * l[3], 2)}` : ""}`, ev)).on("mouseleave", esconderDica);
    svg.append("text").attr("class", "rot").attr("x", x(l[3] ?? l[1]) + 10).attr("y", y + 4).text(fPct(100 * l[1], 2));
  });
}

/* ---------------- MIGRAÇÃO ---------------- */
let sentido = "direita_para_pt", teto = 0, mcVis = "dev";
renderizar.migracao = function () {
  segmentado($("#seg-sentido"), [["direita_para_pt", "Direita → PT"], ["pt_para_direita", "PT → direita"]], sentido, v => { sentido = v; desenharTestes(); });
  segmentado($("#seg-teto"), [[0, "0%"], [0.01, "1%"], [0.02, "2%"], [0.05, "5%"], [0.1, "10%"]], teto, v => { teto = v; desenharTestes(); });
  desenharTestes();
  const ap = D.testes.amapa;
  const linhaAp = n => { const r0 = ap.find(a => a.conjunto === n && a.teto === 0), r5 = ap.find(a => a.conjunto === n && a.teto === 0.05);
    return [n, fInt(r0.secoes), `${fPct(100 * r0.taxa_FL_livre, 1)} <span class="nota">(${fNum(100 * r0.taxa_FL_ic95_inf_boot_secao, 1)}–${fNum(100 * r0.taxa_FL_ic95_sup_boot_secao, 1)})</span>`,
      fPct(100 * r0.taxa_L_abst, 0), fPct(100 * r0.taxa_F_abst, 0), fP(r0.p), fP(r5.p)]; };
  tabela($("#tab-amapa"), ["Conjunto", "Seções", "Troca Flávio→Lula estimada", "Lula → não votou", "Flávio → não votou", "p (limite 0%)", "p (limite 5%)"],
    ["Amapá (todas as seções)", "Macapá e Santana", "interior"].map(linhaAp), ["", "num", "num", "num", "num", "num", "num"]);
  segmentado($("#seg-mc"), [["dev", "Erro de ajuste"], ["FL", "Troca Flávio→Lula"], ["erro", "Erro antes do ajuste"]], mcVis, v => { mcVis = v; monteCarlo(); });
  monteCarlo();
  $("#mc-defs").innerHTML = Object.entries(D.monte_carlo.definicoes).map(([k, v]) => `<p><b>${k.split("_")[0]}</b> ${esc(v.descricao)}.</p>`).join("") +
    `<p>A fração de sorteios com bom ajuste depende da largura escolhida para cada cenário. Por isso ela não é a probabilidade de o cenário ser verdadeiro.</p>`;
};
function desenharTestes() {
  const nomesSent = { direita_para_pt: a => `${NOMES_LONGOS[a][1]} → ${NOMES_LONGOS[a][0]}`, pt_para_direita: a => `${NOMES_LONGOS[a][0]} → ${NOMES_LONGOS[a][1]}` };
  $("#cartoes-teste").innerHTML = [2026, 2022, 2018].map(ano => {
    const r = n => D.testes.conjunto.find(t => t.ano === ano && t.nivel === n && t.hipotese === sentido && Math.abs(t.teto - teto) < 1e-9);
    const s = r("secao"), m = r("municipio");
    const pill = p => p < 0.05 ? `<span class="pill nao">incompatível</span>` : `<span class="pill ok">compatível</span>`;
    return `<div class="bloco"><div class="cab-bloco"><h3>${ano}</h3><span class="natureza estimativa">Estimativa</span></div>
      <p class="nota">${nomesSent[sentido](ano)}, no máximo ${fPct(100 * teto, 0)}</p>
      <div class="ficha"><dl><dt>Seções: valor-p</dt><dd>${fP(s.p_conjunto)} ${pill(s.p_conjunto)}</dd>
      <dt>Municípios: valor-p</dt><dd>${fP(m.p_conjunto)} ${pill(m.p_conjunto)}</dd>
      <dt>Estados que rejeitam (corrigido)</dt><dd>${s.ufs_rejeitadas_bonferroni}</dd></dl></div>
      ${s.ufs_rejeitadas_bonferroni ? `<p class="nota">Maior incompatibilidade: ${esc(s.ufs_maior_incompatibilidade.split(",")[0])}</p>` : ""}</div>`;
  }).join("");
  const dados = D.testes.por_uf.filter(t => t.nivel === "secao" && t.hipotese === sentido && Math.abs(t.teto - teto) < 1e-9).sort((a, b) => b.F - a.F);
  const el = $("#g-teste-uf"), W = larg(el), H = 240, mL = 40, mB = 40;
  const x = d3.scaleBand().domain(dados.map(d => d.uf)).range([mL, W - 6]).padding(.18);
  const maxF = Math.max(12, d3.max(dados, d => d.F));
  const y = d3.scaleSymlog().constant(1).domain([0, maxF]).range([H - mB, 10]);
  const svg = d3.select(el).html("").append("svg").attr("viewBox", `0 0 ${W} ${H}`);
  svg.append("g").attr("class", "eixo").attr("transform", `translate(${mL},0)`).call(d3.axisLeft(y).tickValues([0, 1, 3.84, 9.6, 30, 100].filter(v => v <= maxF)).tickFormat(t => fNum(t, t < 10 && t % 1 ? 1 : 0)));
  svg.append("g").attr("class", "eixo").attr("transform", `translate(0,${H - mB})`).call(d3.axisBottom(x)).selectAll("text").style("font-size", "10px");
  const cor = sentido === "direita_para_pt" ? C.lula : C.dir;
  dados.forEach(d => svg.append("rect").attr("x", x(d.uf)).attr("width", x.bandwidth()).attr("y", y(d.F)).attr("height", Math.max(0, y(0) - y(d.F))).attr("rx", 2)
    .attr("fill", d.F > 9.6 ? cor : C.linhaF)
    .on("mousemove", ev => mostrarDica(`<b>${d.uf}</b><br>Taxa estimada sem limite: ${fPct(100 * d.taxa_livre, 2)}<br>F = ${fNum(d.F, 1)} · p = ${fP(d.p)}`, ev)).on("mouseleave", esconderDica));
  [[3.84, "4 3", "p = 0,05 (um estado)"], [9.6, null, "p = 0,05 corrigido para 27 estados"]].forEach(([v, dash, rot]) => {
    svg.append("line").attr("x1", mL).attr("x2", W - 6).attr("y1", y(v)).attr("y2", y(v)).attr("stroke", C.tinta2).attr("stroke-dasharray", dash);
    svg.append("text").attr("class", "rot").attr("x", W - 8).attr("y", y(v) - 4).attr("text-anchor", "end").text(rot);
  });
}
function monteCarlo() {
  const F = D.monte_carlo.familias, nomes = Object.keys(F), cs = [C.tinta, C.roxo, C.outros, C.verde];
  const el = $("#g-mc"), W = larg(el), H = 260, m = { l: 12, r: 10, t: 10, b: 40 };
  const h0 = F[nomes[0]][mcVis];
  const x = d3.scaleLinear().domain([h0.bordas[0], h0.bordas[h0.bordas.length - 1]]).range([m.l, W - m.r]);
  const dens = nomes.map(n => { const h = F[n][mcVis], tot = d3.sum(h.contagens); return h.contagens.map((c, i) => [(h.bordas[i] + h.bordas[i + 1]) / 2, c / tot]); });
  const y = d3.scaleLinear().domain([0, d3.max(dens.flat(), d => d[1])]).range([H - m.b, m.t]);
  const svg = d3.select(el).html("").append("svg").attr("viewBox", `0 0 ${W} ${H}`);
  const rotX = { dev: "erro de ajuste aos municípios (deviance por 1.000 eleitores; menor = melhor)", FL: "taxa Flávio → Lula depois do ajuste aos totais oficiais (%)", erro: "erro no total de Lula antes do ajuste (pontos percentuais dos aptos)" }[mcVis];
  svg.append("g").attr("class", "eixo").attr("transform", `translate(0,${H - m.b})`).call(d3.axisBottom(x).ticks(7));
  svg.append("text").attr("class", "rot-medio").attr("x", W - m.r).attr("y", H - 4).attr("text-anchor", "end").text(rotX);
  if (mcVis === "dev") { svg.append("line").attr("x1", x(D.monte_carlo.dev_ref)).attr("x2", x(D.monte_carlo.dev_ref)).attr("y1", m.t).attr("y2", H - m.b).attr("stroke", C.tinta3).attr("stroke-dasharray", "4 3");
    svg.append("text").attr("class", "rot").attr("x", x(D.monte_carlo.dev_ref) + 4).attr("y", m.t + 10).text("melhor ajuste com uma tabela única"); }
  if (mcVis === "erro") svg.append("line").attr("x1", x(0)).attr("x2", x(0)).attr("y1", m.t).attr("y2", H - m.b).attr("stroke", C.tinta3);
  dens.forEach((d, i) => svg.append("path").attr("d", d3.line().x(p => x(p[0])).y(p => y(p[1])).curve(d3.curveStepAfter)(d)).attr("fill", "none").attr("stroke", cs[i]).attr("stroke-width", 2));
  legenda($("#leg-mc"), nomes.map((n, i) => [cs[i], ({ C1: "C1 fidelidade alta", C2: "C2 fidelidade alta + mobilização", C3: "C3 trocas moderadas (~6%)", C4: "C4 diferenças regionais" })[n.split("_")[0]], "height:3px"]));
}

/* ---------------- LEGISLATIVO ---------------- */
let casa = 6, splitT = 2, hexV = "flavio";
const BLOCOS = { dep_pl: "PL", dep_dir_outros: "Outros partidos de direita", dep_centro: "Partidos de centro", dep_fe_brasil: "Federação PT, PCdoB, PV",
  dep_esq_outros: "Outros partidos de esquerda", dep_bn: "Branco/nulo/não votou p/ deputado", abst_1x: "Não votou no 1º turno" };
renderizar.legislativo = function () {
  segmentado($("#seg-casa"), [[6, "Câmara"], [5, "Senado"]], casa, v => { casa = v; cadeiras(); });
  segmentado($("#seg-split"), [[1, "Presidente no 1º turno"], [2, "Presidente no 2º turno"]], splitT, v => { splitT = v; split(); });
  segmentado($("#seg-hex"), [["flavio", "Flávio"], ["lula", "Lula"]], hexV, v => { hexV = v; hex(); });
  cadeiras(); razao(); split(); hex();
};
function cadeiras() {
  const c = D.legislativo.cadeiras.filter(x => x.cargo === casa).sort((a, b) => b.votos - a.votos).slice(0, 12);
  const el = $("#g-cadeiras"), W = larg(el), mE = 110, alt = 10, gap = 12, H = c.length * (2 * alt + gap) + 24;
  const x = d3.scaleLinear().domain([0, d3.max(c, d => Math.max(d.pct_votos, d.pct_cadeiras))]).nice().range([mE, W - 40]);
  const svg = d3.select(el).html("").append("svg").attr("viewBox", `0 0 ${W} ${H}`);
  svg.append("g").attr("class", "eixo").attr("transform", `translate(0,${H - 20})`).call(d3.axisBottom(x).ticks(5).tickFormat(t => t + "%"));
  c.forEach((d, i) => {
    const y = i * (2 * alt + gap), cor = d.partido === 22 ? C.dir : d.partido === 13 ? C.lula : C.tinta2, corC = d.partido === 22 ? C.dirC : d.partido === 13 ? C.lulaC : C.linhaF;
    svg.append("text").attr("class", "rot-forte").attr("x", mE - 8).attr("y", y + alt + 4).attr("text-anchor", "end").text(d.sigla);
    const dic = ev => mostrarDica(`<b>${d.sigla}</b><br>Votos: ${fInt(d.votos)} (${fPct(d.pct_votos)})<br>Eleitos: ${d.eleitos} (${fPct(d.pct_cadeiras)})`, ev);
    svg.append("rect").attr("x", mE).attr("y", y).attr("height", alt).attr("width", x(d.pct_votos) - mE).attr("fill", corC).attr("rx", 2).on("mousemove", dic).on("mouseleave", esconderDica);
    svg.append("rect").attr("x", mE).attr("y", y + alt + 1).attr("height", alt).attr("width", x(d.pct_cadeiras) - mE).attr("fill", cor).attr("rx", 2).on("mousemove", dic).on("mouseleave", esconderDica);
    svg.append("text").attr("class", "rot").attr("x", x(Math.max(d.pct_votos, d.pct_cadeiras)) + 4).attr("y", y + alt + 4).text(`${d.eleitos} eleitos`);
  });
}
function razao() {
  const h = D.legislativo.historico.slice().sort((a, b) => a.ano - b.ano);
  const part = { 2018: "PSL", 2022: "PL", 2026: "PL" }, cand = { 2018: "Jair Bolsonaro", 2022: "Jair Bolsonaro", 2026: "Flávio Bolsonaro" };
  const grupos = h.map(d => ({ rot: `${d.ano}: ${cand[d.ano]} e ${part[d.ano]}`, l1: String(d.ano), l2: `${cand[d.ano].split(" ")[0]} / ${part[d.ano]}`, cor: C.dir }));
  barrasAgrupadas($("#g-razao"), grupos, [
    { rot: "Candidato a presidente (1º turno)", cor: C.dir, valores: h.map(d => d.pct_candidato_direita_pres_1T) },
    { rot: "Partido para deputado federal", cor: C.dirC, valores: h.map(d => d.pct_partido_dep_nacional) },
  ], { fmt: v => fPct(v, 1), rotY: "% dos votos válidos", alt: 240 });
  const svg = d3.select("#g-razao svg");
  svg.append("text").attr("class", "rot").attr("x", 44).attr("y", 236).text("Razão presidente ÷ partido: " + h.map(d => `${d.ano} ${fNum(d.razao_pres_sobre_partido, 2)}×`).join(" · "));
}
function split() {
  const nome = splitT === 1 ? "dep_federal_1T -> presidente_1T" : "dep_federal_1T -> presidente_2T (amostra)";
  const s = D.legislativo.split.filter(x => x.analise === nome);
  const dest = splitT === 1 ? ["a_1", "b_1", "o_1", "bn_1"] : DEST;
  const origens = [...new Set(s.map(x => x.origem_legislativo))];
  const linhas = origens.map(o => ({ rot: BLOCOS[o], celulas: Object.fromEntries(dest.map(d => { const c = s.find(x => x.origem_legislativo === o && x.destino_presidente === d); return [d, { taxa: c.taxa, ic95_inf: c.ic95_inf, ic95_sup: c.ic95_sup }]; })) }));
  barras100($("#g-split"), linhas, dest, { mE: 250, nomeDest: d => ({ a_1: "Lula", b_1: "Flávio", o_1: "Eliminados", bn_1: "Branco ou nulo", a_2: "Lula", b_2: "Flávio", bn_2: "Branco ou nulo", abst_2: "Não votou" })[d] });
  legenda($("#leg-split"), splitT === 1 ? [[C.lula, "Lula"], [C.dir, "Flávio"], [C.outros, "Candidatos eliminados"], [C.bn, "Branco ou nulo"]]
    : [[C.lula, "Lula"], [C.dir, "Flávio"], [C.bn, "Branco ou nulo"], [C.abst, "Não votou"]]);
}
function hex() {
  const L = D.legislativo, h = L.hist2d[hexV], nx = L.x_bordas.length - 1, ny = L.y_bordas.length - 1;
  const el = $("#g-hex"), W = Math.min(larg(el), 760), H = Math.round(W * .62), m = { l: 46, r: 10, t: 10, b: 40 };
  const x = d3.scaleLinear().domain([0, 80]).range([m.l, W - m.r]), y = d3.scaleLinear().domain([0, 100]).range([H - m.b, m.t]);
  const max = d3.max(h.flat()), cor = d3.scaleSequentialLog(d3.interpolateRgb(C.meio, hexV === "lula" ? C.lula : C.dir)).domain([1, max]);
  const svg = d3.select(el).html("").append("svg").attr("viewBox", `0 0 ${W} ${H}`).style("max-width", W + "px");
  for (let j = 0; j < ny; j++) for (let i = 0; i < nx; i++) {
    const c = h[j][i]; if (!c) continue;
    svg.append("rect").attr("x", x(L.x_bordas[i])).attr("y", y(L.y_bordas[j + 1])).attr("width", x(L.x_bordas[i + 1]) - x(L.x_bordas[i]) + .5)
      .attr("height", y(L.y_bordas[j]) - y(L.y_bordas[j + 1]) + .5).attr("fill", cor(c))
      .on("mousemove", ev => mostrarDica(`PL ${L.x_bordas[i]}–${L.x_bordas[i + 1]}% · ${hexV === "lula" ? "Lula" : "Flávio"} ${L.y_bordas[j]}–${L.y_bordas[j + 1]}%<br><span class="mono">${fInt(c)}</span> seções`, ev)).on("mouseleave", esconderDica);
  }
  svg.append("line").attr("x1", x(0)).attr("y1", y(0)).attr("x2", x(80)).attr("y2", y(80)).attr("stroke", C.tinta3).attr("stroke-dasharray", "4 3");
  svg.append("g").attr("class", "eixo").attr("transform", `translate(0,${H - m.b})`).call(d3.axisBottom(x).ticks(8).tickFormat(t => t + "%"));
  svg.append("g").attr("class", "eixo").attr("transform", `translate(${m.l},0)`).call(d3.axisLeft(y).ticks(5).tickFormat(t => t + "%"));
  svg.append("text").attr("class", "rot-medio").attr("x", W - m.r).attr("y", H - 4).attr("text-anchor", "end").text("PL para deputado federal (% dos válidos)");
  svg.append("text").attr("class", "rot-medio").attr("x", m.l + 6).attr("y", m.t + 12).text(`${hexV === "lula" ? "Lula" : "Flávio"} no 1º turno (% dos válidos)`);
  const cb = L.combinacoes.find(c => c.pl_dep_min === .3 && c.lula_1T_min === .5);
  $("#hex-legenda").innerHTML = `Cada quadrado reúne seções com valores parecidos; quanto mais escuro, mais seções (escala logarítmica). ${fInt(L.secoes)} seções com mais de 20 votos válidos. Linha tracejada: valores iguais. ` +
    (hexV === "lula" ? `Seções com PL ≥ 30% e Lula ≥ 50%: <b>${fInt(cb.secoes)}</b> (${fPct(cb.pct_secoes)}).` : `Quase todas as seções ficam acima da linha: Flávio teve mais votos que o PL em quase todo lugar.`);
}

/* ---------------- ANOMALIAS ---------------- */
renderizar.anomalias = function () {
  const A = D.anomalias, anos = [2026, 2022, 2018], cs = { 2026: C.tinta, 2022: C.roxo, 2018: C.verde };
  const el = $("#g-hist-z"), W = larg(el), H = 240, m = { l: 12, r: 10, t: 10, b: 36 };
  const x = d3.scaleLinear().domain([-8, 8]).range([m.l, W - m.r]);
  const dens = anos.map(a => { const h = A.hist[a], t = d3.sum(h.contagens); return h.contagens.map((c, i) => [(h.bordas[i] + h.bordas[i + 1]) / 2, c / t]); });
  const y = d3.scaleLinear().domain([0, d3.max(dens.flat(), d => d[1])]).range([H - m.b, m.t]);
  const svg = d3.select(el).html("").append("svg").attr("viewBox", `0 0 ${W} ${H}`);
  [-3, 3].forEach(v => { svg.append("rect").attr("x", v < 0 ? m.l : x(3)).attr("width", v < 0 ? x(-3) - m.l : W - m.r - x(3)).attr("y", m.t).attr("height", H - m.b - m.t).attr("fill", C.fundo); });
  svg.append("g").attr("class", "eixo").attr("transform", `translate(0,${H - m.b})`).call(d3.axisBottom(x).ticks(9));
  svg.append("text").attr("class", "rot-medio").attr("x", W - m.r).attr("y", H - 4).attr("text-anchor", "end").text("desvio padronizado (0 = igual ao esperado)");
  dens.forEach((d, i) => svg.append("path").attr("d", d3.line().x(p => x(p[0])).y(p => y(p[1])).curve(d3.curveMonotoneX)(d)).attr("fill", "none").attr("stroke", cs[anos[i]]).attr("stroke-width", 2));
  legenda($("#leg-hist-z"), anos.map(a => [cs[a], String(a), "height:3px"]).concat([[C.fundo, "faixa além de ±3", `border:1px solid ${C.linhaF}`]]));
  tabela($("#tab-dist"), ["", "2026", "2022", "2018"], [
    ["Municípios com desvio além de ±3", ...anos.map(a => fPct(100 * A.distribuicao.find(d => d.ano === a && d.nivel === "municipio").frac_abs_zr_gt3, 1))],
    ["Municípios sinalizados (corrigido)", ...anos.map(a => fInt(A.distribuicao.find(d => d.ano === a && d.nivel === "municipio").n_q_lula_lt_005))],
    ["Seções (amostra) com desvio além de ±3", ...anos.map(a => fPct(100 * A.distribuicao.find(d => d.ano === a && d.nivel === "secao").frac_abs_zr_gt3, 1))],
    ["I de Moran (agrupamento no mapa)", ...anos.map(a => fNum(A.moran.find(d => d.ano === a).moran_I, 2))],
  ], ["", "num", "num", "num"]);
  const diag = s => {
    if (s.uf === "DF") return "O DF é um município único; o modelo municipal usa a tabela da região Centro-Oeste, e o DF teve 2º turno para governador. Limitação do modelo, não dos dados.";
    const p = [];
    if (s.zr_pt < 0) p.push("Lula abaixo do esperado"); else p.push("Lula acima do esperado");
    if (s.dcomp_pp <= -3) p.push(`comparecimento caiu ${fNum(-s.dcomp_pp, 1)} p.p.`);
    if (s.dcomp_pp >= 3) p.push(`comparecimento subiu ${fNum(s.dcomp_pp, 1)} p.p.`);
    if (s.aptos_1 < 20000) p.push("município pequeno");
    return p.join("; ");
  };
  tabela($("#tab-sinal"), ["Município", "Eleitores", "Lula 1º → 2º turno", "Desvio", "Variação do comparecimento", "Leitura"],
    A.sinalizados.map(s => [`${esc(s.nm_municipio)} · ${s.uf}`, fInt(s.aptos_1), `${fPct(s.lula_1T_pct)} → ${fPct(s.lula_2T_pct)}`,
      `<span class="${s.zr_pt < 0 ? "cor-f" : "cor-l"} mono">${fSin(s.zr_pt, 1)}</span>`, fSin(s.dcomp_pp) + " p.p.", diag(s)]), ["", "num", "num", "num", "num", ""]);
  // urna
  const u = A.urna, eu = $("#g-urna"), Wu = larg(eu), mE = 150, Hu = u.length * 28 + 34;
  const xu = d3.scaleLinear().domain([-.35, .35]).range([mE, Wu - 10]);
  const su = d3.select(eu).html("").append("svg").attr("viewBox", `0 0 ${Wu} ${Hu}`);
  su.append("line").attr("x1", xu(0)).attr("x2", xu(0)).attr("y1", 0).attr("y2", Hu - 24).attr("stroke", C.tinta3);
  su.append("g").attr("class", "eixo").attr("transform", `translate(0,${Hu - 24})`).call(d3.axisBottom(xu).ticks(5));
  u.forEach((d, i) => {
    const y = 10 + i * 28, lo = d.coef_z - 1.96 * d.ep, hi = d.coef_z + 1.96 * d.ep;
    su.append("text").attr("class", "rot-medio").attr("x", mE - 8).attr("y", y + 4).attr("text-anchor", "end").text(`${d.ano} · ${d.modelo} vs ${d.referencia}`);
    su.append("line").attr("x1", xu(lo)).attr("x2", xu(hi)).attr("y1", y).attr("y2", y).attr("stroke", C.tinta2).attr("stroke-width", 3).attr("stroke-linecap", "round");
    su.append("circle").attr("cx", xu(d.coef_z)).attr("cy", y).attr("r", 5).attr("fill", C.tinta)
      .on("mousemove", ev => mostrarDica(`<b>${d.ano} · ${d.modelo}</b> (referência ${d.referencia})<br>diferença: ${fSin(d.coef_z, 3)} · p = ${fP(d.p)}<br>${fInt(d.secoes)} seções em ${fInt(d.municipios)} municípios`, ev)).on("mouseleave", esconderDica);
  });
  tabela($("#tab-extremos"), ["Variação maior que", "Seções", "% do total", "Com mudança de aptos"],
    A.extremos_comparecimento.map(e => [`${e.limite_pp} p.p.`, fInt(e.secoes), fPct(e.pct, 2), fInt(e.das_quais_aptos_mudaram)]), ["", "num", "num", "num"]);
  $("#link-mapa-z").onclick = e => { e.preventDefault(); varMapa = "z"; abrir("mapa"); window.scrollTo({ top: 0 }); };
};

/* ---------------- INVESTIGANDO (investigando.js) ---------------- */
renderizar.investigando = function () { invMontar(); };

/* ---------------- HISTÓRICO ---------------- */
renderizar.historico = function () {
  const h = D.historico.slice().sort((a, b) => a.ano - b.ano);
  const met = [["crescimento_a_por100aptos", "Crescimento do finalista do PT", C.lula], ["crescimento_b_por100aptos", "Crescimento do finalista de direita", C.dir],
    ["eliminados_por100aptos", "Votos dos eliminados no 1º turno", C.outros], ["var_validos_por100aptos", "Variação dos votos válidos", C.verde],
    ["var_brancos_nulos_por100aptos", "Variação de brancos e nulos", C.bn], ["var_comparecimento_pp", "Variação do comparecimento (p.p.)", C.realce]];
  const el = $("#g-hist-multi"); el.innerHTML = "";
  met.forEach(([k, rot, cor]) => {
    const div = document.createElement("div"); el.appendChild(div);
    const W = Math.max(260, larg(div)), H = 170, mT = 30, mB = 34;
    const vals = h.map(d => d[k]);
    const y = d3.scaleLinear().domain([Math.min(0, d3.min(vals)), Math.max(0, d3.max(vals))]).nice().range([H - mB, mT]);
    const x = d3.scaleBand().domain(h.map(d => d.ano)).range([10, W - 10]).padding(.3);
    const svg = d3.select(div).append("svg").attr("viewBox", `0 0 ${W} ${H}`);
    svg.append("text").attr("class", "rot-forte").attr("x", 10).attr("y", 14).text(rot);
    svg.append("line").attr("x1", 10).attr("x2", W - 10).attr("y1", y(0)).attr("y2", y(0)).attr("stroke", C.tinta3);
    h.forEach(d => {
      const v = d[k];
      svg.append("rect").attr("x", x(d.ano)).attr("width", x.bandwidth()).attr("y", Math.min(y(0), y(v))).attr("height", Math.max(1, Math.abs(y(v) - y(0)))).attr("rx", 2).attr("fill", cor).attr("fill-opacity", d.ano === 2026 ? 1 : .55);
      svg.append("text").attr("class", "rot").attr("x", x(d.ano) + x.bandwidth() / 2).attr("y", v >= 0 ? y(v) - 4 : y(v) + 12).attr("text-anchor", "middle").text(fSin(v, 2));
      svg.append("text").attr("class", "rot-medio").attr("x", x(d.ano) + x.bandwidth() / 2).attr("y", H - 18).attr("text-anchor", "middle").text(d.ano);
      svg.append("text").attr("class", "rot").attr("x", x(d.ano) + x.bandwidth() / 2).attr("y", H - 5).attr("text-anchor", "middle").style("font-size", "9px").text(k.includes("_a_") ? d.finalista_PT : k.includes("_b_") ? d.finalista_direita.replace("Jair ", "J. ").replace("Flávio ", "F. ") : "");
    });
  });
  // taxas
  const fl = [["b_1", "a_2", "Direita (1T) → PT (2T)"], ["a_1", "b_2", "PT (1T) → direita (2T)"], ["o_1", "a_2", "Eliminados → PT"], ["o_1", "b_2", "Eliminados → direita"],
    ["bn_1", "a_2", "Brancos/nulos → PT"], ["bn_1", "b_2", "Brancos/nulos → direita"], ["abst_1", "a_2", "Abstenção → PT"], ["abst_1", "b_2", "Abstenção → direita"]];
  const et = $("#g-hist-taxas"), W = larg(et), mE = Math.min(200, W * .38), bh = 9, H = fl.length * (3 * bh + 14) + 30;
  const x = d3.scaleLinear().domain([0, .65]).range([mE, W - 50]);
  const svg = d3.select(et).html("").append("svg").attr("viewBox", `0 0 ${W} ${H}`);
  svg.append("g").attr("class", "eixo").attr("transform", `translate(0,${H - 22})`).call(d3.axisBottom(x).ticks(6).tickFormat(t => fPct(100 * t, 0)));
  fl.forEach(([o, d, rot], i) => {
    const y0 = i * (3 * bh + 14);
    svg.append("text").attr("class", "rot-forte").attr("x", mE - 8).attr("y", y0 + 1.5 * bh + 4).attr("text-anchor", "end").text(rot);
    [2026, 2022, 2018].forEach((ano, j) => {
      const c = D.matrizes.find(m => m.ano === ano && m.nivel === "secao" && m.origens === "base" && m.origem === o && m.destino === d);
      const y = y0 + j * bh;
      svg.append("rect").attr("x", mE).attr("y", y).attr("height", bh - 1).attr("width", Math.max(1, x(c.taxa) - mE)).attr("fill", corCat(d)).attr("fill-opacity", [1, .6, .35][j])
        .on("mousemove", ev => mostrarDica(`<b>${ano}: ${nomeCat(o, ano)} → ${nomeCat(d, ano)}</b><br>${fPct(100 * c.taxa, 2)} (${fPct(100 * c.taxa_ic95_inf, 2)} a ${fPct(100 * c.taxa_ic95_sup, 2)})`, ev)).on("mouseleave", esconderDica);
      svg.append("text").attr("class", "rot").attr("x", x(c.taxa) + 4).attr("y", y + bh - 1).style("font-size", "9px").text(`${ano} ${fPct(100 * c.taxa, 1)}`);
    });
  });
  const lin = [["Líder no 1º turno", "lider_1T"], ["Vencedor no 2º turno", "vencedor_2T"], ["Finalista do PT: % dos válidos 1T → 2T", d => `${fPct(d.a_1T_pct_validos)} → ${fPct(d.a_2T_pct_validos)}`],
    ["Finalista de direita: % dos válidos 1T → 2T", d => `${fPct(d.b_1T_pct_validos)} → ${fPct(d.b_2T_pct_validos)}`], ["Eliminados (% dos válidos no 1T)", d => fPct(d.eliminados_pct_validos)],
    ["Crescimento do PT acima dos eliminados (por 100 aptos)", d => fSin(d.crescimento_a_menos_eliminados_por100aptos, 2)], ["Parcela do PT no crescimento conjunto", d => fPct(100 * d.parcela_crescimento_a_no_crescimento_conjunto, 0)]];
  const H2 = D.historico.slice().sort((a, b) => b.ano - a.ano);
  tabela($("#tab-hist"), ["", ...H2.map(d => d.ano)], lin.map(([r, k]) => [r, ...H2.map(d => typeof k === "function" ? k(d) : d[k])]), ["", "num", "num", "num"]);
};

/* ---------------- FONTES ---------------- */
renderizar.fontes = function () {
  tabela($("#tab-conf"), ["Turno", "Indicador", "Oficial", "Calculado", ""],
    D.conferencia.map(c => [c.turno + "º", c.indicador.replace(/_/g, " "), fInt(c.oficial), fInt(c.calculado), c.confere ? `<span class="pill ok">confere</span>` : `<span class="pill nao">difere</span>`]),
    ["", "", "num", "num", ""]);
  tabela($("#tab-fontes"), ["Arquivo", "Acesso (UTC)", "Tamanho", "SHA-256"],
    D.fontes.map(f => [f.url.startsWith("http") ? `<a href="${esc(f.url.split(" ")[0])}">${esc(f.url.replace("https://", "").slice(0, 90))}</a>${f.url.includes(" (") ? `<br><span class="nota">${esc(f.url.slice(f.url.indexOf(" (")))}</span>` : ""}` : esc(f.url),
      esc((f.acesso_utc || "").replace("T", " ").replace("+00:00", "")), f.tamanho_bytes > 1e6 ? fNum(f.tamanho_bytes / 1e6, 1) + " MB" : fNum(f.tamanho_bytes / 1e3, 0) + " kB",
      `<code>${esc(f.sha256)}</code>`]), ["", "", "num", ""]);
};

/* ---------------- início ---------------- */
function rerender() { C = cores(); feitos.clear(); if (renderizar[abaAtual]) { renderizar[abaAtual](); feitos.add(abaAtual); } }
let tmr; window.addEventListener("resize", () => { clearTimeout(tmr); tmr = setTimeout(rerender, 200); });
try { window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", rerender); } catch (e) { /* navegador antigo */ }
new MutationObserver(rerender).observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
$("#gerado-em").textContent = D.gerado_em;
abrir((location.hash || "#resumo").slice(1));
