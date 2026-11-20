"""
Coleta dos dados abertos do Banco Central sobre o Pix e meios de pagamento.

Uso (na pasta do projeto):
    python src/coleta.py            # baixa tudo
    python src/coleta.py fraudes    # baixa só uma tabela (ver TABELAS)

Fonte: API Olinda do BCB (OData). Licença dos dados: ODbL.
Comportamento da API verificado em 11/11/2026:
  - O parâmetro de data (Database / DataBase / Data / AnoMes) é a data INICIAL:
    a API devolve tudo DAQUELE mês em diante, não só aquele mês.
  - Para pegar um único mês usamos $filter=AnoMes eq AAAAMM.
  - Algumas chamadas levam mais de 1 minuto; por isso o timeout é alto.
"""
import sys
import time
from datetime import date
from pathlib import Path

import pandas as pd
import requests

RAW = Path(__file__).resolve().parents[1] / "data" / "raw"
PIX = "https://olinda.bcb.gov.br/olinda/servico/Pix_DadosAbertos/versao/v1/odata/"
MPV = "https://olinda.bcb.gov.br/olinda/servico/MPV_DadosAbertos/versao/v1/odata/"
INICIO = (2020, 11)  # lançamento do Pix


def baixar(url: str, tentativas: int = 4) -> pd.DataFrame:
    """Faz uma chamada à API e devolve um DataFrame. Tenta de novo se falhar."""
    for i in range(1, tentativas + 1):
        try:
            r = requests.get(url, timeout=300)
            r.raise_for_status()
            return pd.DataFrame(r.json()["value"])
        except Exception as e:  # rede instável ou erro 500 do servidor
            print(f"   tentativa {i} falhou: {e}")
            time.sleep(5 * i)
    raise RuntimeError(f"Não foi possível baixar: {url}")


def meses():
    """Lista (ano, mes) de INICIO até o mês atual."""
    hoje = date.today()
    a, m = INICIO
    while (a, m) <= (hoje.year, hoje.month):
        yield a, m
        a, m = (a + 1, 1) if m == 12 else (a, m + 1)


def salvar(df: pd.DataFrame, nome: str):
    RAW.mkdir(parents=True, exist_ok=True)
    df.to_csv(RAW / f"{nome}.csv", index=False, encoding="utf-8")
    print(f"OK {nome}.csv: {len(df):,} linhas")


def por_mes(recurso: str, param: str, nome: str):
    """Tabelas grandes: uma chamada por mês, para não estourar o servidor."""
    partes = []
    for a, m in meses():
        am = f"{a}{m:02d}"
        print(f"  {nome} {am}")
        url = (f"{PIX}{recurso}({param}=@p)?@p='{am}'"
               f"&$filter=AnoMes eq {am}&$format=json")
        df = baixar(url)
        if not df.empty:
            partes.append(df)
    salvar(pd.concat(partes, ignore_index=True), nome)


def transacoes():
    por_mes("EstatisticasTransacoesPix", "Database", "pix_transacoes")


def municipios():
    por_mes("TransacoesPixPorMunicipio", "DataBase", "pix_municipios")


def recebedor():
    url = f"{PIX}CnaePorteRecebedor(Database=@p)?@p='202011'&$format=json"
    salvar(baixar(url), "pix_recebedor_cnae_porte")


def fraudes():
    url = f"{PIX}EstatisticasFraudesPix(Database=@p)?@p='202011'&$format=json"
    salvar(baixar(url).sort_values("AnoMes"), "pix_fraudes_med")


def usuarios():
    url = f"{PIX}PixUsuariosCadastradosDICT?$format=json"
    salvar(baixar(url).sort_values("DataGraficosPix"), "pix_usuarios_dict")


def chaves():
    """Estoque de chaves no último dia de cada mês, por instituição."""
    partes = []
    for a, m in meses():
        fim = (pd.Timestamp(a, m, 1) + pd.offsets.MonthEnd(0)).date()
        if fim > date.today():
            continue
        print(f"  pix_chaves {fim}")
        url = (f"{PIX}ChavesPix(Data=@p)?@p='{fim}'"
               f"&$filter=Data eq {fim}&$format=json")
        df = baixar(url)
        if not df.empty:
            partes.append(df)
    salvar(pd.concat(partes, ignore_index=True), "pix_chaves")


def meios_pagamento():
    """Pix x TED x boleto x cheque (mensal) e cartões/saques (trimestral).
    Unidades do BCB: quantidade em milhares, valor em R$ milhões."""
    url = f"{MPV}MeiosdePagamentosMensalDA(AnoMes=@p)?@p='201901'&$format=json"
    salvar(baixar(url).sort_values("AnoMes"), "meios_pagamento_mensal")
    url = (f"{MPV}MeiosdePagamentosTrimestralDA(trimestre=@p)"
           f"?@p='20191'&$format=json")
    salvar(baixar(url).sort_values("datatrimestre"), "meios_pagamento_trimestral")


TABELAS = {
    "usuarios": usuarios,
    "fraudes": fraudes,
    "meios_pagamento": meios_pagamento,
    "recebedor": recebedor,
    "municipios": municipios,
    "chaves": chaves,
    "transacoes": transacoes,   # a maior: ~15 mil linhas por mês
}

if __name__ == "__main__":
    escolhidas = sys.argv[1:] or list(TABELAS)
    for t in escolhidas:
        print(f"== {t} ==")
        TABELAS[t]()
    (RAW / "_coleta.txt").write_text(f"Coleta realizada em {date.today()}\n")
