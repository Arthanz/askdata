# Roadmap

**Done**

- Data loader (Olist → DuckDB) with a schema-identical synthetic sample
- Provider-agnostic LLM client (Anthropic / OpenAI / Gemini / Ollama)
- Agent: schema context → SQL → execute → verify → repair → answer,
  with trusted / repaired / abstained statuses
- 28 deterministic tests (scripted LLM, no API key)
- Golden set: 150 questions in six tiers, incl. ambiguous and unanswerable;
  all gold SQL validated against both the full data and the sample
- Star-schema warehouse (`dw`) + marts, documented in `docs/DATA_MODEL.md`
- Review-risk model on the full data (ROC-AUC 0.756, 4.1x top-decile lift),
  scores landed back as `dw.mart_review_risk`
- Streamlit app with confidence badges
- Pilot eval runs (42-question set) on Ollama and OpenAI

**In progress**

- Full eval campaign: 150 questions × 4 providers × 3 runs, reported as
  mean ± sd with per-question paired significance tests

**Next**

- Error-analysis pass → failure-mode taxonomy with per-class counts (paper §6)
- Ablation: which verification check catches which failure class (paper §5)
- Finish paper draft, format for target venue
- Deploy the Streamlit app to a public URL
- Optional: push marts to BigQuery + a public Looker Studio dashboard
- Short findings deck (delivery delay → review risk → targeted outreach)
