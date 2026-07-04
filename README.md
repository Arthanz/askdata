# AskData

Analytics on the Olist e-commerce dataset, end to end: a dimensional warehouse,
a model that predicts which orders will get bad reviews, and a natural-language
agent that answers questions with SQL — and verifies its own answers instead of
confidently making numbers up.

The verification part is the point. Text-to-SQL agents are easy to demo and
hard to trust: ask a question, and the model happily writes SQL, runs it, and
hands you a number, even when the query silently answered a slightly different
question. A wrong number that looks right is worse than an error message.
AskData checks every answer (schema validity, an LLM judge, result sanity),
repairs what it can, and refuses what it can't — tagging each answer
**trusted**, **repaired**, or **abstained**. How much that helps is measured,
not claimed; the measurement is also a paper draft (see `paper/`).

> **Live demo:** [askdata-arthanz.streamlit.app](https://askdata-arthanz.streamlit.app/) · **Paper:** [`paper/DRAFT.md`](paper/DRAFT.md)

## Architecture

```
 raw Olist ─▶ dimensional warehouse ─▶ ┬─▶ marts (delivery, review health)
 (DuckDB)     (star schema, dw.*)      │
                                       ├─▶ review-risk model ─▶ dw.mart_review_risk
                                       │
                                       └─▶ AskData agent (NL → SQL, verified)
```

## Results

**Verification eval** — 150 golden questions across six tiers (lookup,
aggregation, multi-join, temporal, ambiguous, unanswerable), gold answers
computed by executing hand-written gold SQL on the same database:

| confidently-wrong rate (pilot, 42q) | baseline | verified | change |
|---|---|---|---|
| Qwen2.5-Coder-3B (local, Ollama) | 28.6% | 9.5% | −67% |
| GPT-4o-mini (OpenAI) | 26.2% | 19.0% | −27% |

_(pilot numbers; the full campaign — 150 questions × 4 providers × 3 runs —
is in progress and will replace this table)_

**Review-risk model** — trained on 95,823 delivered orders:

```
ROC-AUC 0.756 · PR-AUC 0.469 · bad-review base rate 12.8%
Flagging the riskiest 10% of orders catches 41% of all bad reviews (4.1x random)
Top driver: delivery delay
```

## Stack

- **DuckDB** — raw tables plus a Kimball star schema (`dw`) in one file; the SQL
  ports to BigQuery with minor date-function changes ([`docs/DATA_MODEL.md`](docs/DATA_MODEL.md))
- **scikit-learn** for the risk model ([`predict/review_risk.py`](predict/review_risk.py))
- **LLM-agnostic agent** — Anthropic, OpenAI, Gemini, or local models via Ollama;
  the agent loop is written from scratch so the mechanics are easy to read
- **Streamlit** for the demo

The dataset is [Olist Brazilian E-Commerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
(public, ~100k orders). A built-in synthetic sample with the same schema means
everything runs with zero downloads.

## Quickstart

```bash
pip install -r requirements.txt && pip install -e .
python -m askdata.load_data        # data/askdata.duckdb (sample, or full Olist if CSVs in data/olist/)
python -m askdata.warehouse        # star schema + marts (dw.*)
python -m predict.review_risk      # trains the risk model, writes dw.mart_review_risk
pytest                             # 28 tests, no API key needed

cp .env.example .env               # add a provider key (or install Ollama for free local models)
streamlit run app/app.py           # the demo
python -m eval.run                 # baseline vs verified on the golden set
```

## Repo layout

```
askdata/
├── src/askdata/   # agent (llm, schema, sqlgen, verify) + warehouse builder
├── predict/       # review-risk model
├── docs/          # data model
├── eval/          # golden questions, judge, metrics, runner, reports
├── app/           # Streamlit demo
├── data/          # loader (+ optional data/olist/ CSVs)
├── tests/         # deterministic tests (scripted LLM, synthetic sample)
├── paper/         # failure-mode study + verification layer (draft)
└── notebooks/     # error analysis
```

[`ROADMAP.md`](ROADMAP.md) tracks what's done and what's left.
