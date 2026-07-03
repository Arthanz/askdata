"""The verification layer — the reason this project exists.

Three families of checks run after SQL generation/execution:

1. static   — SELECT-only, and every referenced identifier exists in the schema
2. sanity   — the result is not empty / all-NULL / degenerate
3. judge    — an LLM check: "does this SQL actually answer this question?"

Each check returns a Check(name, passed, detail); the agent turns failures into
repair feedback or, if repairs run out, an abstention.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

import pandas as pd

from .executor import FORBIDDEN
from .llm import LLMClient

SQL_KEYWORDS = {
    "select", "from", "where", "group", "by", "order", "having", "limit", "offset",
    "join", "inner", "left", "right", "full", "outer", "cross", "on", "using", "as",
    "and", "or", "not", "in", "is", "null", "between", "like", "ilike", "case",
    "when", "then", "else", "end", "distinct", "union", "all", "with", "asc", "desc",
    "count", "sum", "avg", "min", "max", "round", "cast", "coalesce", "extract",
    "date_trunc", "date_diff", "datediff", "strftime", "year", "month", "day",
    "interval", "current_date", "now", "abs", "concat", "lower", "upper", "substr",
    "row_number", "rank", "dense_rank", "over", "partition", "filter", "nullif",
    "true", "false", "exists", "any", "some", "median", "stddev", "var_pop",
    "date", "timestamp", "integer", "bigint", "double", "varchar", "decimal",
    "to", "epoch", "quarter", "week", "dayname", "monthname", "last_day", "greatest", "least",
}


@dataclass
class Check:
    name: str
    passed: bool
    detail: str = ""


def static_checks(sql: str, known_identifiers: set[str]) -> list[Check]:
    checks = []
    is_select = bool(re.match(r"^\s*(with|select)\b", sql, re.IGNORECASE)) and not FORBIDDEN.search(sql)
    checks.append(Check("static.select_only", is_select, "" if is_select else "Not a plain SELECT query."))

    # Strip strings/comments, then flag identifiers that are neither SQL keywords,
    # known schema names, nor aliases defined inside the query itself.
    stripped = re.sub(r"'[^']*'", "", sql)
    stripped = re.sub(r"--[^\n]*", "", stripped)
    tokens = set(re.findall(r"[a-zA-Z_][a-zA-Z0-9_]*", stripped))
    # aliases introduced by the query itself: `AS name`, `FROM/JOIN table alias`,
    # and CTE names (`name AS (...)`)
    aliases = {a.lower() for a in re.findall(r"\bas\s+([a-zA-Z_][a-zA-Z0-9_]*)", stripped, re.IGNORECASE)}
    aliases |= {a.lower() for a in re.findall(r"\b(?:from|join)\s+\w+\s+(?:as\s+)?([a-zA-Z_][a-zA-Z0-9_]*)", stripped, re.IGNORECASE)}
    aliases |= {a.lower() for a in re.findall(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\s+as\s*\(", stripped, re.IGNORECASE)}
    unknown = sorted(
        t for t in (tok.lower() for tok in tokens)
        if t not in SQL_KEYWORDS and t not in known_identifiers and t not in aliases
    )
    passed = not unknown
    checks.append(
        Check(
            "static.identifiers",
            passed,
            "" if passed else f"Unknown identifiers (not in schema): {', '.join(unknown[:8])}",
        )
    )
    return checks


def sanity_checks(df: pd.DataFrame) -> list[Check]:
    checks = []
    nonempty = len(df) > 0
    checks.append(Check("sanity.nonempty", nonempty, "" if nonempty else "Query returned zero rows."))
    if nonempty:
        all_null = bool(df.isna().all().all())
        checks.append(
            Check("sanity.not_all_null", not all_null, "All returned values are NULL." if all_null else "")
        )
        neg = [
            c for c in df.select_dtypes("number").columns
            if re.search(r"count|total|revenue|sum|num|qty|orders", c, re.IGNORECASE)
            and (df[c].dropna() < 0).any()
        ]
        checks.append(
            Check(
                "sanity.no_negative_counts",
                not neg,
                f"Negative values in count/total columns: {neg}" if neg else "",
            )
        )
    return checks


JUDGE_SYSTEM = """You are a strict SQL reviewer. Given a database schema, a user
question, a SQL query, and a preview of its result, decide whether executing this
SQL genuinely answers the user's question.

Fail it if the SQL answers a *different* question (wrong metric, wrong filter,
missing join, wrong grain, ignores a time constraint), or if the result preview
is clearly inconsistent with the question. Minor style issues are fine.

Reply with JSON only: {"verdict": "pass" | "fail", "reason": "<one sentence>"}"""


def judge_sql(
    llm: LLMClient, question: str, sql: str, schema_text: str, df: pd.DataFrame
) -> tuple[Check, object]:
    preview = df.head(10).to_string(index=False)
    user = (
        f"{schema_text}\n\n### Question\n{question}\n\n### SQL\n{sql}\n\n"
        f"### Result preview ({len(df)} rows)\n{preview}"
    )
    resp = llm.complete(JUDGE_SYSTEM, user, max_tokens=300)
    verdict, reason = _parse_judge(resp.text)
    return Check("judge.sql_answers_question", verdict == "pass", reason), resp


def _parse_judge(text: str) -> tuple[str, str]:
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if m:
        try:
            obj = json.loads(m.group(0))
            return str(obj.get("verdict", "fail")).lower(), str(obj.get("reason", ""))
        except json.JSONDecodeError:
            pass
    # fallback: look for the word
    return ("pass" if re.search(r"\bpass\b", text, re.IGNORECASE) else "fail"), text.strip()[:200]
