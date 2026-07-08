# Roadmap

**Done**

- Data loader (Olist → DuckDB) with a schema-identical synthetic sample
- Provider-agnostic LLM client (Anthropic / OpenAI / Gemini / Ollama)
- Agent: schema context → SQL → execute → verify → repair → answer,
  with trusted / repaired / abstained statuses
- 29 deterministic tests (scripted LLM, no API key)
- Golden set: 150 questions in six tiers, incl. ambiguous and unanswerable;
  all gold SQL validated against both the full data and the sample
- Star-schema warehouse (`dw`) + marts, documented in `docs/DATA_MODEL.md`
- Review-risk model on the full data (ROC-AUC 0.756, 4.1x top-decile lift),
  scores landed back as `dw.mart_review_risk`
- Streamlit app with confidence badges
- Pilot eval runs (42-question set) on Ollama and OpenAI
- Full eval campaign: 150 questions × 5 models × 3 runs, reported as
  mean ± sd with exact McNemar paired significance tests (`eval/reports/AGGREGATE.md`)
- Generator–judge 2×2 factorial (weak/strong generator × weak/strong judge)
- GPT-5.4 within-family sweep: nano / mini / full
- Ablation: which verification check fires on which failure class (paper §5)
- Error-analysis pass → failure-mode taxonomy (paper §6)
- Paper draft complete through §7 (paper/DRAFT.md)

**Next**

- Format paper for target venue
- ~~Deploy the Streamlit app~~ ✅ live at askdata-arthanz.streamlit.app
- Optional: push marts to BigQuery + a public Looker Studio dashboard
- Short findings deck (delivery delay → review risk → targeted outreach)
