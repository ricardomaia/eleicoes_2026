"""Monta as bases consolidadas por seção e por município (2026, 2022, 2018).

Notação (igual para os três anos):
  a = finalista do PT (2026 e 2022: Lula, nº 13; 2018: Haddad, nº 13)
  b = finalista de direita (2026: Flávio Bolsonaro, nº 22; 2022: Jair
      Bolsonaro, nº 22; 2018: Jair Bolsonaro, nº 17)
  o = demais candidatos válidos do 1º turno
  bn = brancos + nulos (inclui nulos técnicos e votos anulados apurados em separado)
  abst = abstenção = aptos − comparecimento
Sufixo _1 = 1º turno, _2 = 2º turno.

Fontes por seção:
  detalhe_votacao_secao_<ano>_BR.csv : aptos, comparecimento, nominais, brancos,
      nulos, situação da seção, origem do voto, modelo da urna (os dois turnos)
  votacao_secao_<ano>_BR.csv : votos por número votável (95 = branco, 96 = nulo,
      97 = anulado e apurado em separado)
  2026, 2º turno: a votação por candidato por seção ainda não estava publicada
      em votacao_secao; usa-se a amostra de BUs (bu_t2_amostra.parquet).
      Se votacao_secao_2026_BR.csv passar a conter NR_TURNO=2, ela é usada.

Saídas (interim/): secoes_<ano>.parquet, municipios_<ano>.parquet
               (dados_derivados/): municipios_<ano>.csv
               (integridade/): verificacoes_base_<ano>.json
"""
from __future__ import annotations

import zipfile
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

from comum import DERIVADOS, INTEGRIDADE, INTERIM, RAW, salvar_json

FINALISTAS = {2026: ("13", "22"), 2022: ("13", "22"), 2018: ("13", "17")}
# Números que não são votos válidos a candidatos.
INVALIDOS = {"95": "branco", "96": "nulo", "97": "anulado_apu_sep"}
# Candidatos cujos votos foram computados como nulos técnicos (TSE, relatório oficial).
NULOS_TECNICOS = {2026: {"28"}, 2022: set(), 2018: set()}
# Demais candidatos de 2026 individualizados no modelo (≥ 0,2% dos válidos).
OUTROS_2026 = {"70": "cury", "14": "renan", "55": "caiado", "30": "zema"}

CHAVE = ["uf", "cd_mun", "zona", "secao"]


def extrair(ano: int, zipnome: str, membro: str, subdir: str) -> Path:
    destino = RAW / str(ano) / "ex" / subdir / membro
    if not destino.exists():
        destino.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(RAW / str(ano) / zipnome) as z:
            z.extract(membro, destino.parent)
    return destino


def ler_detalhe(ano: int) -> pd.DataFrame:
    p = extrair(ano, f"detalhe_votacao_secao_{ano}.zip", f"detalhe_votacao_secao_{ano}_BR.csv", "dvs")
    q = f"""
    select NR_TURNO::INT turno, SG_UF uf, CD_MUNICIPIO::INT cd_mun, NR_ZONA::INT zona,
           NR_SECAO::INT secao, any_value(NM_MUNICIPIO) nm_municipio,
           any_value(NR_LOCAL_VOTACAO)::INT nr_local,
           sum(QT_APTOS::BIGINT) aptos, sum(QT_COMPARECIMENTO::BIGINT) comp,
           sum(QT_ABSTENCOES::BIGINT) abst_tse, sum(QT_VOTOS_NOMINAIS::BIGINT) nominais,
           sum(QT_VOTOS_BRANCOS::BIGINT) brancos, sum(QT_VOTOS_NULOS::BIGINT) nulos,
           sum(coalesce(try_cast(QT_VOTOS_ANULADOS_APU_SEP as BIGINT),0)) anul_apu_sep,
           any_value(DS_ORIGEM_VOTO) origem_voto, any_value(ST_SECAO_INSTALADA) instalada,
           any_value(ST_SECAO_ANULADA) anulada, any_value(DS_MODELO_URNA) modelo_urna,
           count(*) n_linhas
    from read_csv('{p.as_posix()}', delim=';', encoding='latin-1', header=true, all_varchar=true)
    where CD_CARGO = '1'
    group by all
    """
    return duckdb.sql(q).df()


def ler_votos(ano: int) -> pd.DataFrame:
    p = extrair(ano, f"votacao_secao_{ano}_BR.zip", f"votacao_secao_{ano}_BR.csv", "vs")
    q = f"""
    select NR_TURNO::INT turno, SG_UF uf, CD_MUNICIPIO::INT cd_mun, NR_ZONA::INT zona,
           NR_SECAO::INT secao, NR_VOTAVEL num, sum(QT_VOTOS::BIGINT) votos
    from read_csv('{p.as_posix()}', delim=';', encoding='latin-1', header=true, all_varchar=true)
    where CD_CARGO = '1'
    group by all
    """
    longo = duckdb.sql(q).df()
    largo = longo.pivot_table(index=["turno"] + CHAVE, columns="num", values="votos",
                              aggfunc="sum", fill_value=0)
    largo.columns = [f"n{c}" for c in largo.columns]
    return largo.reset_index()


def compor(ano: int, det: pd.DataFrame, vot: pd.DataFrame, turno: int) -> pd.DataFrame:
    a, b = FINALISTAS[ano]
    d = det[det.turno == turno].drop(columns="turno")
    v = vot[vot.turno == turno].drop(columns="turno")
    x = d.merge(v, on=CHAVE, how="left", indicator=True)
    x["tem_votos"] = x.pop("_merge") == "both"
    numcols = [c for c in x.columns if c.startswith("n") and c[1:].isdigit()]
    x[numcols] = x[numcols].fillna(0).astype("int64")
    tecnicos = [f"n{n}" for n in NULOS_TECNICOS[ano] if f"n{n}" in x]
    candidatos = [c for c in numcols if c[1:] not in INVALIDOS and c not in tecnicos]
    out = x[CHAVE + ["nm_municipio", "nr_local", "aptos", "comp", "abst_tse", "nominais",
                     "brancos", "nulos", "anul_apu_sep", "origem_voto", "instalada",
                     "anulada", "modelo_urna", "tem_votos"]].copy()
    out["a"] = x.get(f"n{a}", 0)
    out["b"] = x.get(f"n{b}", 0)
    out["validos"] = x[candidatos].sum(axis=1)
    out["o"] = out["validos"] - out["a"] - out["b"]
    out["bn_csv"] = x.get("n95", 0) + x.get("n96", 0) + x.get("n97", 0) + (x[tecnicos].sum(axis=1) if tecnicos else 0)
    out["bn"] = out["comp"] - out["validos"]
    out["abst"] = out["aptos"] - out["comp"]
    if ano == 2026 and turno == 1:
        for num, nome in OUTROS_2026.items():
            out[nome] = x.get(f"n{num}", 0)
        out["outros_peq"] = out["o"] - out[list(OUTROS_2026.values())].sum(axis=1)
    sufixo = f"_{turno}"
    chaves = set(CHAVE + ["nm_municipio", "nr_local"])
    return out.rename(columns={c: c + sufixo for c in out.columns if c not in chaves})


def votos_t2_2026_amostra() -> pd.DataFrame:
    arq = INTERIM / "bu_t2_amostra.parquet"
    if not arq.exists():
        return pd.DataFrame(columns=CHAVE + ["a_2", "b_2", "bu_aptos", "bu_comp", "bu_brancos", "bu_nulos"])
    bu = pd.read_parquet(arq)
    bu = bu[bu.erro == ""].rename(columns={"mun": "cd_mun"})
    return pd.DataFrame({
        "uf": bu.uf, "cd_mun": bu.cd_mun, "zona": bu.zona, "secao": bu.secao,
        "a_2": bu.v13.fillna(0).astype("int64"), "b_2": bu.v22.fillna(0).astype("int64"),
        "bu_aptos": bu.aptos, "bu_comp": bu.comparecimento,
        "bu_brancos": bu.brancos, "bu_nulos": bu.nulos,
    })


def montar(ano: int) -> tuple[pd.DataFrame, dict]:
    det = ler_detalhe(ano)
    vot = ler_votos(ano)
    s1 = compor(ano, det, vot, 1)
    chk: dict = {"ano": ano}
    t2_no_csv = (vot.turno == 2).any()
    if t2_no_csv:
        s2 = compor(ano, det, vot, 2)
        chk["fonte_t2_candidatos"] = "votacao_secao (completo)"
        if ano == 2026:
            # A amostra de BUs continua marcada (na_amostra_bu) para que as análises por amostra
            # sejam reproduzíveis, e serve de conferência entre o BU e o arquivo por seção.
            am = votos_t2_2026_amostra().rename(columns={"a_2": "bu_a", "b_2": "bu_b"})
            s2 = s2.merge(am, on=CHAVE, how="left")
            s2["na_amostra_bu"] = s2["bu_a"].notna()
            m = s2[s2.na_amostra_bu]
            chk["bu_amostra_n"] = int(len(m))
            chk["bu_divergencias_vs_votacao_secao"] = {
                "aptos": int((m.bu_aptos != m.aptos_2).sum()), "comparecimento": int((m.bu_comp != m.comp_2).sum()),
                "brancos": int((m.bu_brancos != m.brancos_2).sum()), "nulos": int((m.bu_nulos != m.nulos_2).sum()),
                "lula": int((m.bu_a != m.a_2).sum()), "flavio": int((m.bu_b != m.b_2).sum())}
            s2 = s2.drop(columns=["bu_a", "bu_b"])
    else:
        d2 = det[det.turno == 2].drop(columns="turno")
        s2 = d2[CHAVE + ["aptos", "comp", "nominais", "brancos", "nulos", "anul_apu_sep",
                         "origem_voto", "instalada", "anulada", "modelo_urna"]].copy()
        s2["validos"] = s2["nominais"]  # 2º turno: nominais = válidos (sem nulos técnicos)
        s2["bn"] = s2["comp"] - s2["validos"]
        s2["abst"] = s2["aptos"] - s2["comp"]
        am = votos_t2_2026_amostra()
        s2 = s2.merge(am, on=CHAVE, how="left")
        s2["na_amostra_bu"] = s2["a_2"].notna()
        s2 = s2.rename(columns={c: c + "_2" for c in s2.columns
                                if c not in CHAVE and not c.endswith("_2") and not c.startswith("bu_")
                                and c != "na_amostra_bu"})
        chk["fonte_t2_candidatos"] = "amostra de BUs (sistema de divulgação)"
        # Conferência BU × detalhe por seção (amostra)
        m = s2[s2.na_amostra_bu]
        chk["bu_amostra_n"] = int(len(m))
        chk["bu_divergencias"] = {
            "aptos": int((m.bu_aptos != m.aptos_2).sum()),
            "comparecimento": int((m.bu_comp != m.comp_2).sum()),
            "brancos": int((m.bu_brancos != m.brancos_2).sum()),
            "nulos": int((m.bu_nulos != m.nulos_2).sum()),
            "validos(a+b)": int((m.a_2 + m.b_2 != m.validos_2).sum()),
        }
    s2 = s2.drop(columns=[c for c in ("nm_municipio", "nr_local") if c in s2])
    base = s1.merge(s2, on=CHAVE, how="outer", indicator=True)
    chk["secoes_t1"], chk["secoes_t2"] = int(len(s1)), int(len(s2))
    chk["juncao"] = base["_merge"].value_counts().astype(int).to_dict()
    base = base.drop(columns="_merge")

    # --- verificações de integridade por seção (anotadas; nada é descartado) ---
    t1 = base.aptos_1.notna()
    chk["t1_comp_igual_soma_votos_csv"] = int(((base.a_1 + base.b_1 + base.o_1 + base.bn_csv_1) == base.comp_1)[t1].sum())
    chk["t1_comp_diferente_soma_votos_csv"] = int(((base.a_1 + base.b_1 + base.o_1 + base.bn_csv_1) != base.comp_1)[t1].sum())
    chk["t1_abst_tse_diferente_aptos_menos_comp"] = int((base.abst_tse_1 != base.abst_1)[t1].sum())
    ambos = base.aptos_1.notna() & base.aptos_2.notna()
    base["aptos_iguais"] = ambos & (base.aptos_1 == base.aptos_2)
    chk["secoes_nos_dois_turnos"] = int(ambos.sum())
    chk["secoes_aptos_diferentes_entre_turnos"] = int((ambos & ~base.aptos_iguais).sum())
    chk["soma_abs_dif_aptos"] = int((base.aptos_2 - base.aptos_1).abs()[ambos].sum())
    chk["secoes_nao_instaladas_t1"] = int((base.instalada_1 == "Não").sum())
    chk["secoes_nao_instaladas_t2"] = int((base.instalada_2 == "Não").sum())
    chk["secoes_anuladas_t1"] = int((base.anulada_1 == "Sim").sum())
    chk["secoes_anuladas_t2"] = int((base.anulada_2 == "Sim").sum())
    chk["duplicatas_chave"] = int(base.duplicated(CHAVE).sum())
    for t in (1, 2):
        if f"a_{t}" in base:
            sel = base[f"a_{t}"].notna()
            chk[f"totais_t{t}"] = {k: int(base.loc[sel if k in ("a", "b") else base[f"aptos_{t}"].notna(), f"{k}_{t}"].sum())
                                   for k in ["aptos", "comp", "validos", "bn", "abst", "a", "b"] + (["o"] if t == 1 else [])}
    base["exterior"] = base.uf == "ZZ"
    return base, chk


def municipios(base: pd.DataFrame, ano: int) -> pd.DataFrame:
    soma = [c for c in base.columns if c.endswith(("_1", "_2")) and pd.api.types.is_numeric_dtype(base[c])
            and not c.startswith(("nr_", "bu_"))]
    g = base.groupby(["uf", "cd_mun"], as_index=False).agg(
        nm_municipio=("nm_municipio", "first"), n_secoes=("secao", "size"),
        **{c: (c, "sum") for c in soma})
    return g


def main(anos=(2026, 2022, 2018)) -> None:
    for ano in anos:
        base, chk = montar(ano)
        base.to_parquet(INTERIM / f"secoes_{ano}.parquet", index=False)
        mun = municipios(base, ano)
        if ano == 2026:
            # 2º turno por candidato, por município: JSON do sistema de divulgação (completo)
            t2 = pd.read_parquet(INTERIM / "t2_municipios_2026.parquet")
            t2 = t2.assign(uf=t2.uf.str.upper(), cd_mun=t2.cd_mun_tse.astype(int))
            if chk.get("fonte_t2_candidatos", "").startswith("votacao_secao"):
                # conferência: soma por município do arquivo por seção × JSON do sistema de divulgação
                c = mun[["uf", "cd_mun", "a_2", "b_2"]].merge(
                    t2[["uf", "cd_mun", "lula", "flavio"]], on=["uf", "cd_mun"], how="inner")
                chk["municipios_div_votacao_secao_vs_json"] = {"municipios": int(len(c)),
                                                               "lula": int((c.a_2 != c.lula).sum()),
                                                               "flavio": int((c.b_2 != c.flavio).sum())}
            mun = mun.drop(columns=[c for c in ("a_2", "b_2") if c in mun])
            mun = mun.merge(t2[["uf", "cd_mun", "cd_ibge", "capital", "lula", "flavio", "aptos",
                                "comparecimento", "validos", "brancos", "nulos"]]
                            .rename(columns={"lula": "a_2", "flavio": "b_2", "aptos": "json_aptos",
                                             "comparecimento": "json_comp", "validos": "json_validos",
                                             "brancos": "json_brancos", "nulos": "json_nulos"}),
                            on=["uf", "cd_mun"], how="outer", indicator=True)
            chk["municipios_juncao_json"] = mun["_merge"].value_counts().astype(int).to_dict()
            mun = mun.drop(columns="_merge")
            chk["municipios_div_json_vs_detalhe"] = {
                "aptos": int((mun.json_aptos != mun.aptos_2).sum()),
                "comparecimento": int((mun.json_comp != mun.comp_2).sum()),
                "validos": int((mun.json_validos != mun.validos_2).sum()),
                "brancos": int((mun.json_brancos != mun.brancos_2).sum()),
                "nulos": int((mun.json_nulos != mun.nulos_2).sum()),
            }
        mun.to_parquet(INTERIM / f"municipios_{ano}.parquet", index=False)
        mun.to_csv(DERIVADOS / f"municipios_{ano}.csv", index=False)
        salvar_json(chk, INTEGRIDADE / f"verificacoes_base_{ano}.json")
        print(ano, chk)


if __name__ == "__main__":
    import sys
    main(tuple(int(x) for x in sys.argv[1:]) or (2026, 2022, 2018))
