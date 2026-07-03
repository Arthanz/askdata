import duckdb
import pandas as pd

from askdata.executor import execute

from eval.metrics import results_match, summarize
from eval.run import load_golden


def test_golden_set_loads():
    items = load_golden()
    assert len(items) >= 40
    assert all({"id", "tier", "question"} <= set(it) for it in items)


def test_all_gold_sql_executes(db_path):
    con = duckdb.connect(str(db_path), read_only=True)
    for it in load_golden():
        if not it["gold_sql"]:
            continue
        res = execute(con, it["gold_sql"])
        assert res.ok, f"{it['id']}: {res.error}"
        assert not res.df.empty, f"{it['id']} returned no rows"
    con.close()


def test_results_match_ignores_order_and_names():
    a = pd.DataFrame({"state": ["SP", "RJ"], "n": [10, 5]})
    b = pd.DataFrame({"customer_state": ["RJ", "SP"], "n_orders": [5, 10]})
    assert results_match(a, b)


def test_results_match_scalar_containment():
    gold = pd.DataFrame({"n": [1200]})
    got = pd.DataFrame({"label": ["total orders"], "value": [1200.0]})
    assert results_match(gold, got)


def test_results_match_rejects_wrong_numbers():
    assert not results_match(pd.DataFrame({"n": [1200]}), pd.DataFrame({"n": [900]}))


def test_summarize_counts_confidently_wrong():
    rows = [
        dict(status="trusted", correct=True, acceptable=True, expect_abstain=False,
             attempts=1, seconds=1.0, input_tokens=10, output_tokens=5),
        dict(status="trusted", correct=False, acceptable=False, expect_abstain=False,
             attempts=1, seconds=1.0, input_tokens=10, output_tokens=5),
        dict(status="abstained", correct=True, acceptable=True, expect_abstain=True,
             attempts=1, seconds=1.0, input_tokens=10, output_tokens=5),
        dict(status="trusted", correct=False, acceptable=False, expect_abstain=True,
             attempts=1, seconds=1.0, input_tokens=10, output_tokens=5),
    ]
    s = summarize(rows)
    assert s["confidently_wrong"] == 2
    assert s["hallucinated_unanswerable"] == 1
    assert s["accuracy"] == 0.5
