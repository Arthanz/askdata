"""Introspect the DuckDB schema and render it as LLM prompt context."""

from __future__ import annotations

import duckdb

# Join hints the model can't infer reliably from column names alone.
RELATIONSHIP_HINTS = [
    "orders.customer_id = customers.customer_id",
    "order_items.order_id = orders.order_id",
    "order_items.product_id = products.product_id",
    "order_items.seller_id = sellers.seller_id",
    "order_payments.order_id = orders.order_id",
    "order_reviews.order_id = orders.order_id",
    "products.product_category_name = category_translation.product_category_name",
]

BUSINESS_NOTES = [
    "One order can have multiple items, payments, and (rarely) reviews.",
    "customers.customer_id is per-order; customers.customer_unique_id identifies a person.",
    "product_category_name is in Portuguese; join category_translation for English names.",
    "Revenue questions usually mean SUM(order_payments.payment_value) or SUM(order_items.price).",
    "Delivery-time questions use order_purchase_timestamp vs order_delivered_customer_date.",
]


def get_tables(con: duckdb.DuckDBPyConnection) -> dict[str, list[tuple[str, str]]]:
    """{table_name: [(column, type), ...]}"""
    tables: dict[str, list[tuple[str, str]]] = {}
    rows = con.execute(
        "SELECT table_name, column_name, data_type FROM information_schema.columns "
        "WHERE table_schema = 'main' ORDER BY table_name, ordinal_position"
    ).fetchall()
    for table, column, dtype in rows:
        tables.setdefault(table, []).append((column, dtype))
    return tables


def identifiers(con: duckdb.DuckDBPyConnection) -> set[str]:
    """All known table and column names, lowercased, for static SQL checks."""
    ids: set[str] = set()
    for table, cols in get_tables(con).items():
        ids.add(table.lower())
        ids.update(c.lower() for c, _ in cols)
    return ids


def schema_prompt(con: duckdb.DuckDBPyConnection) -> str:
    lines = ["### Database schema (DuckDB)"]
    for table, cols in get_tables(con).items():
        n = con.execute(f'SELECT count(*) FROM "{table}"').fetchone()[0]
        lines.append(f"\nTable {table} ({n} rows):")
        lines.extend(f"  - {col} ({dtype})" for col, dtype in cols)
    lines.append("\n### Join keys")
    lines.extend(f"  - {h}" for h in RELATIONSHIP_HINTS)
    lines.append("\n### Notes")
    lines.extend(f"  - {n}" for n in BUSINESS_NOTES)
    return "\n".join(lines)
