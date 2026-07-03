"""Sanity-check the golden set: every gold SQL must execute and return rows.

    python -m eval.validate_golden
"""

from __future__ import annotations

import sys

import duckdb

from askdata.config import Settings
from askdata.executor import execute

from .run import load_golden


def main():
    settings = Settings()
    con = duckdb.connect(str(settings.db_path), read_only=True)
    failures = 0
    for it in load_golden():
        if not it["gold_sql"]:
            print(f"  {it['id']:3s} (unanswerable — no gold SQL)")
            continue
        res = execute(con, it["gold_sql"])
        if not res.ok:
            failures += 1
            print(f"  {it['id']:3s} FAILED: {res.error}")
        elif res.df.empty:
            failures += 1
            print(f"  {it['id']:3s} EMPTY RESULT")
        else:
            preview = res.df.iloc[0].to_dict()
            print(f"  {it['id']:3s} ok  {len(res.df):>4} rows  first: {str(preview)[:80]}")
    con.close()
    if failures:
        sys.exit(f"\n{failures} golden queries failed")
    print("\nAll golden queries valid.")


if __name__ == "__main__":
    main()
