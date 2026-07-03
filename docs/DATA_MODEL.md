# Data model — Olist star schema

A dimensional model (Kimball-style) is what the BI/DW half of the Deloitte AI &
Data role is about, so the warehouse is modeled explicitly rather than queried
off raw tables. Built in a `dw` schema inside DuckDB by
[`src/askdata/warehouse.py`](../src/askdata/warehouse.py); the SQL is standard
enough to port to BigQuery with only date-function renames.

## Grain
One row per **order item** in the fact table — the finest useful grain for
revenue, freight, and delivery analysis.

## Star schema

```
                  ┌────────────────┐
                  │   dim_date     │
                  └───────┬────────┘
                          │
  ┌────────────┐   ┌──────┴───────────────┐   ┌──────────────┐
  │dim_customer├──▶│   fact_order_items   │◀──┤ dim_product  │
  └────────────┘   │  · price             │   └──────────────┘
                   │  · freight_value     │
  ┌────────────┐   │  · delivery_delay    │   ┌──────────────┐
  │ dim_seller ├──▶│  · review_score      │◀──┤ dim_payment  │
  └────────────┘   └──────────────────────┘   └──────────────┘
```

| Table | Type | Rows (full Olist) | Key columns |
|---|---|---|---|
| `dw.fact_order_items` | fact | 112,650 | order_id, order_item_id, price, freight_value, delivery_delay_days, review_score |
| `dw.dim_customer` | dimension | 99,441 | customer_id, customer_unique_id, customer_state, customer_city |
| `dw.dim_product` | dimension | 32,951 | product_id, category (English), weight_g, photos_qty |
| `dw.dim_seller` | dimension | 3,095 | seller_id, seller_state, seller_city |
| `dw.dim_date` | dimension | 773 | date_key, year, quarter, month, dow |
| `dw.dim_payment` | junk dimension | 28 | payment_key, payment_type, payment_installments |

Modeling decisions worth defending in an interview:
- **Order-item grain** so revenue and freight aggregate without fan-out; order-level
  facts (status, delay, review) are repeated per item by design.
- **First payment / latest review per order** (window functions) to avoid the
  fan-out a naive join on `order_payments`/`order_reviews` causes.
- **English category names** resolved in `dim_product` once, so no downstream
  consumer joins the translation table again.
- **Separate `dw` schema** so the NL agent's schema context (raw tables) is
  unaffected — one database, two governed surfaces.

## Marts (views the dashboard + model read)
- `dw.mart_delivery_performance` — on-time %, avg delay by state/category/month.
- `dw.mart_review_health` — review-score distribution and bad-review rate by segment.
- `dw.mart_review_risk` — output of the predictive model
  ([`predict/review_risk.py`](../predict/review_risk.py)): order_id + risk_score,
  so at-risk orders surface in the same BI layer.

## Why this shape
Everything downstream reads the marts: the dashboard, the review-risk model's
feature query, and (optionally) the AskData agent. One governed model, three
consumers — which is also the governance/metadata story the JD asks for.
