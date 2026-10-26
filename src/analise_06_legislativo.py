"""Etapa 6 — H4: coerência entre votação legislativa e presidencial.

Fontes: votacao_secao_2026_<UF>.zip (Deputado Federal e Senador, 1º turno, por
seção), votacao_candidato_munzona_2026 (situação de eleito → cadeiras),
votacao_partido_munzona_2022/2018 (comparação histórica, por município).

Classificação dos partidos em blocos (usada só para agrupar; PL e a federação
do PT são analisados isoladamente em todas as tabelas):
  esquerda: PT, PV, PCdoB (Federação Brasil da Esperança), PSOL, Rede, PSB, PDT,
            UP, PSTU, PCO, PCB
  centro:   PSD, MDB, Podemos, PSDB, Cidadania, Avante, PRD, Solidariedade,
            Mobiliza, Democrata, Agir
  direita:  PL, PP, União Brasil, Republicanos, Novo, Missão, DC, PRTB
Base: classificação ideológica de partidos brasileiros por especialistas
(Bolognesi, Ribeiro e Codato, 2023, Dados 66(2)); partidos criados ou
renomeados depois (Missão, PRD, Mobiliza, Democrata) foram posicionados por
este estudo e são uma hipótese. Partidos de centro NÃO são tratados como
direita. Sensibilidade: resultados também com "direita estrita" = PL, PP,
União, Republicanos, Novo.

Análises:
  1. votos e cadeiras por partido (Câmara e Senado);
  2. por seção (todas as 499 mil): participação do PL nos votos válidos para
     deputado federal × participação de Flávio e de Lula; frequência de
     combinações aparentemente divergentes;
  3. inferência ecológica (mesmo estimador do Modelo A): como os eleitores de
     cada bloco para deputado federal votaram para presidente no 1º turno
     (todas as seções) e no 2º turno (amostra de BUs). Isso estima o voto
     dividido (split-ticket) — com as mesmas limitações da inferência ecológica;
  4. comparação histórica municipal: distância entre o voto presidencial do
     candidato de direita e o voto do seu partido para deputado (2018: PSL;
     2022 e 2026: PL).
"""
from __future__ import annotations

import zipfile

import duckdb
import numpy as np
import pandas as pd

from comum import INTERIM, RAW, SEMENTE, TABELAS, UFS, salvar_json
from ei import ajustar, bootstrap_conglomerados, preparar

ESQ = {"13", "43", "65", "50", "18", "40", "12", "80", "16", "29", "21"}
CEN = {"55", "15", "20", "45", "23", "70", "25", "77", "33", "35", "36"}
DIR = {"22", "11", "44", "10", "30", "14", "27", "28"}
FE_BRASIL = {"13", "43", "65"}
DIR_ESTRITA = {"22", "11", "44", "10", "30"}


def bloco(p: str) -> str:
    if p == "22":
        return "pl"
    if p in FE_BRASIL:
        return "fe_brasil"
    if p in DIR:
        return "dir_outros"
    if p in CEN:
        return "centro"
    if p in ESQ:
        return "esq_outros"
    return "outros"


def votos_legislativos_secao() -> pd.DataFrame:
    destino = INTERIM / "legislativo_secao_2026.parquet"
    if destino.exists():
        return pd.read_parquet(destino)
    partes = []
    for uf in UFS:
        z = RAW / "2026" / "votacao_secao_uf" / f"votacao_secao_2026_{uf}.zip"
        pasta = RAW / "2026" / "ex" / "vsuf"
        csv = pasta / f"votacao_secao_2026_{uf}.csv"
        if not csv.exists():
            with zipfile.ZipFile(z) as zz:
                zz.extract(csv.name, pasta)
        q = f"""
        select SG_UF uf, CD_MUNICIPIO::INT cd_mun, NR_ZONA::INT zona, NR_SECAO::INT secao,
               CD_CARGO::INT cargo,
               case when NR_VOTAVEL in ('95','96','97') then 'bn' else substr(NR_VOTAVEL,1,2) end partido,
               sum(QT_VOTOS::BIGINT) votos
        from read_csv('{csv.as_posix()}', delim=';', encoding='latin-1', header=true, all_varchar=true)
        where NR_TURNO='1' and CD_CARGO in ('5','6')
        group by all"""
        longo = duckdb.sql(q).df()
        longo["grupo"] = np.where(longo.partido == "bn", "bn", longo.partido.map(bloco))
        longo["dir_estrita"] = longo.partido.isin(DIR_ESTRITA)
        chave = ["uf", "cd_mun", "zona", "secao"]
        dep = longo[longo.cargo == 6].pivot_table(index=chave, columns="grupo", values="votos",
                                                  aggfunc="sum", fill_value=0)
        dep.columns = [f"dep_{c}" for c in dep.columns]
        dep["dep_dir_estrita"] = longo[(longo.cargo == 6) & longo.dir_estrita].groupby(chave).votos.sum()
        sen = longo[longo.cargo == 5]
        sen_t = sen.groupby(chave).votos.sum().rename("sen_votos")
        sen_pl = sen[sen.partido == "22"].groupby(chave).votos.sum().rename("sen_pl")
        sen_bn = sen[sen.partido == "bn"].groupby(chave).votos.sum().rename("sen_bn")
        df = dep.join([sen_t, sen_pl, sen_bn]).fillna(0).reset_index()
        partes.append(df)
        csv.unlink()  # o CSV extraído é grande; o zip original fica guardado
        print(uf, len(df), flush=True)
    out = pd.concat(partes, ignore_index=True)
    out.to_parquet(destino, index=False)
    return out


def cadeiras() -> pd.DataFrame:
    c = next((RAW / "2026" / "ex" / "cmz").glob("*BRASIL*.csv"))
    q = f"""
    select CD_CARGO::INT cargo, NR_PARTIDO partido, any_value(SG_PARTIDO) sigla,
           count(distinct case when DS_SIT_TOT_TURNO like 'ELEITO%' then SQ_CANDIDATO end) eleitos
    from read_csv('{c.as_posix()}', delim=';', encoding='latin-1', header=true, all_varchar=true)
    where CD_CARGO in ('5','6') and NR_TURNO='1'
    group by all"""
    cad = duckdb.sql(q).df()
    p = next((RAW / "2026" / "ex" / "pmz").glob("*BRASIL*.csv"))
    q = f"""
    select CD_CARGO::INT cargo, NR_PARTIDO partido,
           sum(QT_VOTOS_NOMINAIS_VALIDOS::BIGINT + QT_TOTAL_VOTOS_LEG_VALIDOS::BIGINT) votos
    from read_csv('{p.as_posix()}', delim=';', encoding='latin-1', header=true, all_varchar=true)
    where CD_CARGO in ('5','6') and NR_TURNO='1'
    group by all"""
    vot = duckdb.sql(q).df()
    t = vot.merge(cad, on=["cargo", "partido"], how="outer").fillna({"eleitos": 0, "votos": 0})
    t["bloco"] = t.partido.map(bloco)
    t["pct_votos"] = 100 * t.votos / t.groupby("cargo").votos.transform("sum")
    t["pct_cadeiras"] = 100 * t.eleitos / t.groupby("cargo").eleitos.transform("sum")
    return t.sort_values(["cargo", "votos"], ascending=[True, False])


def ei_split(df, origens, destinos, rng, n_boot=50, nome=""):
    linhas = []
    tot = df[origens].sum()
    fluxo = np.zeros((len(origens), len(destinos)))
    boots = []
    for uf, g in df.groupby("uf"):
        R, C, N, ok = preparar(g, origens, destinos)
        X = R / N[:, None]
        B, _, _ = ajustar(X, C)
        tr = g[origens].sum().to_numpy(float)
        fluxo += tr[:, None] * B
        if n_boot:
            bs = bootstrap_conglomerados(X, C, g.cd_mun.to_numpy()[ok], B, n_boot, rng)
            boots.append(tr[None, :, None] * bs)
    taxa = fluxo / tot.to_numpy(float)[:, None]
    sb = np.sum(boots, axis=0) / tot.to_numpy(float)[None, :, None] if boots else None
    for i, o in enumerate(origens):
        for j, d in enumerate(destinos):
            linhas.append({"analise": nome, "origem_legislativo": o, "destino_presidente": d,
                           "taxa": taxa[i, j],
                           "ic95_inf": np.percentile(sb[:, i, j], 2.5) if sb is not None else np.nan,
                           "ic95_sup": np.percentile(sb[:, i, j], 97.5) if sb is not None else np.nan,
                           "votos": fluxo[i, j]})
    return pd.DataFrame(linhas)


def historico_municipal() -> pd.DataFrame:
    out = []
    for ano, num_partido, num_cand in [(2026, "22", "b_1"), (2022, "22", "b_1"), (2018, "17", "b_1")]:
        z = RAW / str(ano) / f"votacao_partido_munzona_{ano}.zip"
        pasta = RAW / str(ano) / "ex" / "pmz"
        with zipfile.ZipFile(z) as zz:
            nome = next(n for n in zz.namelist() if "BRASIL" in n)
            if not (pasta / nome).exists():
                zz.extract(nome, pasta)
        q = f"""
        select SG_UF uf, CD_MUNICIPIO::INT cd_mun,
               sum(case when NR_PARTIDO='{num_partido}' then QT_VOTOS_NOMINAIS_VALIDOS::BIGINT + QT_TOTAL_VOTOS_LEG_VALIDOS::BIGINT else 0 end) partido,
               sum(QT_VOTOS_NOMINAIS_VALIDOS::BIGINT + QT_TOTAL_VOTOS_LEG_VALIDOS::BIGINT) validos_dep
        from read_csv('{(pasta / nome).as_posix()}', delim=';', encoding='latin-1', header=true, all_varchar=true)
        where CD_CARGO='6' and NR_TURNO='1'
        group by all"""
        p = duckdb.sql(q).df()
        mun = pd.read_parquet(INTERIM / f"municipios_{ano}.parquet")[["uf", "cd_mun", "a_1", "b_1", "validos_1", "aptos_1"]]
        m = p.merge(mun, on=["uf", "cd_mun"])
        m = m[m.uf != "ZZ"]
        sh_part = m.partido / m.validos_dep
        sh_pres = m.b_1 / m.validos_1
        w = m.aptos_1
        out.append({"ano": ano, "partido": num_partido, "pct_partido_dep_nacional": 100 * m.partido.sum() / m.validos_dep.sum(),
                    "pct_candidato_direita_pres_1T": 100 * m.b_1.sum() / m.validos_1.sum(),
                    "razao_pres_sobre_partido": (m.b_1.sum() / m.validos_1.sum()) / (m.partido.sum() / m.validos_dep.sum()),
                    "corr_municipal_ponderada": float(np.corrcoef(sh_part, sh_pres)[0, 1]) if False else
                    float(np.cov(sh_part, sh_pres, aweights=w)[0, 1] / np.sqrt(np.cov(sh_part, aweights=w) * np.cov(sh_pres, aweights=w))),
                    "frac_municipios_partido_acima_pres": float((sh_part > sh_pres).mean())})
    return pd.DataFrame(out)


def main():
    rng = np.random.default_rng(SEMENTE)
    leg = votos_legislativos_secao()
    sec = pd.read_parquet(INTERIM / "secoes_2026.parquet")
    d = sec.merge(leg, on=["uf", "cd_mun", "zona", "secao"], how="inner")
    dep_cols = [c for c in d.columns if c.startswith("dep_") and c != "dep_dir_estrita"]
    d["dep_total"] = d[dep_cols].sum(1)
    d["dep_validos"] = d.dep_total - d.dep_bn
    chk = {"secoes_com_legislativo": int(len(d)),
           "secoes_dep_total_diferente_comparecimento": int((d.dep_total != d.comp_1).sum())}
    cad = cadeiras()
    cad.to_csv(TABELAS / "06_votos_cadeiras_partidos.csv", index=False)

    # 2. combinações por seção
    v = d[(d.dep_validos > 0) & (d.validos_1 > 0)].copy()
    v["pl_dep"] = v.dep_pl / v.dep_validos
    v["dir_dep"] = (v.dep_pl + v.dep_dir_outros) / v.dep_validos
    v["lula1"] = v.a_1 / v.validos_1
    v["flavio1"] = v.b_1 / v.validos_1
    v["fe_dep"] = v.dep_fe_brasil / v.dep_validos
    w = v.aptos_1
    combos = []
    for lim_pl in (0.25, 0.30, 0.40):
        for lim_l in (0.50, 0.60):
            m = (v.pl_dep >= lim_pl) & (v.lula1 >= lim_l)
            combos.append({"pl_dep_min": lim_pl, "lula_1T_min": lim_l, "secoes": int(m.sum()),
                           "pct_secoes": 100 * m.mean(), "pct_aptos": 100 * w[m].sum() / w.sum()})
    combos = pd.DataFrame(combos)
    combos.to_csv(TABELAS / "06_combinacoes_divergentes_secao.csv", index=False)
    am = v[v.na_amostra_bu.fillna(False).astype(bool)].copy()
    am["lula2"] = am.a_2 / (am.a_2 + am.b_2)
    combos2 = []
    for lim_pl in (0.25, 0.30, 0.40):
        m = (am.pl_dep >= lim_pl) & (am.lula2 >= 0.5)
        combos2.append({"pl_dep_min": lim_pl, "lula_2T_min": 0.5, "secoes_amostra": int(m.sum()),
                        "pct_secoes_amostra": 100 * m.mean()})
    pd.DataFrame(combos2).to_csv(TABELAS / "06_combinacoes_divergentes_secao_2T_amostra.csv", index=False)

    def cw(a, b, ww):
        return float(np.cov(a, b, aweights=ww)[0, 1] / np.sqrt(np.cov(a, aweights=ww) * np.cov(b, aweights=ww)))
    cors = {"corr_pl_dep_flavio1": cw(v.pl_dep, v.flavio1, w), "corr_pl_dep_lula1": cw(v.pl_dep, v.lula1, w),
            "corr_fe_dep_lula1": cw(v.fe_dep, v.lula1, w), "corr_dir_dep_flavio1": cw(v.dir_dep, v.flavio1, w),
            "pct_nacional_pl_dep": 100 * v.dep_pl.sum() / v.dep_validos.sum(),
            "pct_nacional_flavio1": 100 * v.b_1.sum() / v.validos_1.sum(),
            "pct_nacional_fe_dep": 100 * v.dep_fe_brasil.sum() / v.dep_validos.sum(),
            "pct_nacional_lula1": 100 * v.a_1.sum() / v.validos_1.sum(),
            "pct_nacional_direita_dep": 100 * (v.dep_pl + v.dep_dir_outros).sum() / v.dep_validos.sum(),
            "pct_nacional_dir_estrita_dep": 100 * v.dep_dir_estrita.sum() / v.dep_validos.sum(),
            "pct_nacional_centro_dep": 100 * v.dep_centro.sum() / v.dep_validos.sum(),
            "pct_nacional_esquerda_dep": 100 * (v.dep_fe_brasil + v.dep_esq_outros).sum() / v.dep_validos.sum(),
            "pct_nacional_pl_senado": 100 * v.sen_pl.sum() / (v.sen_votos - v.sen_bn).sum()}
    cors.update(chk)

    # 3. inferência ecológica do voto dividido
    origens = ["dep_pl", "dep_dir_outros", "dep_centro", "dep_fe_brasil", "dep_esq_outros", "dep_bn"]
    if "dep_outros" in d:
        d["dep_bn"] = d.dep_bn + d.dep_outros
    destinos1 = ["a_1", "b_1", "o_1", "bn_1"]
    s1 = d[d.comp_1 > 0].copy()
    # mesma população nas duas pontas: quem votou para deputado é quem compareceu
    s1["bn_1"] = s1.comp_1 - s1.a_1 - s1.b_1 - s1.o_1
    s1["dep_bn"] = s1.comp_1 - s1[origens[:-1]].sum(1)
    e1 = ei_split(s1, origens, destinos1, rng, n_boot=50, nome="dep_federal_1T -> presidente_1T")
    s2 = d[d.na_amostra_bu.fillna(False).astype(bool) & (d.aptos_1 > 0)].copy()
    s2["dep_bn"] = s2.comp_1 - s2[origens[:-1]].sum(1)
    s2["abst_1x"] = s2.aptos_1 - s2.comp_1
    e2 = ei_split(s2, origens + ["abst_1x"], ["a_2", "b_2", "bn_2", "abst_2"], rng, n_boot=50,
                  nome="dep_federal_1T -> presidente_2T (amostra)")
    ei_t = pd.concat([e1, e2])
    ei_t.to_csv(TABELAS / "06_voto_dividido_inferencia_ecologica.csv", index=False)
    hist = historico_municipal()
    hist.to_csv(TABELAS / "06_historico_partido_vs_presidente.csv", index=False)
    salvar_json(cors, TABELAS / "06_resumo.json")
    with pd.option_context("display.width", 250, "display.float_format", "{:,.4f}".format):
        print(cad[cad.cargo == 6].head(15).to_string())
        print(cad[cad.cargo == 5].head(10).to_string())
        print(combos.to_string()); print(pd.DataFrame(combos2).to_string())
        print(cors)
        print(ei_t.to_string())
        print(hist.to_string())


if __name__ == "__main__":
    main()
