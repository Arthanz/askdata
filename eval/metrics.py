"""Result comparison and metric aggregation for the eval."""

from __future__ import annotations

import re
from datetime import date, datetime

import numpy as np
import pandas as pd

DATE_YM = re.compile(r"^\d{4}-\d{2}$")


def _norm_cell(v):
    """Normalize a cell so semantically-equal results compare equal."""
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return None
    if isinstance(v, (pd.Timestamp, datetime, date, np.datetime64)):
        return str(pd.Timestamp(v).date())
    if isinstance(v, (bool, np.bool_)):
        return bool(v)
    if isinstance(v, (int, float, np.integer, np.floating)):
        return round(float(v), 2)
    s = str(v).strip()
    if DATE_YM.match(s):  # '2017-01' == '2017-01-01'
        return s + "-01"
    try:
        return round(float(s), 2)
    except ValueError:
        return s.lower()


def _norm_rows(df: pd.DataFrame) -> list[tuple]:
    """Order-insensitive, column-name-insensitive canonical form.

    Each row becomes a sorted tuple of its normalized cells (bag of values),
    then rows are sorted — the standard execution-match relaxation used by
    text-to-SQL benchmarks.
    """
    rows = []
    for row in df.itertuples(index=False):
        cells = [_norm_cell(v) for v in row]
        rows.append(tuple(sorted(cells, key=lambda x: (x is None, str(type(x)), str(x)))))
    return sorted(rows, key=str)


def results_match(gold: pd.DataFrame | None, got: pd.DataFrame | None) -> bool:
    if gold is None or got is None:
        return False
    if _norm_rows(gold) == _norm_rows(got):
        return True
    # Scalar answers: accept if the gold value appears in a small result
    # (e.g. gold is the count, the agent also returned a label column).
    if gold.shape == (1, 1) and len(got) == 1 and got.shape[1] <= 3:
        gold_val = _norm_cell(gold.iat[0, 0])
        return any(_norm_cell(v) == gold_val for v in got.iloc[0])
    return False


def summarize(rows: list[dict]) -> dict:
    """Aggregate per-question eval rows into the paper's headline metrics."""
    n = len(rows)
    answerable = [r for r in rows if not r["expect_abstain"]]
    unanswerable = [r for r in rows if r["expect_abstain"]]
    answered = [r for r in rows if r["status"] in ("trusted", "repaired")]
    wrong_answered = [r for r in answered if not r["correct"] and not r["acceptable"]]

    def rate(x, base):
        return round(len(x) / len(base), 3) if base else 0.0

    return {
        "n": n,
        "answered": len(answered),
        "abstained": sum(r["status"] == "abstained" for r in rows),
        "errors": sum(r["status"] == "error" for r in rows),
        "correct": sum(r["correct"] for r in rows),
        "accuracy": rate([r for r in rows if r["correct"]], rows),
        "accuracy_answerable": rate([r for r in answerable if r["correct"]], answerable),
        # the headline: wrong answers presented confidently, as a share of all questions
        "confidently_wrong": len(wrong_answered),
        "confidently_wrong_rate": rate(wrong_answered, rows),
        "hallucinated_unanswerable": sum(
            r["status"] in ("trusted", "repaired") for r in unanswerable
        ),
        "repaired": sum(r["status"] == "repaired" for r in rows),
        "repair_success": sum(r["status"] == "repaired" and r["correct"] for r in rows),
        "avg_attempts": round(np.mean([r["attempts"] for r in rows]), 2) if rows else 0,
        "avg_seconds": round(np.mean([r["seconds"] for r in rows]), 2) if rows else 0,
        "total_tokens": int(sum(r["input_tokens"] + r["output_tokens"] for r in rows)),
    }
