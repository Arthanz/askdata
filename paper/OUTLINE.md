# Paper outline

**Working title:** Reducing Confidently-Wrong Answers in LLM Data-Analytics
Agents: A Failure-Mode Study and a Lightweight Verification Layer

**Target venues (applied, achievable):** IEEE regional/applied AI conferences
(e.g. ICACSIS, ICAICTA, ISRITI, ICITEE, EECSI) or an applied-NLP/data-systems
workshop. Framed as an *applied systems + evaluation* contribution, not a new
model.

**One-sentence contribution:** We show that LLM chat-with-your-data agents
produce a measurable rate of *confidently-wrong* answers on realistic business
questions, characterize where they fail, and demonstrate that a lightweight,
model-agnostic verification layer reduces that rate by **X%** at a modest
latency/token cost — without fine-tuning.

Why this is publishable even though text-to-SQL is crowded: the crowded part is
*generating* SQL. The under-addressed part is *trusting* the answer in an
interactive analytics setting — abstention, self-verification, and a failure-mode
taxonomy grounded in a reproducible eval. The contribution is the evaluation +
the intervention, not the generator.

---

## 1. Introduction
- The gap between demo-able and trustworthy analytics agents.
- Confidently-wrong answers as the dominant real-world failure mode.
- Contributions: (i) a failure-mode taxonomy, (ii) a golden eval on a public
  dataset, (iii) a verification layer + measured effect.

## 2. Related work
- Text-to-SQL benchmarks (Spider, BIRD) — focus on execution accuracy, less on
  interactive trust/abstention.
- LLM self-verification / self-consistency / LLM-as-a-judge.
- Guardrails and abstention in QA systems.

## 3. System
- Architecture: schema-aware planning → SQL generation → execution → verification
  → answer (with status: trusted / repaired / abstained).
- Verification checks: (a) schema & column validity, (b) LLM-judge "does this SQL
  answer this question", (c) result sanity (empty/degenerate/out-of-range),
  (d) optional self-consistency across sampled generations.
- Repair loop on failure.

## 4. Evaluation setup
- Dataset: Olist (public). Golden set of N natural-language questions with gold
  SQL / gold answers spanning difficulty tiers (lookup, aggregation, multi-join,
  temporal, ambiguous).
- Metrics: execution accuracy, **answer correctness**, **confidently-wrong rate**
  (wrong answer returned as trusted), abstention rate, repair success rate,
  latency/token overhead.
- Baselines: naive agent (no verification) vs. AskData (verification on), across
  ≥2 model providers for robustness.

## 5. Results
- Headline: reduction in confidently-wrong rate.
- Precision/recall of the verifier (does it flag the right answers?).
- Cost of trust: latency/token overhead vs. errors prevented.
- Ablations: which verification check does the work.

## 6. Failure-mode taxonomy
- Categorized error analysis with examples (the qualitative core reviewers like).

## 7. Discussion & limitations
- Where verification still misses; generalization beyond one schema.

## 8. Conclusion

---

## Build → paper mapping (so nothing is wasted)
| Repo artifact | Paper section it feeds |
|---|---|
| `eval/golden.jsonl` | §4 dataset |
| `eval/run.py` report | §5 results tables |
| `notebooks/error_analysis` | §6 taxonomy |
| `src/askdata/verify.py` | §3 system + §5 ablations |
