"""Converte os JSON municipais do 2º turno (sistema de divulgação) numa tabela.

Campos usados do JSON "-u" (resultado por abrangência):
  s.ts / s.st      seções totais / seções totalizadas
  e.te             eleitorado apto
  e.c / e.a        comparecimento / abstenção
  v.tv             total de votos
  v.vv             votos válidos      v.vnom  votos nominais
  v.van, v.vansj   votos anulados (e anulados sub judice) — computados à parte
  v.vb             brancos            v.tvn   total de nulos
  carg[0].agr[].par[].cand[].vap   votos apurados do candidato

Saída: interim/t2_municipios_2026.parquet e dados_derivados/t2_municipios_2026.csv
"""
from __future__ import annotations

import json

import pandas as pd

from comum import DERIVADOS, INTERIM, RAW

ORIGEM = RAW / "2026" / "t2_divulgacao"

NUM_CANDIDATO = {"13": "lula", "22": "flavio"}


def _i(x) -> int:
    return int(x) if x not in (None, "") else 0


def ler_resultado(caminho) -> dict:
    d = json.loads(caminho.read_text(encoding="utf-8"))
    s, e, v = d["s"], d["e"], d["v"]
    lin = {
        "tpabr": d["tpabr"], "cdabr": d["cdabr"],
        "dt_geracao": f'{d["dg"]} {d["hg"]}', "dt_totalizacao": f'{d["dt"]} {d["ht"]}',
        "totalizacao_final": d.get("tf"),
        "secoes_total": _i(s["ts"]), "secoes_totalizadas": _i(s["st"]),
        "aptos": _i(e["te"]), "aptos_secoes_totalizadas": _i(e["est"]),
        "comparecimento": _i(e["c"]), "abstencao": _i(e["a"]),
        "votos_total": _i(v["tv"]), "validos": _i(v["vv"]),
        "nominais": _i(v["vnom"]), "anulados": _i(v["van"]),
        "anulados_subjudice": _i(v["vansj"]),
        "brancos": _i(v["vb"]), "nulos": _i(v["tvn"]),
        "nulos_tecnicos": _i(v.get("vnt")),
    }
    for c in d["carg"]:
        if c["cd"] != "1":
            continue
        for agr in c["agr"]:
            for par in agr["par"]:
                for cand in par["cand"]:
                    chave = NUM_CANDIDATO.get(cand["n"], f'cand_{cand["n"]}')
                    lin[chave] = _i(cand["vap"])
                    lin[f"{chave}_situacao"] = cand.get("st")
    return lin


def main() -> pd.DataFrame:
    cfg = json.loads((ORIGEM / "config" / "mun-e006258-cm.json").read_text(encoding="utf-8"))
    cod_ibge, nomes, capital = {}, {}, {}
    for abr in cfg["abr"]:
        for mu in abr["mu"]:
            cod_ibge[mu["cd"]] = mu["cdi"]
            nomes[mu["cd"]] = mu["nm"]
            capital[mu["cd"]] = mu["c"] == "s"

    linhas = []
    for uf_dir in sorted((ORIGEM / "dados").iterdir()):
        uf = uf_dir.name
        for arq in sorted(uf_dir.glob("*-u.json")):
            lin = ler_resultado(arq)
            lin["uf"] = uf.upper()
            linhas.append(lin)
    df = pd.DataFrame(linhas)

    mun = df[df.tpabr == "mu"].copy()
    mun["cd_mun_tse"] = mun["cdabr"].astype(str).str.zfill(5)
    mun["cd_ibge"] = mun["cd_mun_tse"].map(cod_ibge)
    mun["nm_municipio"] = mun["cd_mun_tse"].map(nomes)
    mun["capital"] = mun["cd_mun_tse"].map(capital)

    # Verificações internas de cada registro (anotadas, nada é descartado).
    mun["chk_comp_eq_votos"] = mun.comparecimento == mun.votos_total
    mun["chk_votos_eq_soma"] = mun.votos_total == mun.validos + mun.brancos + mun.nulos + mun.anulados + mun.anulados_subjudice
    mun["chk_validos_eq_cand"] = mun.validos == mun.lula + mun.flavio
    mun["chk_aptos_eq_comp_abst"] = mun.aptos == mun.comparecimento + mun.abstencao
    mun["chk_totalizado"] = mun.secoes_totalizadas == mun.secoes_total

    agregados = df[df.tpabr != "mu"].copy()
    INTERIM.mkdir(parents=True, exist_ok=True)
    mun.to_parquet(INTERIM / "t2_municipios_2026.parquet", index=False)
    agregados.to_parquet(INTERIM / "t2_agregados_2026.parquet", index=False)
    cols = ["uf", "cd_mun_tse", "cd_ibge", "nm_municipio", "capital", "secoes_total",
            "secoes_totalizadas", "aptos", "comparecimento", "abstencao", "votos_total",
            "validos", "brancos", "nulos", "anulados", "anulados_subjudice", "lula", "flavio",
            "dt_totalizacao"]
    mun[cols].to_csv(DERIVADOS / "t2_municipios_2026.csv", index=False)

    chk = [c for c in mun.columns if c.startswith("chk_")]
    print(len(mun), "municípios;", "falhas por verificação:")
    print((~mun[chk]).sum())
    print(agregados[["tpabr", "cdabr", "aptos", "comparecimento", "validos", "lula", "flavio"]]
          .query("tpabr=='br'"))
    return mun


if __name__ == "__main__":
    main()
