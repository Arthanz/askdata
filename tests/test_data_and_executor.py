from askdata.executor import execute
from askdata.schema import get_tables, identifiers, schema_prompt

EXPECTED_TABLES = {
    "customers", "orders", "order_items", "order_payments",
    "order_reviews", "products", "sellers", "category_translation",
}


def test_loader_creates_all_tables(con):
    assert set(get_tables(con)) == EXPECTED_TABLES
    for table in EXPECTED_TABLES:
        assert con.execute(f"SELECT count(*) FROM {table}").fetchone()[0] > 0


def test_schema_prompt_mentions_tables_and_joins(con):
    text = schema_prompt(con)
    assert "orders" in text and "customer_unique_id" in text
    assert "order_items.order_id = orders.order_id" in text


def test_identifiers_include_tables_and_columns(con):
    ids = identifiers(con)
    assert "orders" in ids and "payment_value" in ids


def test_execute_select_ok(con):
    res = execute(con, "SELECT count(*) AS n FROM orders;")
    assert res.ok and res.df.iloc[0, 0] > 0


def test_execute_rejects_writes(con):
    for sql in ["DROP TABLE orders", "INSERT INTO orders VALUES (1)",
                "SELECT 1; SELECT 2", "CREATE TABLE x AS SELECT 1"]:
        assert not execute(con, sql).ok


def test_execute_row_limit(con):
    res = execute(con, "SELECT * FROM orders", row_limit=10)
    assert res.ok and len(res.df) == 10 and res.truncated


def test_execute_reports_errors(con):
    res = execute(con, "SELECT nonexistent_col FROM orders")
    assert not res.ok and "nonexistent_col" in res.error
