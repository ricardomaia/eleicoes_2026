"""Configuração e utilitários comuns da auditoria.

Os dados brutos (vários GB) ficam fora do Google Drive, no diretório indicado
pela variável de ambiente AUDITORIA_DADOS (padrão: ~/dados-tse). O código,
as tabelas de resultado e os dados derivados pequenos ficam na pasta do
projeto.
"""
from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
import os
import random
import threading
import time
from pathlib import Path

import requests

PROJETO = Path(__file__).resolve().parents[1]
DADOS = Path(os.environ.get("AUDITORIA_DADOS", Path.home() / "dados-tse"))
RAW = DADOS / "raw"
INTERIM = DADOS / "interim"
DERIVADOS = PROJETO / "dados_derivados"
TABELAS = PROJETO / "resultados" / "tabelas"
FIGURAS = PROJETO / "resultados" / "figuras"
INTEGRIDADE = PROJETO / "integridade"
MANIFESTO = INTEGRIDADE / "manifesto_downloads.csv"

for _p in (RAW, INTERIM, DERIVADOS, TABELAS, FIGURAS, INTEGRIDADE):
    _p.mkdir(parents=True, exist_ok=True)

# Semente global: todas as rotinas aleatórias derivam dela (registrada em
# resultados/tabelas/parametros_execucao.json).
SEMENTE = 20261025

CDN = "https://cdn.tse.jus.br/estatistica/sead/odsele"
CDN_BU = "https://cdn.tse.jus.br/estatistica/sead/eleicoes"
DIVULGA = "https://resultados.tse.jus.br/oficial"

# Códigos de eleição/pleito no sistema de divulgação do TSE (ele-c.json).
ELEICAO_T1_FED, ELEICAO_T2_FED = "6257", "6258"
PLEITO_T1, PLEITO_T2 = "3220", "3221"

UFS = ["AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS",
       "MT", "PA", "PB", "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC",
       "SE", "SP", "TO"]

REGIAO = {
    "AC": "Norte", "AM": "Norte", "AP": "Norte", "PA": "Norte", "RO": "Norte",
    "RR": "Norte", "TO": "Norte",
    "AL": "Nordeste", "BA": "Nordeste", "CE": "Nordeste", "MA": "Nordeste",
    "PB": "Nordeste", "PE": "Nordeste", "PI": "Nordeste", "RN": "Nordeste",
    "SE": "Nordeste",
    "DF": "Centro-Oeste", "GO": "Centro-Oeste", "MS": "Centro-Oeste",
    "MT": "Centro-Oeste",
    "ES": "Sudeste", "MG": "Sudeste", "RJ": "Sudeste", "SP": "Sudeste",
    "PR": "Sul", "RS": "Sul", "SC": "Sul",
    "ZZ": "Exterior",
}

_sessao_local = threading.local()
_trava_manifesto = threading.Lock()


def sessao() -> requests.Session:
    s = getattr(_sessao_local, "s", None)
    if s is None:
        s = requests.Session()
        s.headers["User-Agent"] = (
            "Mozilla/5.0 (auditoria estatistica academica; dados abertos TSE)")
        _sessao_local.s = s
    return s


def sha256_arquivo(caminho: Path, bloco: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        while True:
            b = f.read(bloco)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def registrar_manifesto(url: str, destino: Path, status: str,
                        last_modified: str = "", etag: str = "") -> None:
    """Acrescenta uma linha ao manifesto de downloads (URL, data, tamanho, hash)."""
    novo = not MANIFESTO.exists()
    tam = destino.stat().st_size if destino.exists() else 0
    sha = sha256_arquivo(destino) if destino.exists() else ""
    linha = {
        "url": url,
        "arquivo_local": str(destino.relative_to(DADOS)) if destino.is_relative_to(DADOS) else str(destino),
        "acesso_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "tamanho_bytes": tam,
        "sha256": sha,
        "last_modified_servidor": last_modified,
        "etag_servidor": etag,
        "status": status,
    }
    with _trava_manifesto:
        with open(MANIFESTO, "a", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(linha))
            if novo:
                w.writeheader()
            w.writerow(linha)


def baixar(url: str, destino: Path, *, registrar: bool = True,
           tentativas: int = 8, timeout: int = 600, sobrescrever: bool = False) -> Path:
    """Baixa um arquivo com retomada simples e espera exponencial em 429/5xx."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    if destino.exists() and destino.stat().st_size > 0 and not sobrescrever:
        return destino
    tmp = destino.with_suffix(destino.suffix + ".part")
    espera = 5.0
    for tentativa in range(tentativas):
        try:
            with sessao().get(url, stream=True, timeout=timeout) as r:
                if r.status_code in (429, 500, 502, 503, 504):
                    raise requests.HTTPError(f"HTTP {r.status_code}")
                r.raise_for_status()
                with open(tmp, "wb") as f:
                    for bloco in r.iter_content(1 << 20):
                        f.write(bloco)
                tmp.replace(destino)
                if registrar:
                    registrar_manifesto(url, destino, "ok",
                                        r.headers.get("Last-Modified", ""),
                                        r.headers.get("ETag", ""))
                return destino
        except (requests.RequestException, OSError) as e:
            if isinstance(e, requests.HTTPError) and "404" in str(e):
                raise
            time.sleep(espera + random.random() * espera)
            espera = min(espera * 2, 300)
    raise RuntimeError(f"falha ao baixar {url}")


def salvar_json(obj, caminho: Path) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, default=str)
