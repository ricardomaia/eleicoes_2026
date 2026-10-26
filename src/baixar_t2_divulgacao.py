"""Baixa os resultados do 2º turno presidencial (25/10/2026) do sistema de
divulgação do TSE (resultados.tse.jus.br), por município.

Motivo: na data da execução (26/10/2026) o portal de dados abertos ainda não
tinha publicado os arquivos do 2º turno (votacao_secao, detalhe_votacao_secao
e bweb_2t). O sistema de divulgação publica um JSON por município com aptos,
comparecimento, brancos, nulos e votos de cada candidato.

Arquivos baixados (ciclo ele2026, eleição 6258 = Federal 2º turno):
  config/mun-e006258-cm.json             lista de municípios e códigos IBGE
  dados/br/br-c0001-e006258-u.json       total nacional
  dados/<uf>/<uf>-c0001-e006258-u.json   total por UF (inclui zz = exterior)
  dados/<uf>/<uf><mun>-c0001-e006258-u.json   total por município
"""
from __future__ import annotations

import concurrent.futures as cf
import json
import sys

from comum import DIVULGA, ELEICAO_T2_FED, RAW, baixar, registrar_manifesto

DEST = RAW / "2026" / "t2_divulgacao"
E = ELEICAO_T2_FED


def main(paralelo: int = 6) -> None:
    cfg_url = f"{DIVULGA}/ele2026/{E}/config/mun-e{int(E):06d}-cm.json"
    cfg = baixar(cfg_url, DEST / "config" / cfg_url.rsplit("/", 1)[1], sobrescrever=True)
    municipios = json.loads(cfg.read_text(encoding="utf-8"))

    alvos = [f"{DIVULGA}/ele2026/{E}/dados/br/br-c0001-e{int(E):06d}-u.json",
             f"{DIVULGA}/ele2026/{E}/dados/br/br-e{int(E):06d}-ab.json"]
    for abr in municipios["abr"]:
        uf = abr["cd"]
        alvos.append(f"{DIVULGA}/ele2026/{E}/dados/{uf}/{uf}-c0001-e{int(E):06d}-u.json")
        for mu in abr["mu"]:
            alvos.append(f"{DIVULGA}/ele2026/{E}/dados/{uf}/{uf}{mu['cd']}-c0001-e{int(E):06d}-u.json")

    def tarefa(url: str):
        partes = url.split("/dados/")[1]
        destino = DEST / "dados" / partes
        try:
            baixar(url, destino, registrar=False)
            return url, None
        except Exception as e:  # registra e segue; falhas são listadas no fim
            return url, repr(e)

    falhas = []
    with cf.ThreadPoolExecutor(paralelo) as ex:
        for i, (url, erro) in enumerate(ex.map(tarefa, alvos), 1):
            if erro:
                falhas.append((url, erro))
            if i % 500 == 0:
                print(f"{i}/{len(alvos)} arquivos", flush=True)

    # Um registro de manifesto por arquivo seria grande demais (5.800 linhas);
    # registra-se o diretório com um hash do conjunto ordenado de hashes.
    import hashlib
    from comum import sha256_arquivo
    arquivos = sorted((DEST / "dados").rglob("*.json"))
    h = hashlib.sha256()
    for a in arquivos:
        h.update(a.name.encode() + sha256_arquivo(a).encode())
    lista = DEST / "lista_arquivos_sha256.txt"
    with open(lista, "w", encoding="utf-8") as f:
        for a in arquivos:
            f.write(f"{sha256_arquivo(a)}  {a.relative_to(DEST).as_posix()}\n")
    registrar_manifesto(f"{DIVULGA}/ele2026/{E}/dados/<uf>/<uf><mun>-c0001-e{int(E):06d}-u.json "
                        f"({len(arquivos)} arquivos; hash = sha256 da lista)", lista, "ok")
    print(f"baixados {len(arquivos)} de {len(alvos)}; falhas: {len(falhas)}")
    for u, e in falhas:
        print("FALHA", u, e)
    if falhas:
        sys.exit(1)


if __name__ == "__main__":
    main()
