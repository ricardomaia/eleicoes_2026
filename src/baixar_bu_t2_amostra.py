"""Baixa os boletins de urna do 2º turno de uma amostra aleatória de seções.

Por que amostra: em 26/10/2026 o TSE já publicou o 2º turno por seção no
arquivo detalhe_votacao_secao (aptos, comparecimento, brancos, nulos,
nominais), mas ainda não a votação por candidato por seção (votacao_secao).
A divisão Lula/Flávio por seção só está nos BUs individuais do sistema de
divulgação, que exigem duas requisições por seção (índice + BU). Baixar as
~499 mil seções levaria horas; uma amostra estratificada por UF basta para a
inferência ecológica em nível de seção. Quando o arquivo votacao_secao do 2º
turno for publicado, montar_base.py passa a usá-lo no lugar da amostra.

Desenho da amostra: aleatória simples sem reposição dentro de cada UF
(estratos = 27 UFs + exterior), fração 10%, mínimo de 400 seções por estrato
(ou todas, se houver menos), semente fixa SEMENTE. Universo = seções
instaladas e não anuladas do 2º turno no detalhe_votacao_secao.
"""
from __future__ import annotations

import concurrent.futures as cf
import json
import time

import duckdb
import numpy as np
import pandas as pd

from boletim_urna import ler_bu
from comum import DIVULGA, INTERIM, PLEITO_T2, RAW, SEMENTE, sessao

DETALHE = RAW / "2026" / "ex" / "dvs" / "detalhe_votacao_secao_2026_BR.csv"
DEST = RAW / "2026" / "bu_t2_amostra"
FRACAO, MINIMO = 0.10, 400


def universo() -> pd.DataFrame:
    q = f"""
    select SG_UF uf, CD_MUNICIPIO::INT mun, NR_ZONA::INT zona, NR_SECAO::INT secao
    from read_csv('{DETALHE.as_posix()}', delim=';', encoding='latin-1', header=true, all_varchar=true)
    where NR_TURNO='2' and CD_CARGO='1' and ST_SECAO_INSTALADA='Sim'
    order by 1,2,3,4"""
    return duckdb.sql(q).df()


def sortear(u: pd.DataFrame) -> pd.DataFrame:
    rng = np.random.default_rng(SEMENTE)
    partes = []
    for uf, g in u.groupby("uf", sort=True):
        n = min(len(g), max(MINIMO, int(round(FRACAO * len(g)))))
        idx = rng.choice(len(g), size=n, replace=False)
        s = g.iloc[np.sort(idx)].copy()
        s["n_estrato"], s["n_amostra"] = len(g), n
        partes.append(s)
    return pd.concat(partes, ignore_index=True)


def url_aux(uf, mun, zona, secao) -> str:
    u = uf.lower()
    base = f"{DIVULGA}/ele2026/arquivo-urna/{PLEITO_T2}/dados/{u}/{mun:05d}/{zona:04d}/{secao:04d}"
    return base, f"{base}/p00{PLEITO_T2}-{u}-m{mun:05d}-z{zona:04d}-s{secao:04d}-aux.json"


def obter(url: str, tentativas: int = 8) -> bytes:
    espera = 2.0
    for _ in range(tentativas):
        try:
            r = sessao().get(url, timeout=60)
            if r.status_code == 200:
                return r.content
            if r.status_code == 404:
                raise FileNotFoundError(url)
        except FileNotFoundError:
            raise
        except Exception:
            pass
        time.sleep(espera)
        espera = min(espera * 2, 120)
    raise RuntimeError(url)


def baixar_secao(linha) -> dict:
    uf, mun, zona, secao = linha
    destino = DEST / uf / f"{mun:05d}-{zona:04d}-{secao:04d}.bu"
    reg = {"uf": uf, "mun": mun, "zona": zona, "secao": secao}
    try:
        if not destino.exists():
            base, ua = url_aux(uf, mun, zona, secao)
            aux = json.loads(obter(ua))
            hashes = aux.get("hashes", [])
            reg["n_hashes"] = len(hashes)
            reg["st_hashes"] = "|".join(h.get("st", "") for h in hashes)
            escolhido = [h for h in hashes if h.get("st") == "Totalizado"] or hashes
            h = escolhido[-1]
            nome_bu = next(a["nm"] for a in h["arq"] if a["tp"] in ("bu", "busa"))
            reg["tipo_bu"] = nome_bu.rsplit("-", 1)[1]
            conteudo = obter(f"{base}/{h['hash']}/{nome_bu}")
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_bytes(conteudo)
        r = ler_bu(destino.read_bytes())
        reg.update({k: v for k, v in r.items() if k != "votos"})
        for num, q in r["votos"].items():
            reg[f"v{num}"] = q
        reg["erro"] = ""
    except Exception as e:
        reg["erro"] = repr(e)[:200]
    return reg


def main(paralelo: int = 12) -> None:
    amostra = sortear(universo())
    amostra.to_csv(INTERIM / "amostra_secoes_t2.csv", index=False)
    print("amostra:", len(amostra), "seções em", amostra.uf.nunique(), "estratos", flush=True)
    linhas = list(amostra[["uf", "mun", "zona", "secao"]].itertuples(index=False, name=None))
    regs = []
    with cf.ThreadPoolExecutor(paralelo) as ex:
        for i, reg in enumerate(ex.map(baixar_secao, linhas), 1):
            regs.append(reg)
            if i % 2000 == 0:
                print(f"{i}/{len(linhas)}", flush=True)
    df = pd.DataFrame(regs)
    df.to_parquet(INTERIM / "bu_t2_amostra.parquet", index=False)
    print("erros:", (df.erro != "").sum())
    print(df[df.erro != ""].head(20).to_string())


if __name__ == "__main__":
    main()
