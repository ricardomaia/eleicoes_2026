"""Etapa 1 — Reconciliação nacional e limites aritméticos das transferências.

Nada aqui depende de modelo estatístico: são somas, identidades contábeis e
limites de Fréchet calculados em quatro níveis de agregação (nacional, UF,
município, seção). Quanto mais fina a unidade, mais estreitos os limites.

Saídas em resultados/tabelas/:
  01_reconciliacao_nacional.csv     tabela T1 × T2 × diferença
  01_conferencia_oficial.csv        totais calculados × relatórios oficiais
  01_identidades.csv                identidades contábeis verificadas
  01_limites_<nivel>.csv            limites por célula da matriz de transição
  01_quantidades_minimas.csv        quantidades que a aritmética obriga a existir
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from comum import INTERIM, TABELAS, salvar_json
from fluxos import COLUNAS, LINHAS_BASE, LINHAS_DETALHADAS, margens, tabela_limites

# Valores dos documentos oficiais, transcritos para conferência:
# 1º turno: Relatório Resultado da Totalização, TSE/SISTOT, 07/10/2026 16:37:18
#           (arquivo 6257_BR_BRASIL_2026_T1_PRESIDENTE.pdf).
# 2º turno: sistema de divulgação, br-c0001-e006258-u.json, gerado 25/10/2026 23:27:02,
#           totalização final ("tf":"s"). O relatório PDF do 2º turno ainda não
#           estava publicado em 26/10/2026.
OFICIAL_T1 = {"aptos": 158_745_502, "comparecimento": 125_275_835, "abstencao_tse": 33_469_244,
              "aptos_secoes_nao_instaladas": 423, "validos": 119_300_788, "brancos": 2_300_798,
              "nulos": 3_674_249, "nulos_tecnicos": 5_246, "lula": 53_879_538, "flavio": 56_104_503}


def carregar():
    sec = pd.read_parquet(INTERIM / "secoes_2026.parquet")
    mun = pd.read_parquet(INTERIM / "municipios_2026.parquet")
    br = pd.read_parquet(INTERIM / "t2_agregados_2026.parquet").query("tpabr=='br'").iloc[0]
    return sec, mun, br


def reconciliacao(sec, br) -> pd.DataFrame:
    s = sec.sum(numeric_only=True)
    t1 = {
        "Lula": s.a_1, "Flávio Bolsonaro": s.b_1, "Outros candidatos": s.o_1,
        "Votos válidos": s.validos_1, "Votos brancos": s.brancos_1,
        "Votos nulos (inclui nulos técnicos)": s.bn_1 - s.brancos_1,
        "Abstenções (aptos − comparecimento)": s.abst_1,
        "Comparecimento": s.comp_1, "Eleitores aptos": s.aptos_1,
    }
    t2 = {
        "Lula": br.lula, "Flávio Bolsonaro": br.flavio, "Outros candidatos": 0,
        "Votos válidos": s.validos_2, "Votos brancos": s.brancos_2,
        "Votos nulos (inclui nulos técnicos)": s.bn_2 - s.brancos_2,
        "Abstenções (aptos − comparecimento)": s.abst_2,
        "Comparecimento": s.comp_2, "Eleitores aptos": s.aptos_2,
    }
    df = pd.DataFrame({"primeiro_turno": t1, "segundo_turno": t2})
    df["diferenca"] = df.segundo_turno - df.primeiro_turno
    df["pct_aptos_t1"] = 100 * df.primeiro_turno / s.aptos_1
    df["pct_aptos_t2"] = 100 * df.segundo_turno / s.aptos_2
    v1, v2 = s.validos_1, s.validos_2
    df.loc[["Lula", "Flávio Bolsonaro", "Outros candidatos"], "pct_validos_t1"] = 100 * df.primeiro_turno / v1
    df.loc[["Lula", "Flávio Bolsonaro", "Outros candidatos"], "pct_validos_t2"] = 100 * df.segundo_turno / v2
    return df


def conferencia(sec, br) -> pd.DataFrame:
    s = sec.sum(numeric_only=True)
    nao_inst = sec.loc[sec.instalada_1 == "Não", "aptos_1"].sum()
    calc_t1 = {"aptos": s.aptos_1, "comparecimento": s.comp_1, "abstencao_tse": s.abst_1 - nao_inst,
               "aptos_secoes_nao_instaladas": nao_inst, "validos": s.validos_1, "brancos": s.brancos_1,
               "nulos": s.bn_1 - s.brancos_1, "nulos_tecnicos": s.nominais_1 - s.validos_1,
               "lula": s.a_1, "flavio": s.b_1}
    linhas = [{"turno": 1, "indicador": k, "oficial": v, "calculado": calc_t1[k]} for k, v in OFICIAL_T1.items()]
    calc_t2 = {"aptos": s.aptos_2, "comparecimento": s.comp_2, "validos": s.validos_2,
               "brancos": s.brancos_2, "nulos": s.bn_2 - s.brancos_2}
    of_t2 = {"aptos": br.aptos, "comparecimento": br.comparecimento, "validos": br.validos,
             "brancos": br.brancos, "nulos": br.nulos}
    linhas += [{"turno": 2, "indicador": k, "oficial": of_t2[k], "calculado": v} for k, v in calc_t2.items()]
    linhas += [{"turno": 2, "indicador": "lula + flavio = validos", "oficial": br.validos,
                "calculado": br.lula + br.flavio}]
    df = pd.DataFrame(linhas)
    df["diferenca"] = df.calculado - df.oficial
    df["confere"] = df.diferenca == 0
    return df


def identidades(sec, br) -> pd.DataFrame:
    s = sec.sum(numeric_only=True)
    dL, dF = br.lula - s.a_1, br.flavio - s.b_1
    dV = s.validos_2 - s.validos_1
    regs = [
        ("T1: Lula + Flávio + outros = válidos", s.a_1 + s.b_1 + s.o_1, s.validos_1),
        ("T1: válidos + brancos + nulos = comparecimento", s.validos_1 + s.bn_1, s.comp_1),
        ("T1: comparecimento + abstenção = aptos", s.comp_1 + s.abst_1, s.aptos_1),
        ("T2: Lula + Flávio = válidos", br.lula + br.flavio, s.validos_2),
        ("T2: válidos + brancos + nulos = comparecimento", s.validos_2 + s.bn_2, s.comp_2),
        ("T2: comparecimento + abstenção = aptos", s.comp_2 + s.abst_2, s.aptos_2),
        ("ΔLula + ΔFlávio = outros(T1) + Δválidos", dL + dF, s.o_1 + dV),
        ("Δválidos = −Δ(brancos+nulos) − Δabstenção + Δaptos",
         dV, -(s.bn_2 - s.bn_1) - (s.abst_2 - s.abst_1) + (s.aptos_2 - s.aptos_1)),
    ]
    return pd.DataFrame(regs, columns=["identidade", "lado_esquerdo", "lado_direito"]).assign(
        confere=lambda d: d.lado_esquerdo == d.lado_direito)


def quantidades_minimas(sec, mun) -> pd.DataFrame:
    """Quantidades que a aritmética obriga, somando máx(0, ·) unidade a unidade.

    Em cada unidade:
      votos de Lula no 2T que não podem ter vindo de Lula(1T) nem de outros(1T):
          máx(0, L2 − L1 − O1)  → vieram de Flávio(1T), brancos/nulos(1T), abstenção(1T) ou entrada
      idem para Flávio: máx(0, F2 − F1 − O1)
      votos válidos do 2T que não podem ter vindo de válidos do 1T: máx(0, V2 − V1)
      migração direta mínima Flávio(1T)→Lula(2T): máx(0, F1 + L2 − N)
      migração direta mínima Lula(1T)→Flávio(2T): máx(0, L1 + F2 − N)
    """
    out = []

    def bloco(df, nivel, com_candidatos=True):
        N1 = df.aptos_1
        N2 = df.aptos_2
        N = np.maximum(N1, N2)  # a entrada/saída de cadastro só afrouxa os limites
        reg = {"nivel": nivel, "unidades": len(df),
               "validos_2T_sem_origem_valida_1T": np.clip(df.validos_2 - df.validos_1, 0, None).sum(),
               "comparecimento_2T_sem_origem_comparecimento_1T": np.clip(df.comp_2 - df.comp_1, 0, None).sum()}
        if com_candidatos:
            reg.update({
                "lula_2T_alem_de_lula1T_e_outros1T": np.clip(df.a_2 - df.a_1 - df.o_1, 0, None).sum(),
                "flavio_2T_alem_de_flavio1T_e_outros1T": np.clip(df.b_2 - df.b_1 - df.o_1, 0, None).sum(),
                "min_flavio1T_para_lula2T": np.clip(df.b_1 + df.a_2 - N, 0, None).sum(),
                "min_lula1T_para_flavio2T": np.clip(df.a_1 + df.b_2 - N, 0, None).sum(),
                "unidades_onde_F_para_L_zero_e_inviavel": int((df.b_1 + df.a_2 - N > 0).sum()),
                "unidades_onde_L_para_F_zero_e_inviavel": int((df.a_1 + df.b_2 - N > 0).sum()),
            })
        out.append(reg)

    s = sec.sum(numeric_only=True).to_frame().T
    s["a_2"], s["b_2"] = mun.a_2.sum(), mun.b_2.sum()
    bloco(s, "nacional")
    uf = mun.groupby("uf").sum(numeric_only=True)
    bloco(uf, "UF")
    bloco(mun, "município")
    bloco(sec, "seção (todas; sem divisão por candidato no 2T)", com_candidatos=False)
    am = sec[sec.get("na_amostra_bu", False) == True]  # noqa: E712
    if len(am):
        bloco(am, "seção (amostra de BUs, sem expansão)")
    return pd.DataFrame(out)


def main() -> dict:
    sec, mun, br = carregar()
    rec = reconciliacao(sec, br)
    rec.to_csv(TABELAS / "01_reconciliacao_nacional.csv")
    conf = conferencia(sec, br)
    conf.to_csv(TABELAS / "01_conferencia_oficial.csv", index=False)
    ide = identidades(sec, br)
    ide.to_csv(TABELAS / "01_identidades.csv", index=False)

    # Limites de Fréchet por nível de agregação.
    nac = sec.sum(numeric_only=True).to_frame().T
    nac["a_2"], nac["b_2"] = mun.a_2.sum(), mun.b_2.sum()
    uf = mun.groupby("uf").sum(numeric_only=True)
    tabs = []
    for nome, df, linhas in [("nacional", nac, LINHAS_DETALHADAS), ("uf", uf, LINHAS_DETALHADAS),
                             ("municipio", mun, LINHAS_DETALHADAS)]:
        R, C, nl, nc = margens(df, linhas, COLUNAS)
        t = tabela_limites(R, C, nl, nc, nome)
        t.to_csv(TABELAS / f"01_limites_{nome}.csv", index=False)
        tabs.append(t)
    # Seção (todas): destino só como válidos / brancos+nulos / abstenção.
    R, C, nl, nc = margens(sec.dropna(subset=["aptos_1", "aptos_2"]), LINHAS_DETALHADAS,
                           ["validos_2", "bn_2", "abst_2"])
    t = tabela_limites(R, C, nl, nc, "secao_todas")
    t.to_csv(TABELAS / "01_limites_secao_todas.csv", index=False)
    tabs.append(t)
    am = sec[sec.na_amostra_bu.fillna(False).astype(bool)] if "na_amostra_bu" in sec else sec.iloc[:0]
    if len(am):
        R, C, nl, nc = margens(am, LINHAS_DETALHADAS, COLUNAS)
        t = tabela_limites(R, C, nl, nc, "secao_amostra")
        t.to_csv(TABELAS / "01_limites_secao_amostra.csv", index=False)
        tabs.append(t)
        # Mesma amostra, agregada por município (comparação de granularidade nas mesmas pessoas).
        g = am.groupby(["uf", "cd_mun"]).sum(numeric_only=True)
        R, C, nl, nc = margens(g, LINHAS_DETALHADAS, COLUNAS)
        t = tabela_limites(R, C, nl, nc, "amostra_agregada_municipio")
        t.to_csv(TABELAS / "01_limites_amostra_agregada_municipio.csv", index=False)
        tabs.append(t)
    lim = pd.concat(tabs, ignore_index=True)
    lim.to_csv(TABELAS / "01_limites_todos_niveis.csv", index=False)

    qm = quantidades_minimas(sec, mun)
    qm.to_csv(TABELAS / "01_quantidades_minimas.csv", index=False)

    with pd.option_context("display.width", 200, "display.max_columns", 30, "display.float_format", "{:,.0f}".format):
        print(rec)
        print(conf)
        print(ide)
        print(qm.T)
        chave = lim[(lim.origem.isin(["b_1", "a_1"])) & (lim.destino.isin(["a_2", "b_2"]))]
        print(chave[["nivel", "origem", "destino", "min_votos", "max_votos", "min_taxa", "max_taxa"]]
              .to_string(float_format=lambda x: f"{x:,.4f}"))
    resumo = {"reconciliacao": rec.to_dict(), "quantidades_minimas": qm.to_dict(orient="records")}
    salvar_json(resumo, TABELAS / "01_resumo.json")
    return resumo


if __name__ == "__main__":
    main()
