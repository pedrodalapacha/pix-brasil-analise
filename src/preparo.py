"""
Limpeza e preparo: lê data/raw e grava tabelas resumidas em data/processed.
Uso: python src/preparo.py

Decisões de limpeza (documentadas no README):
1. keep_default_na=False: a base usa o texto "NA" como categoria; sem isso o
   pandas transformaria "NA" em valor nulo.
2. Categorias vazias, "NA", "N/D", "Nao disponivel" e "Nao informado" viram
   "Não informado".
3. Meses incompletos são descartados (o mês corrente vem parcial na tabela de
   municípios).
4. Meios de pagamento: quantidade vem em milhares e valor em R$ milhões;
   convertemos para unidades e R$.
"""
from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
RAW, OUT = BASE / "data" / "raw", BASE / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)
SEM_INFO = {"", "NA", "N/D", "Nao disponivel", "Nao informado", "NAO INFORMADO"}


def ler(nome):
    df = pd.read_csv(RAW / f"{nome}.csv", keep_default_na=False, low_memory=False)
    for c in df.select_dtypes("object"):
        df[c] = df[c].where(~df[c].isin(SEM_INFO), "Não informado")
    return df


def data_de(anomes):
    return pd.to_datetime(anomes.astype(str), format="%Y%m")


def salvar(df, nome):
    df.to_csv(OUT / f"{nome}.csv", index=False, encoding="utf-8-sig")
    print(f"{nome}.csv: {len(df):,} linhas")


# ---------- 1. Transações (liquidadas no SPI) ----------
tx = ler("pix_transacoes")
ULTIMO_MES = int(tx["AnoMes"].max())          # último mês completo
tx["Data"] = data_de(tx["AnoMes"])

mensal = tx.groupby(["AnoMes", "Data"], as_index=False)[["QUANTIDADE", "VALOR"]].sum()
mensal["TicketMedio"] = mensal["VALOR"] / mensal["QUANTIDADE"]
mensal["CrescQtdAnual"] = mensal["QUANTIDADE"].pct_change(12)
mensal["CrescValorAnual"] = mensal["VALOR"].pct_change(12)
mensal["DiasNoMes"] = mensal["Data"].dt.days_in_month
mensal["QtdPorDia"] = mensal["QUANTIDADE"] / mensal["DiasNoMes"]

us = ler("pix_usuarios_dict")
us["AnoMes"] = pd.to_datetime(us["DataGraficosPix"]).dt.strftime("%Y%m").astype(int)
us = us.rename(columns={"qtdUsuariosPessoaFisica": "UsuariosPF",
                        "qtdUsuariosPessoaJuridica": "UsuariosPJ",
                        "qtdUsuariosCadastradosDICTTotal": "UsuariosTotal"})
mensal = mensal.merge(us[["AnoMes", "UsuariosPF", "UsuariosPJ", "UsuariosTotal"]],
                      on="AnoMes", how="left")
mensal["TransacoesPorUsuario"] = mensal["QUANTIDADE"] / mensal["UsuariosTotal"]
salvar(mensal, "pix_mensal")

for col, nome in [("NATUREZA", "pix_natureza_mensal"),
                  ("FORMAINICIACAO", "pix_forma_iniciacao_mensal"),
                  ("FINALIDADE", "pix_finalidade_mensal")]:
    g = tx.groupby(["AnoMes", "Data", col], as_index=False)[["QUANTIDADE", "VALOR"]].sum()
    g["PartQtd"] = g["QUANTIDADE"] / g.groupby("AnoMes")["QUANTIDADE"].transform("sum")
    salvar(g, nome)

pf = tx[tx["PAG_PFPJ"] == "PF"].copy()
pf["Ano"] = pf["AnoMes"] // 100
idade = pf.groupby(["Ano", "PAG_IDADE"], as_index=False)[["QUANTIDADE", "VALOR"]].sum()
idade["PartQtd"] = idade["QUANTIDADE"] / idade.groupby("Ano")["QUANTIDADE"].transform("sum")
idade["TicketMedio"] = idade["VALOR"] / idade["QUANTIDADE"]
salvar(idade, "pix_idade_pagador_anual")

tx["Ano"] = tx["AnoMes"] // 100
fluxo = tx.groupby(["Ano", "PAG_REGIAO", "REC_REGIAO"], as_index=False)[["QUANTIDADE", "VALOR"]].sum()
salvar(fluxo, "pix_fluxo_regioes_anual")

# ---------- 2. Meios de pagamento ----------
mp = ler("meios_pagamento_mensal")
longo = []
for meio in ["Pix", "TED", "TEC", "Cheque", "Boleto", "DOC"]:
    longo.append(pd.DataFrame({"AnoMes": mp["AnoMes"].astype(int), "Meio": meio,
                               "Quantidade": mp[f"quantidade{meio}"] * 1_000,
                               "Valor": mp[f"valor{meio}"] * 1_000_000}))
mpl = pd.concat(longo, ignore_index=True)
mpl["Data"] = data_de(mpl["AnoMes"])
mpl["PartQtd"] = mpl["Quantidade"] / mpl.groupby("AnoMes")["Quantidade"].transform("sum")
mpl["PartValor"] = mpl["Valor"] / mpl.groupby("AnoMes")["Valor"].transform("sum")
salvar(mpl, "meios_pagamento_mensal")

mt = ler("meios_pagamento_trimestral")
nomes = {"Pix": "Pix", "TED": "TED", "TEC": "TEC", "Cheque": "Cheque", "Boleto": "Boleto",
         "DOC": "DOC", "CartaoCredito": "Cartão de crédito", "CartaoDebito": "Cartão de débito",
         "CartaoPrePago": "Cartão pré-pago", "TransIntrabancaria": "Transferência intrabancária",
         "Convenios": "Convênios", "DebitoDireto": "Débito direto", "Saques": "Saques"}
longo = []
for k, v in nomes.items():
    longo.append(pd.DataFrame({"Trimestre": pd.to_datetime(mt["datatrimestre"]), "Meio": v,
                               "Quantidade": mt[f"quantidade{k}"] * 1_000,
                               "Valor": mt[f"valor{k}"] * 1_000_000}))
mtl = pd.concat(longo, ignore_index=True)
mtl["PartQtd"] = mtl["Quantidade"] / mtl.groupby("Trimestre")["Quantidade"].transform("sum")
mtl["PartValor"] = mtl["Valor"] / mtl.groupby("Trimestre")["Valor"].transform("sum")
salvar(mtl, "meios_pagamento_trimestral")

# ---------- 3. Municípios e estados ----------
mu = ler("pix_municipios")
mu = mu[mu["AnoMes"] <= ULTIMO_MES].copy()
mu["QtdPagador"] = mu["QT_PagadorPF"] + mu["QT_PagadorPJ"]
mu["ValorPagador"] = mu["VL_PagadorPF"] + mu["VL_PagadorPJ"]
uf = mu.groupby(["AnoMes", "Estado", "Regiao"], as_index=False)[
    ["QtdPagador", "ValorPagador", "QT_PagadorPF", "VL_PagadorPF", "QT_PES_PagadorPF",
     "QT_RecebedorPJ", "VL_RecebedorPJ", "QT_PES_RecebedorPJ"]].sum()
uf["Data"] = data_de(uf["AnoMes"])
uf["PixPorPagadorPF"] = uf["QT_PagadorPF"] / uf["QT_PES_PagadorPF"]
salvar(uf, "pix_uf_mensal")

ult12 = sorted(mu["AnoMes"].unique())[-12:]
m12 = mu[mu["AnoMes"].isin(ult12) & (mu["Estado"] != "Não informado")]
mun = m12.groupby(["Municipio_Ibge", "Municipio", "Estado", "Regiao"], as_index=False).agg(
    QtdPagadorPF=("QT_PagadorPF", "sum"), ValorPagadorPF=("VL_PagadorPF", "sum"),
    PagadoresPF_MediaMensal=("QT_PES_PagadorPF", "mean"),
    QtdRecebedorPJ=("QT_RecebedorPJ", "sum"), ValorRecebedorPJ=("VL_RecebedorPJ", "sum"),
    RecebedoresPJ_MediaMensal=("QT_PES_RecebedorPJ", "mean"))
mun["PixMensalPorPagadorPF"] = mun["QtdPagadorPF"] / 12 / mun["PagadoresPF_MediaMensal"]
mun["TicketMedioPF"] = mun["ValorPagadorPF"] / mun["QtdPagadorPF"]
salvar(mun, "pix_municipio_ultimos_12m")

# ---------- 4. Recebedores por setor e porte ----------
rc = ler("pix_recebedor_cnae_porte")
rc = rc[rc["AnoMes"] <= ULTIMO_MES].copy()
rc["Ano"] = rc["AnoMes"] // 100
# mesmatit = "S" marca transferências entre contas do mesmo titular. Guardamos a
# coluna para poder excluí-las: não são pagamentos, e o próprio BCB as exclui
# nas Estatísticas de Pagamentos por Atividade Econômica.
setor = rc[rc["tipopessoa"] == "PJ"].groupby(
    ["Ano", "cnssecao", "porte", "mei", "mesmatit"], as_index=False)[["qtlanliq", "vllanliq"]].sum()
setor = setor.rename(columns={"cnssecao": "Setor", "porte": "Porte", "mei": "MEI",
                              "mesmatit": "MesmaTitularidade",
                              "qtlanliq": "Quantidade", "vllanliq": "Valor"})
salvar(setor, "pix_setor_porte_anual")

# Forma de iniciação por setor (só pagamentos a empresas, sem mesma titularidade)
sf = rc[(rc["tipopessoa"] == "PJ") & (rc["mesmatit"] == "N")].groupby(
    ["Ano", "cnssecao", "formainic"], as_index=False)["qtlanliq"].sum()
sf = sf.rename(columns={"cnssecao": "Setor", "formainic": "FormaIniciacao", "qtlanliq": "Quantidade"})
sf["PartNoSetor"] = sf["Quantidade"] / sf.groupby(["Ano", "Setor"])["Quantidade"].transform("sum")
salvar(sf, "pix_setor_forma_iniciacao_anual")

tit = rc.groupby(["Ano", "mesmatit"], as_index=False)[["qtlanliq", "vllanliq"]].sum()
tit = tit.rename(columns={"mesmatit": "MesmaTitularidade", "qtlanliq": "Quantidade", "vllanliq": "Valor"})
tit["PartQtd"] = tit["Quantidade"] / tit.groupby("Ano")["Quantidade"].transform("sum")
tit["PartValor"] = tit["Valor"] / tit.groupby("Ano")["Valor"].transform("sum")
salvar(tit, "pix_mesma_titularidade_anual")

# ---------- 5. Chaves ----------
ch = ler("pix_chaves")
tipo = ch.groupby(["Data", "TipoChave", "NaturezaUsuario"], as_index=False)["qtdChaves"].sum()
salvar(tipo, "pix_chaves_tipo_mensal")
inst = ch.groupby(["Data", "ISPB", "Nome", "Segmento"], as_index=False)["qtdChaves"].sum()
inst["Part"] = inst["qtdChaves"] / inst.groupby("Data")["qtdChaves"].transform("sum")
conc = inst.groupby("Data").agg(
    Instituicoes=("ISPB", "nunique"), ChavesTotal=("qtdChaves", "sum"),
    HHI=("Part", lambda s: (s * 100).pow(2).sum()),
    Top5=("Part", lambda s: s.nlargest(5).sum())).reset_index()
salvar(conc, "pix_chaves_concentracao_mensal")
salvar(inst[inst["Data"] == inst["Data"].max()].sort_values("qtdChaves", ascending=False),
       "pix_chaves_instituicao_ultimo_mes")

# ---------- 6. Fraudes (MED) ----------
fr = ler("pix_fraudes_med").sort_values("AnoMes")
fr["Data"] = data_de(fr["AnoMes"])
fr["TaxaAceitacao"] = fr["Qtdecontestacoesaceitas"] / fr["QtdePixcontestados"]
fr["TicketFraudeAceita"] = fr["ValorPixcontestadosaceitos"] / fr["Qtdecontestacoesaceitas"]
salvar(fr, "pix_fraudes_med")
print("Último mês completo:", ULTIMO_MES)
