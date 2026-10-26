"""Leitura dos boletins de urna (BU) do 2º turno de 2026.

O arquivo .bu é codificado em ASN.1/BER. A especificação publicada pelo TSE
em 2022 (formato-arquivos-bu-rdv-ass-digital.zip) não decodifica o
BU de 2026: o campo urna.correspondenciaResultado.carga.dataHoraCarga mudou de
tipo. Para não depender da especificação completa, este módulo percorre a
árvore BER e extrai apenas os campos de resultado, cuja estrutura não mudou:

ResultadoVotacaoPorEleicao ::= SEQUENCE {
    idEleicao, qtdEleitoresAptos, ..., resultadosVotacao SEQUENCE OF
        ResultadoVotacao ::= SEQUENCE { tipoCargo ENUM, qtdComparecimento,
            totaisVotosCargo SEQUENCE OF TotalVotosCargo ::= SEQUENCE {
                codigoCargo [1], ordemImpressao, votosVotaveis SEQUENCE OF
                    TotalVotosVotavel ::= SEQUENCE { tipoVoto [1],
                        quantidadeVotos [2], identificacaoVotavel [3] {partido, codigo} OPTIONAL,
                        ..., assinatura OCTET STRING } } } }

tipoVoto: 1 = nominal, 2 = branco, 3 = nulo, 4 = legenda (cargos proporcionais).
A leitura foi conferida contra o arquivo detalhe_votacao_secao do TSE
(aptos, comparecimento, brancos, nulos e nominais de cada seção).
"""
from __future__ import annotations

from dataclasses import dataclass, field

UNIVERSAL, CONTEXTO = 0, 2
INTEIRO, ENUMERADO, OCTETOS, SEQUENCIA = 2, 10, 4, 16


@dataclass
class No:
    classe: int
    construido: bool
    tag: int
    valor: bytes = b""
    filhos: list = field(default_factory=list)

    def inteiro(self) -> int:
        return int.from_bytes(self.valor, "big", signed=True)


def _ler_tlv(b: bytes, i: int):
    t = b[i]
    i += 1
    classe, construido, tag = t >> 6, bool(t & 0x20), t & 0x1F
    if tag == 0x1F:
        tag = 0
        while True:
            x = b[i]
            i += 1
            tag = (tag << 7) | (x & 0x7F)
            if not x & 0x80:
                break
    n = b[i]
    i += 1
    if n & 0x80:
        k = n & 0x7F
        n = int.from_bytes(b[i:i + k], "big")
        i += k
    return classe, construido, tag, i, n


def arvore(b: bytes, i: int = 0, fim: int | None = None) -> list[No]:
    fim = len(b) if fim is None else fim
    nos = []
    while i < fim:
        classe, construido, tag, vi, n = _ler_tlv(b, i)
        no = No(classe, construido, tag)
        if construido:
            no.filhos = arvore(b, vi, vi + n)
        else:
            no.valor = b[vi:vi + n]
        nos.append(no)
        i = vi + n
    return nos


def _ints(no: No) -> list[int]:
    return [f.inteiro() for f in no.filhos
            if f.classe == UNIVERSAL and f.tag == INTEIRO and not f.construido]


def ler_bu(conteudo_arquivo: bytes, id_eleicao: int = 6258, cargo: int = 1) -> dict:
    """Retorna aptos, comparecimento, votos nominais por número, brancos e nulos."""
    envelope = arvore(conteudo_arquivo)[0]
    interno = next(f for f in envelope.filhos
                   if f.classe == UNIVERSAL and f.tag == OCTETOS and len(f.valor) > 200)
    bu = arvore(interno.valor)[0]

    # identificação da seção no BU interno: SEQUENCE { {municipio, zona}, local, secao }.
    # Vale para o BU da urna e para o BU do Sistema de Apuração (busa).
    ident = next(f for f in bu.filhos
                 if f.construido and f.tag == SEQUENCIA and f.filhos
                 and f.filhos[0].construido and len(_ints(f.filhos[0])) == 2
                 and len(_ints(f)) == 2)
    mz = _ints(ident.filhos[0])
    loc_sec = _ints(ident)
    saida = {"municipio": mz[0], "zona": mz[1], "local": loc_sec[0], "secao": loc_sec[1]}

    # lista de ResultadoVotacaoPorEleicao: SEQUENCE cujo filho é SEQUENCE iniciada por idEleicao
    for f in bu.filhos:
        if not (f.construido and f.tag == SEQUENCIA):
            continue
        for rpe in f.filhos:
            if not (rpe.construido and rpe.tag == SEQUENCIA):
                continue
            ints = _ints(rpe)
            if len(ints) < 2 or ints[0] != id_eleicao:
                continue
            saida["aptos"] = ints[1]
            lista_rv = next(x for x in rpe.filhos if x.construido and x.tag == SEQUENCIA)
            for rv in lista_rv.filhos:
                comp = _ints(rv)
                lista_tvc = next(x for x in rv.filhos if x.construido and x.tag == SEQUENCIA)
                for tvc in lista_tvc.filhos:
                    cod = next(x for x in tvc.filhos if x.classe == CONTEXTO and x.tag == 1).inteiro()
                    if cod != cargo:
                        continue
                    saida["comparecimento"] = comp[0]
                    votos, brancos, nulos = {}, 0, 0
                    lista_vv = next(x for x in tvc.filhos if x.construido and x.tag == SEQUENCIA)
                    for vv in lista_vv.filhos:
                        tipo = qtd = None
                        numero = None
                        for x in vv.filhos:
                            if x.classe == CONTEXTO and x.tag == 1:
                                tipo = x.inteiro()
                            elif x.classe == CONTEXTO and x.tag == 2:
                                qtd = x.inteiro()
                            elif x.classe == CONTEXTO and x.tag == 3:
                                numero = _ints(x)[-1]
                        if tipo == 1:
                            votos[numero] = votos.get(numero, 0) + qtd
                        elif tipo == 2:
                            brancos += qtd
                        elif tipo == 3:
                            nulos += qtd
                        else:
                            saida.setdefault("outros_tipos", []).append((tipo, qtd))
                    saida["votos"] = votos
                    saida["brancos"] = brancos
                    saida["nulos"] = nulos
                    return saida
    raise ValueError("resultado da eleição/cargo não encontrado no BU")
