# Reducing Confidently-Wrong Answers in LLM Data-Analytics Agents: A Failure-Mode Study and a Lightweight Verification Layer

**Status:** full draft — placeholders marked `[..]` are filled from `eval/reports/`
after running `python -m eval.run` on the full Olist data with ≥2 providers.

---

## Abstract

Large language model (LLM) agents that answer natural-language questions over
relational data ("chat with your data") are now easy to build and demo, but hard
to trust. Existing text-to-SQL benchmarks measure whether a system *can* produce
a correct query; they say little about what the system does when it *cannot* —
which, in an interactive analytics setting, determines whether users can rely on
it at all. We study the dominant real-world failure mode of such agents:
**confidently-wrong answers**, where the agent returns a plausible-looking but
incorrect result with no signal of uncertainty. Using a 150-question golden set
over the public Olist e-commerce dataset — spanning lookup, aggregation,
multi-join, temporal, deliberately *ambiguous*, and deliberately *unanswerable*
questions — we show that a naive LLM agent produces confidently-wrong answers on
**[X]%** of questions, and answers **[X] of 32** unanswerable questions instead of
declining. We then add a lightweight, model-agnostic verification layer — static
schema checks, result sanity checks, an LLM judge that asks *"does this SQL
answer this question?"*, and a bounded repair loop — that assigns every answer a
status of *trusted*, *repaired*, or *abstained*. Verification reduces the
confidently-wrong rate by **[X]%** (relative) at a cost of **[X]×** tokens and
**[X]×** latency, without fine-tuning or schema-specific engineering. We release
the system, the golden set, and the harness for reproduction.

## 1. Introduction

Text-to-SQL generation has improved to the point where a competent demo can be
assembled in an afternoon: give a model the schema, ask a question, execute the
query, display the result. The gap between that demo and a tool an analyst can
rely on is not primarily generation quality — it is that the system has **no
notion of when it is wrong**. A query that executes successfully and returns a
plausible number is indistinguishable, to the user, from a correct answer. When
the SQL silently answers a slightly different question (wrong filter, wrong
grain, missing join) the result is a *confidently-wrong* answer, which in a
business setting is strictly worse than an error message: it gets pasted into
slides.

Public benchmarks under-measure this. Spider [1] and BIRD [3] score execution accuracy
on answerable questions; they do not ask what a system does with a question the
schema cannot answer, or an ambiguous question with several defensible readings.
Interactive analytics encounters both constantly.

**Contributions.**
1. A **failure-mode study**: a golden evaluation set over a public e-commerce
   dataset whose tiers include ambiguous and unanswerable questions, plus a
   taxonomy of the errors a naive agent actually makes (§6).
2. A **lightweight verification layer** — static identifier checks, result
   sanity checks, an LLM SQL-judge, and a bounded repair loop — that attaches a
   *trusted / repaired / abstained* status to every answer (§3).
3. **Measurements** of the trade-off: the reduction in confidently-wrong answers
   against the token/latency overhead, with ablations showing which check does
   the work (§5).
4. A **generator–judge factorial**: by decoupling the judge model from the
   generator, we test whether verification quality is a property of the judge
   rather than of the pipeline — to our knowledge the first such decomposition
   for text-to-SQL verification, with direct consequences for deploying cheap
   local generators under a thin layer of strong-judge calls.

The contribution is deliberately not a new generator: it is an evaluation and an
intervention that any text-to-SQL stack can adopt.

## 2. Related work

**Text-to-SQL generation and its benchmarks.** Semantic parsing of natural
language into SQL has a long history; the modern era was defined by Spider [1],
which introduced cross-domain evaluation over 200 databases and made
execution-based metrics standard, later hardened against false positives by
distilled test suites [2]. BIRD [3] scaled the setting to larger, noisier
databases and added execution-efficiency concerns, and its leaderboard has been
dominated by LLM-based systems since. Prompting-based methods now define the
state of the art: DIN-SQL [4] decomposes the task into sub-problems with a
self-correction stage, and DAIL-SQL [5] systematically benchmarks prompt
designs, approaching human performance on Spider. All of this work measures
whether a system *can* produce correct SQL. None of it models what the system
should do when it cannot — every question in Spider and BIRD has an answer, so
a system that never abstains is never penalized.

**Reliability and unanswerable questions.** A smaller thread addresses exactly
that gap. EHRSQL [6] was, to our knowledge, the first text-to-SQL benchmark to
include unanswerable questions (about a third of its validation and test
splits), arguing that hospital deployments cannot tolerate confident guesses;
its 2024 shared task made abstention a first-class part of the evaluation.
TrustSQL [7] generalizes this into a reliability benchmark by re-annotating
three datasets with infeasible questions and scoring models with an explicit
penalty for wrong answers over abstentions. Our work is complementary: rather
than proposing another benchmark, we contribute (i) an *intervention* — a
model-agnostic verification layer that any text-to-SQL stack can adopt without
fine-tuning — and (ii) an evaluation grounded in a realistic business-analytics
schema, with an error taxonomy connecting failure classes to the checks that
catch them. Where TrustSQL scores a model's own abstention decisions, we
measure how much an external verification layer improves a generator that was
not trained to abstain.

**Self-verification and critique.** Hallucination in generative models is well
documented [8]. Several lines of work show LLMs can usefully critique their own
or other models' outputs: SelfCheckGPT [9] detects hallucination by sampling
multiple generations and measuring consistency; self-consistency decoding [10]
aggregates sampled reasoning paths; Self-Refine [11] and Reflexion [12] feed a
model's critique back into regeneration, a loop our repair mechanism instantiates
for SQL; CRITIC [13] grounds the critique in external tool calls — the closest
in spirit to our judge, which sees the executed result, not just the query
text. LLM-as-a-judge evaluation was validated (and its biases catalogued) by
Zheng et al. [14]. We differ in *where* the judge sits: not as an offline
evaluation metric but as a gate in the serving path, with its verdict deciding
whether an answer reaches the user.

**Selective prediction.** Declining to answer under uncertainty is an
established capability in QA: Kamath et al. [15] trained calibrators for
selective question answering under domain shift, and Cole et al. [16] study
abstention on ambiguous questions. We port this framing to interactive
analytics, where the asymmetry is stark — an abstention costs the user a
rephrase, while a confidently-wrong number can silently enter a business
decision.

## 3. System

AskData is a from-scratch agent loop (no framework) over DuckDB:
**schema-aware prompt → SQL generation → read-only execution → verification →
answer**, with the verification verdict driving a repair loop.

**Generation.** The prompt contains the introspected schema (tables, columns,
types, row counts), explicit join keys, and business notes (e.g. the
per-order vs. per-person customer-ID distinction in Olist). Two behaviors are
prompted, and both are *checked* downstream rather than assumed: the model must
output `ABSTAIN` when the schema cannot answer the question, and must state an
`-- assumption:` comment when it resolves an ambiguity.

**Verification.** Three check families run after generation:

1. **Static (no LLM):** the query must be a single read-only SELECT; every
   identifier must resolve to a schema table/column or a query-local alias.
   Catches invented columns before execution.
2. **Sanity (no LLM):** non-empty result, not all-NULL, no negative values in
   count/total-like columns.
3. **Judge (one LLM call):** given the schema, question, SQL, and a result
   preview, a model answers *"does executing this SQL genuinely answer this
   question?"* — targeting the silent-mismatch failure mode that execution
   cannot catch.

**Repair and status.** Any failed check becomes feedback for a regeneration
attempt (max 3). Answers passing on attempt 1 are **trusted**; on a later
attempt, **repaired**; if attempts are exhausted or the model declines, the agent
**abstains** with the reason. The baseline used in §5 is the same agent with
verification off: first executable query wins and is always presented as trusted
— which is exactly what most deployed demos do.

## 4. Evaluation setup

**Dataset.** Olist Brazilian E-Commerce [17] (public, ~100k orders, 8 relational
tables). Experiments run on the full dump; the repo also ships a schema-identical
synthetic sample so the harness is reproducible with zero downloads.

**Golden set.** 150 questions in six tiers: lookup (20), aggregation (26),
multi-join (30), temporal (24), ambiguous (18), unanswerable (32 — 21% of the
set, following EHRSQL's precedent of weighting unanswerable questions heavily
[6]). Answerable
questions carry gold SQL, executed against the same database at eval time — so
gold answers are correct by construction. Unanswerable questions (profit margin,
churn, marketing channel, returns, conversion, customer age) reference data that
does not exist in the schema; the correct behavior is abstention. Ambiguous
questions accept either the modal business interpretation or an abstention.

**Scoring.** Result equivalence is order- and column-name-insensitive (bag-of-
values per row, rows sorted, floats rounded), the standard execution-match
relaxation; a scalar gold answer contained in a one-row result also counts. An
optional LLM answer-equivalence judge (disabled by default) provides a second
score for shaped-differently answers; we report both.

**Metrics.** Accuracy (overall and answerable-only); **confidently-wrong rate**
(answers presented as trusted/repaired that are wrong — the headline);
hallucinated-unanswerable count; abstention rate; repair success rate; attempts,
latency, and token overhead.

**Configurations.** Baseline (verification off) vs. AskData (verification on).
Each configuration runs three times per model; we report mean ± sd across runs
and an exact McNemar test on paired per-question confidently-wrong outcomes.

**Model selection.** Models were chosen to span deployment tiers while
controlling the confounds that cross-vendor comparisons usually carry:

- *Qwen2.5-Coder-3B (local, via Ollama)* — the on-premise/privacy tier:
  organizations in regulated settings often cannot send data to external APIs.
  It is also the weakest generator in the study, anchoring the capability axis;
  we use a code-specialized model so that small-model results are not an
  artifact of evaluating a generalist.
- *gpt-oss-120B (open weights, via Cerebras)* — the strongest self-hostable
  open model, testing whether openness at scale behaves like a closed frontier
  model.
- *GPT-5.4-nano / -mini / -full* — a **within-family capability sweep**: same
  lab, same generation, same training recipe, so generator capability is the
  only variable. Prior comparisons across vendors confound capability with
  training data, alignment style, and API behavior.
- *GPT-4o-mini* — a previous-generation anchor and, in practice, the most
  widely deployed budget API model.

**Generator–judge factorial.** Self-verification couples two distinct
abilities: *generating* SQL and *judging* it. Because our judge is an
independent model call, we can decouple them: a 2×2 factorial crossing
{weak (3B), strong (5.4-mini)} generators with {weak, strong} judges, holding
every prompt and check constant. If the verification benefit tracks judge
capability rather than generator capability, the deployment implication is
direct: run a cheap local generator and spend a small API budget on judge
calls only.

## 5. Results

> Numbers below come from `eval/reports/report_*.json`; the table is generated
> by `python -m eval.run`.

> **Note:** the two tables below are pilot runs on the initial 42-question set
> (single run each). They are superseded by the final campaign on the
> 150-question set (3 runs per provider per configuration, reported as
> mean ± sd) and are kept here only until those tables land.

### Pilot, first provider: Qwen2.5-Coder-3B (local, via Ollama) — 2026-07-03

| metric | baseline | AskData (verified) |
|---|---|---|
| accuracy (all 42) | 0.429 | 0.524 |
| accuracy (answerable only) | 0.361 | 0.472 |
| **confidently-wrong rate** | **0.286** (12/42) | **0.095** (4/42) |
| abstained | 17 | 21 |
| repaired / repair success | 2 / 1 | 3 / 1 |
| avg latency per question | 6.4 s | 8.9 s (1.39×) |
| total tokens | 51,956 | 75,333 (1.45×) |

**Headline: verification reduces the confidently-wrong rate by 67% relative
(28.6% → 9.5%) at 1.45× token cost.** Notably, the baseline already abstains
often because the generation prompt itself offers an ABSTAIN escape — i.e.
this is a *conservative* baseline, and the verification layer still removes
two-thirds of the remaining confidently-wrong answers. On the unanswerable
tier, both configurations hallucinated once (the 3B judge shares the
generator's blind spot — see §7).

### Second provider: GPT-4o-mini (OpenAI API) — 2026-07-04

| metric | baseline | AskData (verified) |
|---|---|---|
| accuracy (all 42) | 0.643 | 0.690 |
| accuracy (answerable only) | 0.583 | 0.639 |
| **confidently-wrong rate** | **0.262** (11/42) | **0.190** (8/42) |
| hallucinated unanswerable | 0/6 | 0/6 |
| abstained | 10 | 11 |
| avg latency per question | 3.9 s | 3.4 s |
| total tokens | 42,369 | 67,115 (1.58×) |

### Cross-provider reading

The effect replicates in direction on both providers but its *size* tracks
generator strength: −67% relative on the 3B local model vs. −27% on
GPT-4o-mini. Verification does the most work where the generator is weakest —
the practical deployment story for organizations running small or local
models. The stronger model needs no help declining unanswerable questions
(0/6 hallucinated even at baseline; the prompt's ABSTAIN escape suffices),
whereas its residual confidently-wrong answers are silent wrong-question SQL —
the class the LLM judge targets but does not fully catch (§6, §7). Latency
overhead was negligible on the API provider (verification added one judge call
but reduced failed-execution retries). Both runs used the same golden set,
database, prompts, and strict structural answer comparison; enabling the
answer-equivalence judge (`--use-judge`) would loosen near-miss formatting
mismatches for both configurations equally.

**Headline.** [Table 1: baseline vs verified × provider — accuracy,
confidently-wrong rate, abstentions, hallucinated-unanswerable.]

- Baseline confidently-wrong rate: **[X]%** of all questions; on unanswerable
  questions the baseline answered **[X]/6** with fabricated proxies.
- With verification: confidently-wrong rate falls to **[X]%** (**[X]%** relative
  reduction); **[X]/6** unanswerable questions correctly abstained.
- Repair loop: **[X]** first-attempt failures were converted into correct
  answers (repair success **[X]%**), i.e. verification does not merely abstain —
  it recovers.

**Cost of trust.** Verification adds **[X]×** tokens and **[X]×** wall-clock
latency per question (judge call + occasional retries). [Discussion: framed
against the cost of one wrong number reaching a decision.]

**Verifier quality.** Precision/recall of the verification verdict against
ground-truth correctness: of the answers the verifier let through as *trusted*,
**[X]%** were actually correct; of the answers it blocked, **[X]%** were indeed
wrong. [False-block examples.]

**Ablations.** [Which check catches what: static checks catch invented
identifiers cheaply; sanity checks catch empty-result queries; the LLM judge is
the only check that catches silent wrong-question SQL — table of caught-error
counts per check family.]

## 6. Failure-mode taxonomy

From the per-question logs (`notebooks/error_analysis.py`), errors observed in
the baseline cluster into: **(a) silent wrong-question SQL** — executes, looks
right, answers a different question (wrong filter/grain/metric); **(b) invented
schema** — columns or tables that don't exist; **(c) proxy fabrication** — for
unanswerable questions, substituting a lookalike metric (e.g. cancellation rate
for return rate) without flagging it; **(d) unresolved ambiguity** — silently
choosing one reading of an ambiguous question; **(e) degenerate results** —
empty or all-NULL outputs presented as answers. [Counts + one worked example
per class, with the check family that catches it.]

## 7. Discussion and limitations

Single schema and language pair; the golden set is small (42) relative to
benchmark suites, though it covers tiers those suites omit; the judge shares a
provider with the generator in our default setup (correlated blind spots) — we
mitigate by cross-provider runs; ambiguous-question scoring accepts one modal
interpretation. The verifier is a gate, not a proof: §5's verifier-precision
numbers quantify how far "trusted" can be trusted.

## 8. Conclusion

Trust, not generation, is the bottleneck for LLM analytics agents. A small,
model-agnostic verification layer — cheap static checks, one judge call, a
bounded repair loop, and the option to abstain — measurably reduces the failure
mode that matters most in practice, at a token cost that is easy to justify
against the cost of a wrong number in a boardroom slide.

## References

[1] T. Yu, R. Zhang, K. Yang, M. Yasunaga, D. Wang, Z. Li, J. Ma, I. Li,
Q. Yao, S. Roman, Z. Zhang, and D. Radev, "Spider: A large-scale
human-labeled dataset for complex and cross-domain semantic parsing and
text-to-SQL task," in *Proc. EMNLP*, 2018, pp. 3911–3921.

[2] R. Zhong, T. Yu, and D. Klein, "Semantic evaluation for text-to-SQL with
distilled test suites," in *Proc. EMNLP*, 2020, pp. 396–411.

[3] J. Li, B. Hui, G. Qu, J. Yang, B. Li, B. Li, B. Wang, B. Qin, R. Geng,
N. Huo, X. Zhou, C. Ma, G. Li, K. C. C. Chang, F. Huang, R. Cheng, and
Y. Li, "Can LLM already serve as a database interface? A BIg bench for
large-scale database grounded text-to-SQLs," in *Proc. NeurIPS Datasets and
Benchmarks Track*, 2023.

[4] M. Pourreza and D. Rafiei, "DIN-SQL: Decomposed in-context learning of
text-to-SQL with self-correction," in *Proc. NeurIPS*, 2023.

[5] D. Gao, H. Wang, Y. Li, X. Sun, Y. Qian, B. Ding, and J. Zhou,
"Text-to-SQL empowered by large language models: A benchmark evaluation,"
*Proc. VLDB Endowment*, vol. 17, no. 5, pp. 1132–1145, 2024.

[6] G. Lee, H. Hwang, S. Bae, Y. Kwon, W. Shin, S. Yang, M. Seo, J.-Y. Kim,
and E. Choi, "EHRSQL: A practical text-to-SQL benchmark for electronic
health records," in *Proc. NeurIPS Datasets and Benchmarks Track*, 2022.

[7] G. Lee, W. Chay, S. Cho, and E. Choi, "TrustSQL: Benchmarking text-to-SQL
reliability with penalty-based scoring," arXiv:2403.15879, 2024.

[8] Z. Ji, N. Lee, R. Frieske, T. Yu, D. Su, Y. Xu, E. Ishii, Y. Bang,
A. Madotto, and P. Fung, "Survey of hallucination in natural language
generation," *ACM Computing Surveys*, vol. 55, no. 12, pp. 1–38, 2023.

[9] P. Manakul, A. Liusie, and M. J. F. Gales, "SelfCheckGPT: Zero-resource
black-box hallucination detection for generative large language models,"
in *Proc. EMNLP*, 2023, pp. 9004–9017.

[10] X. Wang, J. Wei, D. Schuurmans, Q. Le, E. Chi, S. Narang, A. Chowdhery,
and D. Zhou, "Self-consistency improves chain of thought reasoning in
language models," in *Proc. ICLR*, 2023.

[11] A. Madaan, N. Tandon, P. Gupta, S. Hallinan, L. Gao, S. Wiegreffe,
U. Alon, N. Dziri, S. Prabhumoye, Y. Yang, S. Gupta, B. P. Majumder,
K. Hermann, S. Welleck, A. Yazdanbakhsh, and P. Clark, "Self-Refine:
Iterative refinement with self-feedback," in *Proc. NeurIPS*, 2023.

[12] N. Shinn, F. Cassano, A. Gopinath, K. Narasimhan, and S. Yao,
"Reflexion: Language agents with verbal reinforcement learning," in
*Proc. NeurIPS*, 2023.

[13] Z. Gou, Z. Shao, Y. Gong, Y. Shen, Y. Yang, N. Duan, and W. Chen,
"CRITIC: Large language models can self-correct with tool-interactive
critiquing," in *Proc. ICLR*, 2024.

[14] L. Zheng, W.-L. Chiang, Y. Sheng, S. Zhuang, Z. Wu, Y. Zhuang, Z. Lin,
Z. Li, D. Li, E. P. Xing, H. Zhang, J. E. Gonzalez, and I. Stoica,
"Judging LLM-as-a-judge with MT-Bench and Chatbot Arena," in *Proc.
NeurIPS Datasets and Benchmarks Track*, 2023.

[15] A. Kamath, R. Jia, and P. Liang, "Selective question answering under
domain shift," in *Proc. ACL*, 2020, pp. 5684–5696.

[16] J. R. Cole, M. J. Q. Zhang, D. Gillick, J. M. Eisenschlos, B. Dhingra,
and J. Eisenstein, "Selectively answering ambiguous questions," in
*Proc. EMNLP*, 2023, pp. 530–543.

[17] Olist, "Brazilian e-commerce public dataset by Olist," Kaggle, 2018.
[Online]. Available:
https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
