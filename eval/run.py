"""Run the evaluation: baseline (no verification) vs AskData (verification on).

    python -m eval.run                 # both configs, full golden set
    python -m eval.run --mode verified --limit 10
    python -m eval.run --use-judge     # add LLM answer-equivalence scoring

Writes a markdown + JSON report to eval/reports/ and prints the summary table.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import duckdb

from askdata.agent import AskDataAgent
from askdata.config import Settings
from askdata.executor import execute
from askdata.llm import get_client

from .metrics import results_match, summarize

EVAL_DIR = Path(__file__).resolve().parent
GOLDEN = EVAL_DIR / "golden.jsonl"
REPORTS = EVAL_DIR / "reports"


def load_golden(limit: int | None = None) -> list[dict]:
    items = [json.loads(line) for line in GOLDEN.read_text().splitlines() if line.strip()]
    for it in items:
        it.setdefault("abstain_ok", False)
        it.setdefault("expect_abstain", False)
    return items[:limit] if limit else items


def run_config(name: str, verify: bool, items: list[dict], settings: Settings,
               use_judge: bool = False) -> tuple[list[dict], dict]:
    agent = AskDataAgent(settings=settings, verify=verify)
    gold_con = duckdb.connect(str(settings.db_path), read_only=True)
    judge_llm = get_client(settings) if use_judge else None
    rows = []
    print(f"\n=== {name} ({len(items)} questions) ===")
    for it in items:
        ans = agent.ask(it["question"])
        gold_df = None
        if it["gold_sql"]:
            gold_res = execute(gold_con, it["gold_sql"])
            if not gold_res.ok:
                raise RuntimeError(f"Gold SQL failed for {it['id']}: {gold_res.error}")
            gold_df = gold_res.df

        answered = ans.status in ("trusted", "repaired")
        if it["expect_abstain"]:
            correct = ans.status == "abstained"
            acceptable = correct
        elif not answered:
            correct = False
            acceptable = bool(it["abstain_ok"]) and ans.status == "abstained"
        else:
            correct = results_match(gold_df, ans.df)
            acceptable = correct
            if not correct and use_judge and judge_llm and gold_df is not None and ans.df is not None:
                equiv, _ = answers_equivalent_safe(judge_llm, it["question"], gold_df, ans.df)
                correct = acceptable = equiv

        rows.append({
            "id": it["id"], "tier": it["tier"], "question": it["question"],
            "expect_abstain": it["expect_abstain"], "abstain_ok": it["abstain_ok"],
            "status": ans.status, "correct": correct, "acceptable": acceptable,
            "attempts": ans.attempts, "sql": ans.sql, "answer": ans.text,
            "failed_checks": [c.name for c in ans.checks if not c.passed],
            "input_tokens": ans.input_tokens, "output_tokens": ans.output_tokens,
            "seconds": round(ans.seconds, 2),
        })
        flag = "OK " if correct else ("ABST" if ans.status == "abstained" else "WRONG")
        print(f"  [{flag:5s}] {it['id']:3s} {it['tier']:12s} status={ans.status:9s} "
              f"attempts={ans.attempts} {it['question'][:60]}")
    agent.close()
    gold_con.close()
    return rows, summarize(rows)


def answers_equivalent_safe(llm, question, gold, got):
    from .judge import answers_equivalent
    try:
        return answers_equivalent(llm, question, gold, got)
    except Exception as e:
        return False, f"judge error: {e}"


def render_report(results: dict[str, tuple[list, dict]]) -> str:
    lines = [f"# AskData evaluation report — {datetime.now():%Y-%m-%d %H:%M}", ""]
    keys = ["n", "answered", "abstained", "correct", "accuracy", "accuracy_answerable",
            "confidently_wrong", "confidently_wrong_rate", "hallucinated_unanswerable",
            "repaired", "repair_success", "avg_attempts", "avg_seconds", "total_tokens"]
    lines.append("| metric | " + " | ".join(results) + " |")
    lines.append("|---|" + "---|" * len(results))
    for k in keys:
        lines.append(f"| {k} | " + " | ".join(str(s[k]) for _, s in results.values()) + " |")
    lines.append("\n## Per-question detail\n")
    for name, (rows, _) in results.items():
        lines.append(f"### {name}\n")
        lines.append("| id | tier | status | correct | attempts | failed checks |")
        lines.append("|---|---|---|---|---|---|")
        for r in rows:
            lines.append(
                f"| {r['id']} | {r['tier']} | {r['status']} | {r['correct']} "
                f"| {r['attempts']} | {', '.join(r['failed_checks']) or '-'} |"
            )
        lines.append("")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mode", choices=["both", "verified", "baseline"], default="both")
    ap.add_argument("--limit", type=int, default=None, help="run only the first N questions")
    ap.add_argument("--use-judge", action="store_true", help="LLM answer-equivalence fallback")
    ap.add_argument("--db", default=None, help="path to the DuckDB file")
    args = ap.parse_args(argv)

    settings = Settings()
    if args.db:
        settings.db_path = Path(args.db)
    if not settings.db_path.exists():
        sys.exit(f"No database at {settings.db_path} — run `python -m askdata.load_data` first.")
    try:
        settings.resolved_provider()
    except RuntimeError as e:
        sys.exit(str(e))

    items = load_golden(args.limit)
    results: dict[str, tuple[list, dict]] = {}
    if args.mode in ("both", "baseline"):
        results["baseline (no verification)"] = run_config(
            "baseline (no verification)", False, items, settings, args.use_judge)
    if args.mode in ("both", "verified"):
        results["askdata (verification on)"] = run_config(
            "askdata (verification on)", True, items, settings, args.use_judge)

    report = render_report(results)
    REPORTS.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    (REPORTS / f"report_{stamp}.md").write_text(report)
    (REPORTS / f"report_{stamp}.json").write_text(json.dumps(
        {name: {"rows": rows, "summary": s} for name, (rows, s) in results.items()},
        indent=2, default=str))
    print("\n" + "=" * 70)
    for name, (_, s) in results.items():
        print(f"\n{name}:")
        for k, v in s.items():
            print(f"  {k:28s} {v}")
    print(f"\nReport written to eval/reports/report_{stamp}.md")


if __name__ == "__main__":
    main()
