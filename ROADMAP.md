# Roadmap — scratch to finish (full JD-aligned scope)

Sequenced so every phase produces something showable, and so the pieces the
Deloitte JD weights most (a prediction + a warehouse + a recommendation you can
present) all get built — not just the flashy agent.

**Phase 0 — Foundation** ✅
README, paper outline, repo skeleton, roadmap.

**Phase 1 — Agent core** ✅
Data loader (Olist → DuckDB) + synthetic sample, provider-agnostic LLM client
(Anthropic / OpenAI / Ollama), base agent: schema context → SQL → execute → answer.

**Phase 2 — The differentiator** ✅
Verification layer (static schema checks, does-the-SQL-answer-the-question
judge, sanity checks, repair loop, trusted/repaired/abstained status) + 28
deterministic tests with a scripted LLM.

**Phase 3 — Eval harness** ✅
42 golden questions across 6 tiers (incl. ambiguous + unanswerable), metrics,
LLM answer-equivalence judge, markdown/JSON report. First full run done on the
full Olist with a free local model (Qwen2.5-Coder-3B via Ollama):
**verification cuts the confidently-wrong rate 28.6% → 9.5% (−67%) at 1.45×
token cost.** Remaining: replicate on ≥1 API provider (~$5 credit) for the
paper's robustness claim.

**Phase 4 — Warehouse** ✅
Kimball star schema (`dw` schema in DuckDB, BigQuery-portable SQL): 5 dims +
order-item-grain fact + `mart_delivery_performance` / `mart_review_health`.
Documented in `docs/DATA_MODEL.md`.

**Phase 5 — Predict a business outcome** ✅
Review-risk model on the real data: **ROC-AUC 0.756; top-decile outreach
catches 41% of bad reviews (4.1x random); delivery delay is the top driver.**
Scores land back in the warehouse as `dw.mart_review_risk`.

**Phase 6 — Demo + dashboard** ✅ (app) / ⏳ (deploy, dashboard)
Streamlit app with confidence badges done. Remaining: deploy to a public URL;
optional Looker Studio dashboard on the marts (delivery performance, review
health, at-risk orders).

**Phase 7 — Paper** ⏳
Full draft exists (`paper/DRAFT.md`) with placeholders keyed to the eval report.
Remaining: run the eval, paste numbers, error-analysis notebook pass, format
for target venue.

**Phase 8 — Recommendation deck + polish** ⏳
The consulting wrapper: a short deck framing findings as a client
recommendation with quantified impact ("proactive outreach on the top risk
decile reaches 4.1x more at-risk customers per contact"). Then: README results,
architecture diagram, 60-second Loom, LinkedIn write-up.
