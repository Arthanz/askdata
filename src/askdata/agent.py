"""The AskData agent: plan -> SQL -> execute -> verify -> (repair) -> answer.

Every answer carries a status:
  trusted   — passed all verification on the first attempt
  repaired  — failed at least once, a later attempt passed
  abstained — could not produce an answer it trusts (this is a feature)
  error     — infrastructure failure (no DB, provider down, ...)

`verify=False` gives the naive baseline used in the eval: first executable
query wins and is always reported as trusted.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import duckdb
import pandas as pd

from .config import Settings
from .executor import execute
from .llm import LLMClient, get_client
from .schema import identifiers, schema_prompt
from .sqlgen import generate_sql
from .verify import Check, judge_sql, sanity_checks, static_checks

SUMMARY_SYSTEM = """You summarize SQL results for a business user. Given a question,
the SQL used, and the result table, answer the question in 1-2 plain sentences with
the key numbers. Do not mention SQL. If an `-- assumption:` comment is present in
the SQL, state the assumption briefly."""


@dataclass
class Answer:
    question: str
    status: str  # trusted | repaired | abstained | error
    sql: str | None = None
    df: pd.DataFrame | None = None
    text: str = ""
    checks: list[Check] = field(default_factory=list)
    attempts: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    seconds: float = 0.0


class AskDataAgent:
    def __init__(
        self,
        db_path: str | None = None,
        llm: LLMClient | None = None,
        settings: Settings | None = None,
        verify: bool = True,
    ):
        self.settings = settings or Settings()
        self.verify = verify
        self.llm = llm or get_client(self.settings)
        path = str(db_path or self.settings.db_path)
        self.con = duckdb.connect(path, read_only=True)
        self.schema_text = schema_prompt(self.con)
        self.ids = identifiers(self.con)

    def ask(self, question: str) -> Answer:
        start = time.perf_counter()
        ans = Answer(question=question, status="abstained")
        feedback: str | None = None

        for attempt in range(1, self.settings.max_attempts + 1):
            ans.attempts = attempt
            try:
                sql, raw, resp = generate_sql(self.llm, question, self.schema_text, feedback)
            except Exception as e:
                ans.status, ans.text = "error", f"LLM call failed: {e}"
                break
            ans.input_tokens += resp.input_tokens
            ans.output_tokens += resp.output_tokens

            if sql is None:  # model itself declined
                ans.status = "abstained"
                ans.text = raw.replace("ABSTAIN", "").strip() or (
                    "I can't answer this from the available data."
                )
                break
            ans.sql = sql

            checks: list[Check] = []
            if self.verify:
                checks += static_checks(sql, self.ids)
                if bad := [c for c in checks if not c.passed]:
                    feedback = "; ".join(f"{c.name}: {c.detail}" for c in bad)
                    ans.checks = checks
                    continue

            result = execute(self.con, sql, self.settings.row_limit)
            if not result.ok:
                feedback = f"Execution error: {result.error}"
                ans.checks = checks
                continue
            ans.df = result.df

            if self.verify:
                checks += sanity_checks(result.df)
                if bad := [c for c in checks if not c.passed]:
                    feedback = "; ".join(f"{c.name}: {c.detail}" for c in bad)
                    ans.checks = checks
                    continue
                try:
                    judge_check, jresp = judge_sql(
                        self.llm, question, sql, self.schema_text, result.df
                    )
                    ans.input_tokens += jresp.input_tokens
                    ans.output_tokens += jresp.output_tokens
                except Exception as e:
                    judge_check = Check("judge.sql_answers_question", False, f"judge call failed: {e}")
                checks.append(judge_check)
                if not judge_check.passed:
                    feedback = f"Reviewer rejected the SQL: {judge_check.detail}"
                    ans.checks = checks
                    continue

            ans.checks = checks
            ans.status = "trusted" if attempt == 1 else "repaired"
            ans.text = self._summarize(question, sql, result.df)
            break
        else:
            ans.text = (
                "I couldn't produce an answer I trust for this question. "
                f"Last problem: {feedback}"
            )

        ans.seconds = time.perf_counter() - start
        return ans

    def _summarize(self, question: str, sql: str, df: pd.DataFrame) -> str:
        preview = df.head(20).to_string(index=False)
        try:
            resp = self.llm.complete(
                SUMMARY_SYSTEM,
                f"Question: {question}\n\nSQL:\n{sql}\n\nResult ({len(df)} rows):\n{preview}",
                max_tokens=1000,
            )
            return resp.text.strip()
        except Exception:
            return f"Result ({len(df)} rows):\n{preview}"

    def close(self):
        self.con.close()
