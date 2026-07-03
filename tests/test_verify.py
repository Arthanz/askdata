import pandas as pd

from askdata.llm import ScriptedClient
from askdata.schema import identifiers
from askdata.sqlgen import extract_sql
from askdata.verify import judge_sql, sanity_checks, static_checks


def _failed(checks):
    return [c.name for c in checks if not c.passed]


def test_static_ok(con):
    ids = identifiers(con)
    sql = "SELECT order_status, count(*) AS n FROM orders GROUP BY order_status"
    assert _failed(static_checks(sql, ids)) == []


def test_static_flags_unknown_identifier(con):
    ids = identifiers(con)
    checks = static_checks("SELECT profit_margin FROM orders", ids)
    assert "static.identifiers" in _failed(checks)


def test_static_flags_non_select(con):
    checks = static_checks("DELETE FROM orders", identifiers(con))
    assert "static.select_only" in _failed(checks)


def test_sanity_empty_and_null():
    assert "sanity.nonempty" in _failed(sanity_checks(pd.DataFrame({"a": []})))
    assert "sanity.not_all_null" in _failed(sanity_checks(pd.DataFrame({"a": [None]})))
    assert _failed(sanity_checks(pd.DataFrame({"n": [3]}))) == []


def test_sanity_negative_count():
    checks = sanity_checks(pd.DataFrame({"total_orders": [-5]}))
    assert "sanity.no_negative_counts" in _failed(checks)


def test_judge_parses_json_verdict(con):
    df = pd.DataFrame({"n": [10]})
    llm = ScriptedClient(['{"verdict": "fail", "reason": "wrong table"}'])
    check, _ = judge_sql(llm, "how many orders?", "SELECT 10 AS n", "schema", df)
    assert not check.passed and "wrong table" in check.detail


def test_extract_sql_variants():
    assert extract_sql("```sql\nSELECT 1;\n```") == "SELECT 1"
    assert extract_sql("SELECT 2") == "SELECT 2"
    assert extract_sql("ABSTAIN — no cost data available") is None
