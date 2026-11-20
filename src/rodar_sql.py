"""Executa os scripts da pasta sql/ no DuckDB e salva os resultados em sql/resultados/.
Uso: python src/rodar_sql.py"""
from pathlib import Path
import duckdb

BASE = Path(__file__).resolve().parents[1]
con = duckdb.connect()
con.execute(f"SET file_search_path = '{BASE.as_posix()}'")
for arq in sorted((BASE / "sql").glob("*.sql")):
    sql = arq.read_text(encoding="utf-8")
    if arq.name.startswith("00"):
        con.execute(sql)
        print(f"{arq.name}: tabelas criadas")
        continue
    df = con.execute(sql).df()
    df.to_csv(BASE / "sql" / "resultados" / f"{arq.stem}.csv", index=False)
    print(f"\n== {arq.name} ({len(df)} linhas) ==")
    print(df.tail(8).to_string(index=False) if len(df) > 20 else df.to_string(index=False))
