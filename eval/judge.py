"""LLM-as-a-judge answer equivalence — a second opinion when the structural
comparison in metrics.py says 'no match'.

Structural comparison is strict: it can reject answers that are semantically
right but shaped differently (extra context column, different granularity).
When enabled (--use-judge), this asks a model whether the produced answer is
equivalent to the gold answer, and the eval records both scores.
"""

from __future__ import annotations

import json
import re

import pandas as pd

from askdata.llm import LLMClient

EQUIV_SYSTEM = """You compare two answers to a business data question. Given the
question, the GOLD result (correct by construction), and the AGENT's result,
decide whether the agent's answer conveys the same substantive answer — same
key numbers/entities, allowing different formatting, extra harmless columns,
or rounding differences up to 1%.

Reply with JSON only: {"equivalent": true | false, "reason": "<one sentence>"}"""


def answers_equivalent(
    llm: LLMClient, question: str, gold: pd.DataFrame, got: pd.DataFrame
) -> tuple[bool, str]:
    user = (
        f"### Question\n{question}\n\n### GOLD result\n{gold.head(25).to_string(index=False)}"
        f"\n\n### AGENT result\n{got.head(25).to_string(index=False)}"
    )
    resp = llm.complete(EQUIV_SYSTEM, user, max_tokens=200)
    m = re.search(r"\{.*\}", resp.text, re.DOTALL)
    if m:
        try:
            obj = json.loads(m.group(0))
            return bool(obj.get("equivalent")), str(obj.get("reason", ""))
        except json.JSONDecodeError:
            pass
    return False, resp.text.strip()[:200]
