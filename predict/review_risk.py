"""review_risk.py — Predict which orders are at risk of a bad review (<=2 stars).

Business framing: a low review score is a leading indicator of churn and a drag
on marketplace conversion. If we can flag at-risk orders *before* the review
lands (using only signals known at/around delivery), the business can intervene
— proactive support outreach, a goodwill voucher, seller coaching.

Data source, in order of preference:
1. data/askdata.duckdb (real Olist if loaded, else the synthetic sample) —
   features come from FEATURES_SQL below, one row per delivered order.
2. A pure in-memory synthetic fixture, so the script runs with zero setup.

The fitted model also scores every delivered order and writes the scores back
to the warehouse as dw.mart_review_risk, so at-risk orders surface in the same
BI layer as everything else. (In production you would score orders *before*
their review arrives; here we score the historical set to demonstrate the loop.)

Run: python -m predict.review_risk
"""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.inspection import permutation_importance
from sklearn.metrics import average_precision_score, classification_report, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

RANDOM_STATE = 42
NUMERIC = ["price", "freight_value", "n_items", "delivery_delay_days",
           "estimated_days", "product_photos", "payment_installments"]
CATEGORICAL = ["product_category", "customer_state", "payment_type"]
TARGET = "low_review"

# One row per delivered order. Only signals available at/around delivery —
# no leakage from the review itself. Portable to BigQuery with minor
# date-function renames (date_diff -> DATE_DIFF).
FEATURES_SQL = """
WITH order_agg AS (
    SELECT oi.order_id,
           round(sum(oi.price), 2)          AS price,
           round(sum(oi.freight_value), 2)  AS freight_value,
           count(*)                         AS n_items,
           max_by(coalesce(t.product_category_name_english, p.product_category_name),
                  oi.price)                 AS product_category,
           max(p.product_photos_qty)        AS product_photos
    FROM order_items oi
    JOIN products p USING (product_id)
    LEFT JOIN category_translation t USING (product_category_name)
    GROUP BY 1
), first_payment AS (
    SELECT order_id, payment_type, payment_installments
    FROM order_payments
    QUALIFY row_number() OVER (PARTITION BY order_id ORDER BY payment_sequential) = 1
), first_review AS (
    SELECT order_id, review_score
    FROM order_reviews
    QUALIFY row_number() OVER (PARTITION BY order_id ORDER BY review_creation_date DESC) = 1
)
SELECT o.order_id,
       a.price, a.freight_value, a.n_items,
       date_diff('day', o.order_estimated_delivery_date, o.order_delivered_customer_date)
           AS delivery_delay_days,
       date_diff('day', o.order_purchase_timestamp, o.order_estimated_delivery_date)
           AS estimated_days,
       a.product_photos,
       fp.payment_installments,
       a.product_category,
       c.customer_state,
       fp.payment_type,
       CASE WHEN fr.review_score <= 2 THEN 1 ELSE 0 END AS low_review
FROM orders o
JOIN order_agg a USING (order_id)
JOIN customers c USING (customer_id)
JOIN first_payment fp USING (order_id)
JOIN first_review fr USING (order_id)
WHERE o.order_status = 'delivered'
  AND o.order_delivered_customer_date IS NOT NULL
"""


def load_data() -> tuple[pd.DataFrame, str]:
    db = Path(os.environ.get("ASKDATA_DB", "data/askdata.duckdb"))
    if db.exists():
        import duckdb

        con = duckdb.connect(str(db), read_only=True)
        df = con.execute(FEATURES_SQL).fetch_df()
        con.close()
        n_orders = len(df)
        source = f"{db.name} ({'full Olist' if n_orders > 10_000 else 'synthetic sample'})"
        return df, source
    return generate_sample(), "in-memory synthetic fixture (no database found)"


def generate_sample(n: int = 6000, seed: int = RANDOM_STATE) -> pd.DataFrame:
    """Synthetic Olist-shaped orders. Bad reviews are driven mostly by late
    delivery and high freight-to-price, so the model has real signal to find."""
    rng = np.random.default_rng(seed)
    cats = ["bed_bath_table", "health_beauty", "sports_leisure", "furniture_decor",
            "computers_accessories", "housewares", "watches_gifts", "toys"]
    states = ["SP", "RJ", "MG", "RS", "PR", "BA", "SC", "GO", "PE", "CE"]
    ptypes = ["credit_card", "boleto", "voucher", "debit_card"]

    price = np.round(rng.gamma(2.0, 60.0, n) + 10, 2)
    freight = np.round(rng.gamma(2.0, 8.0, n) + 5, 2)
    n_items = rng.integers(1, 5, n)
    estimated_days = rng.integers(6, 30, n)
    delay = rng.normal(-2, 6, n).round().astype(int)
    photos = rng.integers(1, 8, n)
    installments = rng.integers(1, 11, n)
    category = rng.choice(cats, n)
    state = rng.choice(states, n, p=np.array([30, 13, 12, 8, 7, 6, 6, 6, 3, 9]) / 100)
    ptype = rng.choice(ptypes, n, p=[0.74, 0.19, 0.04, 0.03])

    freight_ratio = freight / np.maximum(price, 1)
    logit = (-2.7
             + 0.30 * np.clip(delay, 0, None)
             + 3.2 * freight_ratio
             + 0.15 * (n_items - 1)
             + np.where(np.isin(category, ["furniture_decor", "bed_bath_table"]), 0.5, 0.0)
             + rng.normal(0, 0.35, n))
    prob = 1 / (1 + np.exp(-logit))
    low_review = (rng.random(n) < prob).astype(int)

    return pd.DataFrame({
        "order_id": [f"synth{i:06d}" for i in range(n)],
        "price": price, "freight_value": freight, "n_items": n_items,
        "delivery_delay_days": delay, "estimated_days": estimated_days,
        "product_photos": photos, "payment_installments": installments,
        "product_category": category, "customer_state": state,
        "payment_type": ptype, "low_review": low_review,
    })


def build_pipeline() -> Pipeline:
    pre = ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL),
        ("num", "passthrough", NUMERIC),
    ])
    model = HistGradientBoostingClassifier(
        max_depth=4, learning_rate=0.08, max_iter=300,
        l2_regularization=1.0, random_state=RANDOM_STATE)
    return Pipeline([("pre", pre), ("model", model)])


def top_decile_lift(y_true: np.ndarray, scores: np.ndarray) -> tuple[float, float]:
    """If we flag the highest-risk 10% of orders, what share of all bad reviews
    do we catch, and how many times better than random is that?"""
    k = max(1, int(0.10 * len(scores)))
    idx = np.argsort(scores)[::-1][:k]
    caught = y_true[idx].sum()
    total_bad = y_true.sum()
    recall_at_10 = caught / total_bad if total_bad else 0.0
    base_rate = total_bad / len(y_true)
    lift = (caught / k) / base_rate if base_rate else 0.0
    return recall_at_10, lift


def write_scores_to_warehouse(df: pd.DataFrame, scores: np.ndarray) -> bool:
    """Land risk scores back into the BI layer as dw.mart_review_risk."""
    db = Path(os.environ.get("ASKDATA_DB", "data/askdata.duckdb"))
    if not db.exists():
        return False
    import duckdb

    out = pd.DataFrame({
        "order_id": df["order_id"],
        "risk_score": np.round(scores, 4),
        "had_bad_review": df[TARGET].values,
    })
    con = duckdb.connect(str(db))
    con.execute("CREATE SCHEMA IF NOT EXISTS dw")
    con.register("_scores", out)
    con.execute("CREATE OR REPLACE TABLE dw.mart_review_risk AS SELECT * FROM _scores ORDER BY risk_score DESC")
    con.close()
    return True


def main() -> None:
    df, source = load_data()
    df[CATEGORICAL] = df[CATEGORICAL].fillna("unknown")
    # DuckDB returns nullable Int64 with pd.NA; cast to float so NA -> NaN,
    # which HistGradientBoosting handles natively
    df[NUMERIC] = df[NUMERIC].astype("float64")
    X, y = df[NUMERIC + CATEGORICAL], df[TARGET].values

    Xtr, Xte, ytr, yte = train_test_split(
        X, y, test_size=0.25, stratify=y, random_state=RANDOM_STATE)

    pipe = build_pipeline().fit(Xtr, ytr)
    scores = pipe.predict_proba(Xte)[:, 1]

    auc = roc_auc_score(yte, scores)
    ap = average_precision_score(yte, scores)
    recall10, lift10 = top_decile_lift(yte, scores)

    print("=" * 66)
    print("  ORDER REVIEW-RISK MODEL")
    print(f"  data source : {source}")
    print(f"  rows        : {len(df):,}   bad-review base rate: {y.mean():.1%}")
    print("=" * 66)
    print(f"  ROC-AUC             : {auc:.3f}")
    print(f"  PR-AUC (avg prec.)  : {ap:.3f}")
    print("\n  BUSINESS READOUT")
    print(f"  Flagging the top-10% highest-risk orders catches "
          f"{recall10:.0%} of all bad reviews")
    print(f"  ({lift10:.1f}x better than random outreach).")

    print("\n  Top drivers (permutation importance):")
    imp = permutation_importance(pipe, Xte, yte, n_repeats=5,
                                 random_state=RANDOM_STATE, scoring="roc_auc")
    order = np.argsort(imp.importances_mean)[::-1]
    for i in order[:5]:
        print(f"    {X.columns[i]:<22} {imp.importances_mean[i]:+.3f}")

    print("\n  (classification report @ 0.5 threshold)")
    print(classification_report(yte, (scores >= 0.5).astype(int),
                                target_names=["ok", "bad_review"], digits=3))

    all_scores = pipe.predict_proba(X)[:, 1]
    if write_scores_to_warehouse(df, all_scores):
        print("  Risk scores written to dw.mart_review_risk.")


if __name__ == "__main__":
    main()
