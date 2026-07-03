# AskData — from raw orders to a decision, with an AI layer that knows when it's wrong

An end-to-end analytics solution on a public e-commerce dataset: a governed data
warehouse, a model that **predicts a business outcome**, and a natural-language
agent on top that **verifies its own answers** instead of confidently making
numbers up.

Built to mirror the work of a Deloitte **AI & Data / Strategy & Analytics**
analyst: data → insight → prediction → recommendation, communicated to a client.

> **Live demo:** _(link once deployed)_ · **Paper:** [`paper/DRAFT.md`](paper/DRAFT.md) · **Recommendation deck:** _(coming — see ROADMAP)_

---

## The decision arc

```
 raw Olist ─▶ dimensional warehouse ─▶ ┬─▶ marts / dashboard (what happened)
 (DuckDB,     (star schema, dw.*)      │
  BigQuery-                            ├─▶ review-risk model (what will happen)
  portable)                            │
                                       └─▶ AskData agent (ask anything, in English)
                                                 │  verifies · repairs · abstains
                                                 ▼
                                        one-page recommendation + deck
```

## How it maps to the role

| Job posting line | What proves it here |
|---|---|
| "design and implement data structures … BI/DW reporting" | star-schema warehouse — [`docs/DATA_MODEL.md`](docs/DATA_MODEL.md), [`src/askdata/warehouse.py`](src/askdata/warehouse.py) |
| "apply analytical models to predict business outcomes … Python" | review-risk model — [`predict/review_risk.py`](predict/review_risk.py) |
| "uncover insights, inform decision-making" | marts + business readout (below) |
| "latest technologies … AI/ML … cognitive technologies" | AskData NL agent — [`src/askdata/agent.py`](src/askdata/agent.py) |
| "attention to detail" / reliability | verification layer + 150-question eval harness — [`eval/`](eval) |
| "Good understanding in AI and ML" | LLM-as-judge, abstention, failure-mode taxonomy — [`paper/`](paper) |
| "recommend … to clients", communication, presentation | recommendation one-pager + deck (ROADMAP Phase 7) |

## The differentiator

Most "chat with your data" demos will confidently return a **wrong number** —
the SQL silently answered a different question. AskData's verification layer
checks schema validity, judges whether the SQL actually answers the question,
sanity-checks the result, and repairs or **abstains** — tagging every answer
**trusted / repaired / abstained**. The evaluation harness measures how much
this cuts confidently-wrong answers; that measurement is also the research
paper ([`paper/DRAFT.md`](paper/DRAFT.md)).

The golden set includes deliberately **ambiguous** and **unanswerable** questions
(profit margin, churn — data that isn't there), where the only correct behavior
is to decline. A naive agent answers them anyway; that's the headline metric.

## Predictive model — result on the full Olist data (95,823 orders)

```
ROC-AUC 0.756 · PR-AUC 0.469 · bad-review base rate 12.8%
Flagging the riskiest 10% of orders catches 41% of all bad reviews (4.1x random)
Top driver: delivery delay — then basket size and promised lead time
```

Business framing: proactive outreach (support ticket, goodwill voucher, seller
coaching) targeted with this model reaches 4x more soon-to-be-unhappy customers
per contact than untargeted outreach. Scores land in `dw.mart_review_risk` so
at-risk orders surface in the same BI layer as everything else.

## Dataset & stack

- **[Olist Brazilian E-Commerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)** — public, realistic relational schema (100k orders). A built-in synthetic sample with the same schema means the repo runs with zero downloads.
- **DuckDB** — raw tables + `dw` star schema in one file; SQL is BigQuery-portable
- **Python / scikit-learn** — review-risk model
- **Provider-agnostic LLM client** — Anthropic, OpenAI, or free local models via Ollama (`ASKDATA_PROVIDER=ollama`)
- **Streamlit** — demo app with the confidence badge front and center
- A from-scratch agent loop (no framework) so the mechanics are legible to a reader

## Quickstart

```bash
pip install -r requirements.txt && pip install -e .
python -m askdata.load_data        # data/askdata.duckdb (synthetic sample, or full Olist if CSVs in data/olist/)
python -m askdata.warehouse        # star schema + marts (dw.*)
python -m predict.review_risk      # trains + prints the business readout + writes dw.mart_review_risk
pytest                             # 28 tests, no API key needed

cp .env.example .env               # add ANTHROPIC_API_KEY / OPENAI_API_KEY (or use Ollama)
streamlit run app/app.py           # the demo
python -m eval.run                 # baseline vs verified — the paper's results
```

## Evaluation

[`eval/golden.jsonl`](eval/golden.jsonl): 150 questions across six tiers — lookup
(20), aggregation (26), multi-join (30), temporal (24), **ambiguous** (18),
**unanswerable** (32). Gold answers
come from executing gold SQL on the same database. `python -m eval.run` compares
the naive agent against AskData and reports the **confidently-wrong rate** (the
headline), accuracy, abstention, repair success, and the latency/token cost of
trust. Results land in `eval/reports/`.

## Results — pilot runs (42-question set), full Olist, two providers

_(final campaign on the 150-question set — 3 runs × 3 providers — in progress;
these pilot numbers will be replaced)_

| confidently-wrong rate | baseline | AskData (verified) | reduction |
|---|---|---|---|
| Qwen2.5-Coder-3B (local, Ollama) | 28.6% | **9.5%** | −67% |
| GPT-4o-mini (OpenAI) | 26.2% | **19.0%** | −27% |

Both providers answer wrong-but-confident on over a quarter of realistic
business questions out of the box. Verification removes most of those — and
helps most where the model is weakest, which is the deployment story for
teams running small or local models. Accuracy also rises on both (43→52%
local, 64→69% API) at ~1.5× token cost. Reproduce with `python -m eval.run`;
full tables in [`eval/reports/`](eval/reports) and [`paper/DRAFT.md`](paper/DRAFT.md) §5.

## Repo layout

```
askdata/
├── src/askdata/   # NL agent (llm, schema, sqlgen, verify, agent) + warehouse builder
├── predict/       # review-risk model (predict business outcomes)
├── docs/          # dimensional data model
├── eval/          # golden questions, judge, metrics, runner, reports
├── app/           # Streamlit demo
├── data/          # loader + duckdb file (+ optional data/olist/ CSVs)
├── tests/         # 28 deterministic tests (scripted LLM, synthetic sample)
├── paper/         # failure-mode study + verification layer (draft)
└── notebooks/     # error analysis / failure-mode taxonomy
```

See [`ROADMAP.md`](ROADMAP.md) for the build sequence and what's left.
