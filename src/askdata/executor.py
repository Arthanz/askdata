"""Safe SQL execution: SELECT-only, row-limited, timed."""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field

import duckdb
import pandas as pd

# Belt-and-suspenders on top of opening the DB read-only.
FORBIDDEN = re.compile(
    r"\b(insert|update|delete|drop|create|alter|attach|detach|copy|export|import|"
    r"pragma|call|install|load|set|vacuum)\b",
    re.IGNORECASE,
)


@dataclass
class QueryResult:
    sql: str
    df: pd.DataFrame | None = None
    error: str | None = None
    truncated: bool = False
    seconds: float = 0.0

    @property
    def ok(self) -> bool:
        return self.error is None


def execute(con: duckdb.DuckDBPyConnection, sql: str, row_limit: int = 500) -> QueryResult:
    sql = sql.strip().rstrip(";")
    if FORBIDDEN.search(sql):
        return QueryResult(sql=sql, error="Rejected: only read-only SELECT queries are allowed.")
    if ";" in sql:
        return QueryResult(sql=sql, error="Rejected: multiple statements are not allowed.")
    start = time.perf_counter()
    try:
        df = con.execute(sql).fetch_df()
    except Exception as e:  # duckdb raises many exception types; message is what matters
        return QueryResult(sql=sql, error=f"{type(e).__name__}: {e}", seconds=time.perf_counter() - start)
    seconds = time.perf_counter() - start
    truncated = len(df) > row_limit
    if truncated:
        df = df.head(row_limit)
    return QueryResult(sql=sql, df=df, truncated=truncated, seconds=seconds)
