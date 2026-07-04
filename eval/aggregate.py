"""Aggregate tagged eval reports into per-provider tables (mean ± sd across runs)
plus a paired McNemar test on the confidently-wrong outcomes.

    python -m eval.aggregate

Reads every eval/reports/report_<tag>_*.json that carries a meta block; pilots
(untagged reports) are ignored. Writes eval/reports/AGGREGATE.md.
"""

from __future__ import annotations

import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

REPORTS = Path(__file__).resolve().parent / "reports"

BASELINE = "baseline (no verification)"
VERIFIED = "askdata (verification on)"
METRICS = [
    ("accuracy", "accuracy"),
    ("accuracy_answerable", "accuracy (answerable)"),
    ("confidently_wrong_rate", "confidently-wrong rate"),
    ("abstained", "abstained (n)"),
    ("hallucinated_unanswerable", "hallucinated unanswerable (n)"),
    ("repaired", "repaired (n)"),
    ("avg_seconds", "avg seconds / question"),
    ("total_tokens", "total tokens"),
]


def is_cw(row: dict) -> bool:
    return row["status"] in ("trusted", "repaired") and not row["correct"] and not row["acceptable"]


def mcnemar_p(b: int, c: int) -> float:
    """Exact two-sided McNemar test on discordant pair counts."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / 2**n
    return min(1.0, 2 * tail)


def fmt(values: list[float]) -> str:
    if len(values) == 1:
        return f"{values[0]:.3f}"
    return f"{statistics.mean(values):.3f} ± {statistics.stdev(values):.3f}"


def main():
    by_provider: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for path in sorted(REPORTS.glob("report_*.json")):
        data = json.loads(path.read_text())
        if "meta" not in data or not data["meta"].get("tag"):
            continue
        m = data["meta"]
        by_provider[(m["provider"], m["model"])].append(data)

    lines = ["# Aggregated eval results", ""]
    for (provider, model), runs in sorted(by_provider.items()):
        lines.append(f"## {provider} — `{model}` ({len(runs)} run{'s' if len(runs) > 1 else ''})")
        lines.append("")
        lines.append("| metric | baseline | verified |")
        lines.append("|---|---|---|")
        for key, label in METRICS:
            base = [r["configs"][BASELINE]["summary"][key] for r in runs]
            ver = [r["configs"][VERIFIED]["summary"][key] for r in runs]
            lines.append(f"| {label} | {fmt(base)} | {fmt(ver)} |")

        # paired McNemar on confidently-wrong outcomes, per (question, run) pair
        b = c = 0
        for r in runs:
            base_rows = {x["id"]: x for x in r["configs"][BASELINE]["rows"]}
            ver_rows = {x["id"]: x for x in r["configs"][VERIFIED]["rows"]}
            for qid in base_rows:
                bw, vw = is_cw(base_rows[qid]), is_cw(ver_rows[qid])
                b += bw and not vw
                c += vw and not bw
        p = mcnemar_p(b, c)
        lines.append("")
        lines.append(
            f"Paired confidently-wrong outcomes across {len(runs)} run(s): "
            f"baseline-only CW on {b} question-runs, verified-only CW on {c}; "
            f"exact McNemar p = {p:.2g}."
        )
        lines.append("")

    out = "\n".join(lines)
    (REPORTS / "AGGREGATE.md").write_text(out)
    print(out)


if __name__ == "__main__":
    main()
