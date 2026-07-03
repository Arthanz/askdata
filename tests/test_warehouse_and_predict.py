from pathlib import Path

import duckdb

from askdata.load_data import build as build_db
from askdata.warehouse import build as build_warehouse

from predict.review_risk import FEATURES_SQL, generate_sample


def test_warehouse_builds_star_schema(tmp_path):
    # own DB file: the shared db_path has a session-scoped read-only connection
    # open, and DuckDB rejects mixing read-only and read-write on one file
    path = tmp_path / "wh.duckdb"
    build_db(path, olist_dir=Path("/nonexistent"))
    build_warehouse(path)
    con = duckdb.connect(str(path), read_only=True)
    tables = {r[0] for r in con.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_schema = 'dw'"
    ).fetchall()}
    assert {"fact_order_items", "dim_customer", "dim_product", "dim_seller",
            "dim_date", "dim_payment", "mart_delivery_performance",
            "mart_review_health"} <= tables
    n_fact = con.execute("SELECT count(*) FROM dw.fact_order_items").fetchone()[0]
    n_items = con.execute("SELECT count(*) FROM order_items").fetchone()[0]
    assert n_fact == n_items  # order-item grain, no fan-out from payments/reviews
    assert con.execute("SELECT count(*) FROM dw.mart_review_health").fetchone()[0] > 0
    con.close()


def test_feature_query_runs_on_db(db_path):
    con = duckdb.connect(str(db_path), read_only=True)
    df = con.execute(FEATURES_SQL).fetch_df()
    con.close()
    assert len(df) > 100
    assert set(df["low_review"].unique()) <= {0, 1}
    assert df["order_id"].is_unique  # one row per order


def test_synthetic_sample_has_signal():
    df = generate_sample(2000)
    late = df[df.delivery_delay_days > 5].low_review.mean()
    on_time = df[df.delivery_delay_days <= 0].low_review.mean()
    assert late > on_time  # lateness drives bad reviews
