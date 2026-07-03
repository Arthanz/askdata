"""Build the dimensional warehouse (Kimball star schema) inside askdata.duckdb.

Creates a `dw` schema — dims, a fact table at order-item grain, and the marts
the dashboard reads — from the raw Olist tables. Kept in a separate schema so
the NL agent's context (raw `main` tables) is unaffected. The SQL is standard
enough to port to BigQuery unchanged apart from date functions.

Run after load_data:  python -m askdata.warehouse
"""

from __future__ import annotations

import sys
from pathlib import Path

import duckdb

from .config import Settings

DDL = """
CREATE SCHEMA IF NOT EXISTS dw;

CREATE OR REPLACE TABLE dw.dim_customer AS
SELECT customer_id, customer_unique_id, customer_city, customer_state
FROM customers;

CREATE OR REPLACE TABLE dw.dim_product AS
SELECT p.product_id,
       coalesce(t.product_category_name_english, p.product_category_name, 'unknown') AS category,
       p.product_weight_g AS weight_g,
       p.product_photos_qty AS photos_qty
FROM products p
LEFT JOIN category_translation t USING (product_category_name);

CREATE OR REPLACE TABLE dw.dim_seller AS
SELECT seller_id, seller_city, seller_state FROM sellers;

CREATE OR REPLACE TABLE dw.dim_date AS
SELECT cast(gs AS date)      AS date_key,
       year(gs)              AS year,
       quarter(gs)           AS quarter,
       month(gs)             AS month,
       dayofweek(gs)         AS dow
FROM generate_series(
    (SELECT cast(min(order_purchase_timestamp) AS timestamp) FROM orders),
    (SELECT cast(max(order_purchase_timestamp) AS timestamp) FROM orders),
    INTERVAL 1 DAY) t(gs);

-- junk dimension: one row per (payment_type, installments) combination
CREATE OR REPLACE TABLE dw.dim_payment AS
SELECT row_number() OVER (ORDER BY payment_type, payment_installments) AS payment_key,
       payment_type, payment_installments
FROM (SELECT DISTINCT payment_type, payment_installments FROM order_payments);

CREATE OR REPLACE TABLE dw.fact_order_items AS
WITH first_payment AS (
    SELECT order_id, payment_type, payment_installments
    FROM order_payments
    QUALIFY row_number() OVER (PARTITION BY order_id ORDER BY payment_sequential) = 1
), first_review AS (
    SELECT order_id, review_score
    FROM order_reviews
    QUALIFY row_number() OVER (PARTITION BY order_id ORDER BY review_creation_date DESC) = 1
)
SELECT oi.order_id,
       oi.order_item_id,
       o.customer_id,
       oi.product_id,
       oi.seller_id,
       cast(o.order_purchase_timestamp AS date) AS date_key,
       dp.payment_key,
       o.order_status,
       oi.price,
       oi.freight_value,
       date_diff('day', o.order_estimated_delivery_date, o.order_delivered_customer_date)
           AS delivery_delay_days,   -- positive = late
       fr.review_score
FROM order_items oi
JOIN orders o USING (order_id)
LEFT JOIN first_payment fp USING (order_id)
LEFT JOIN dw.dim_payment dp
       ON fp.payment_type = dp.payment_type
      AND fp.payment_installments = dp.payment_installments
LEFT JOIN first_review fr USING (order_id);

CREATE OR REPLACE VIEW dw.mart_delivery_performance AS
SELECT dc.customer_state,
       dp.category,
       date_trunc('month', f.date_key) AS month,
       count(*)                                                        AS n_items,
       round(avg(f.delivery_delay_days), 2)                            AS avg_delay_days,
       round(avg(CASE WHEN f.delivery_delay_days <= 0 THEN 1.0 ELSE 0.0 END), 3) AS on_time_rate
FROM dw.fact_order_items f
JOIN dw.dim_customer dc USING (customer_id)
JOIN dw.dim_product dp USING (product_id)
WHERE f.delivery_delay_days IS NOT NULL
GROUP BY 1, 2, 3;

CREATE OR REPLACE VIEW dw.mart_review_health AS
SELECT date_trunc('month', f.date_key) AS month,
       dp.category,
       count(*)                                                  AS n_reviews,
       round(avg(f.review_score), 2)                             AS avg_score,
       sum(CASE WHEN f.review_score <= 2 THEN 1 ELSE 0 END)      AS n_bad,
       round(avg(CASE WHEN f.review_score <= 2 THEN 1.0 ELSE 0.0 END), 3) AS bad_rate
FROM dw.fact_order_items f
JOIN dw.dim_product dp USING (product_id)
WHERE f.review_score IS NOT NULL
GROUP BY 1, 2;
"""
# dw.mart_review_risk (order_id, risk_score, ...) is written by predict/review_risk.py


def build(db_path: Path | None = None) -> None:
    db_path = db_path or Settings().db_path
    if not db_path.exists():
        sys.exit(f"No database at {db_path} — run `python -m askdata.load_data` first.")
    con = duckdb.connect(str(db_path))
    con.execute(DDL)
    rows = con.execute(
        "SELECT table_name, estimated_size FROM duckdb_tables() WHERE schema_name = 'dw' "
        "UNION ALL SELECT view_name, NULL FROM duckdb_views() WHERE schema_name = 'dw' "
        "ORDER BY 1"
    ).fetchall()
    for name, size in rows:
        print(f"  dw.{name:26s} {'' if size is None else f'{size:>9,} rows'}")
    con.close()
    print("Warehouse built.")


if __name__ == "__main__":
    build(Path(sys.argv[1]) if len(sys.argv) > 1 else None)
