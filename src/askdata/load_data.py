"""Build data/askdata.duckdb.

Uses the full Olist CSVs if they exist in data/olist/ (download from
https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce), otherwise
generates the built-in synthetic sample. Run: python -m askdata.load_data
"""

from __future__ import annotations

import sys
from pathlib import Path

import duckdb

from .config import PROJECT_ROOT, Settings

OLIST_DIR = PROJECT_ROOT / "data" / "olist"
OLIST_FILES = {
    "olist_customers_dataset.csv": "customers",
    "olist_orders_dataset.csv": "orders",
    "olist_order_items_dataset.csv": "order_items",
    "olist_order_payments_dataset.csv": "order_payments",
    "olist_order_reviews_dataset.csv": "order_reviews",
    "olist_products_dataset.csv": "products",
    "olist_sellers_dataset.csv": "sellers",
    "product_category_name_translation.csv": "category_translation",
}


def build(db_path: Path | None = None, olist_dir: Path = OLIST_DIR) -> Path:
    db_path = db_path or Settings().db_path
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()
    con = duckdb.connect(str(db_path))

    have_olist = olist_dir.is_dir() and all((olist_dir / f).exists() for f in OLIST_FILES)
    if have_olist:
        print(f"Loading full Olist dataset from {olist_dir} ...")
        for csv, table in OLIST_FILES.items():
            con.execute(
                f'CREATE TABLE "{table}" AS SELECT * FROM read_csv_auto(?)',
                [str(olist_dir / csv)],
            )
    else:
        print("Olist CSVs not found — building the synthetic sample (same schema).")
        from .sample_data import generate

        for table, df in generate().items():
            con.register("_df", df)
            con.execute(f'CREATE TABLE "{table}" AS SELECT * FROM _df')
            con.unregister("_df")

    for (table,) in con.execute("SHOW TABLES").fetchall():
        n = con.execute(f'SELECT count(*) FROM "{table}"').fetchone()[0]
        print(f"  {table:22s} {n:>8,} rows")
    con.close()
    print(f"Done -> {db_path}")
    return db_path


if __name__ == "__main__":
    build(Path(sys.argv[1]) if len(sys.argv) > 1 else None)
