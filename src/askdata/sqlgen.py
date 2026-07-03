"""Question -> SQL generation prompts and parsing."""

from __future__ import annotations

import re

from .llm import LLMClient, LLMResponse

SQL_SYSTEM = """You are an expert analytics engineer writing DuckDB SQL for an
e-commerce database. Rules:
- Output exactly ONE SELECT statement inside a ```sql fenced block.
- Use only tables and columns that appear in the provided schema. Never invent columns.
- If the question cannot be answered from this schema (the data simply is not there),
  do NOT guess a proxy. Output the single word ABSTAIN (no fence) and one sentence
  explaining what data is missing.
- If the question is ambiguous, pick the most common business interpretation and
  add a SQL comment line starting with `-- assumption:` stating it.
- Give aggregate columns clear aliases. Prefer English category names via
  category_translation when showing categories to the user.
- Round money to 2 decimals. Add ORDER BY + LIMIT for top-N questions."""


def build_sql_prompt(question: str, schema_text: str, feedback: str | None = None) -> str:
    parts = [schema_text, f"\n### Question\n{question}"]
    if feedback:
        parts.append(
            "\n### Previous attempt failed\n"
            f"{feedback}\n"
            "Write a corrected query (or ABSTAIN if the question is unanswerable)."
        )
    return "\n".join(parts)


def extract_sql(text: str) -> str | None:
    """Pull SQL out of the model response; None means the model abstained."""
    if re.search(r"^\s*ABSTAIN\b", text.strip(), re.IGNORECASE):
        return None
    m = re.search(r"```(?:sql)?\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    sql = (m.group(1) if m else text).strip().rstrip(";").strip()
    return sql or None


def generate_sql(
    llm: LLMClient, question: str, schema_text: str, feedback: str | None = None
) -> tuple[str | None, str, LLMResponse]:
    """Returns (sql_or_none, raw_text, response). sql None => model abstained."""
    resp = llm.complete(SQL_SYSTEM, build_sql_prompt(question, schema_text, feedback))
    return extract_sql(resp.text), resp.text, resp
