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
incorrect result with no signal of uncertainty. Using a 42-question golden set
over the public Olist e-commerce dataset — spanning lookup, aggregation,
multi-join, temporal, deliberately *ambiguous*, and deliberately *unanswerable*
questions — we show that a naive LLM agent produces confidently-wrong answers on
**[X]%** of questions, and answers **[X] of 6** unanswerable questions instead of
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

Public benchmarks under-measure this. Spider and BIRD score execution accuracy
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

The contribution is deliberately not a new generator: it is an evaluation and an
intervention that any text-to-SQL stack can adopt.

## 2. Related work

**Text-to-SQL benchmarks.** Spider [Yu et al., 2018] and BIRD [Li et al., 2023]
established execution accuracy on complex schemas; recent work adds dialect and
efficiency concerns. These benchmarks assume every question is answerable, so
abstention behavior goes unmeasured.

**Self-verification and LLM-as-a-judge.** Self-consistency [Wang et al., 2023],
self-refine [Madaan et al., 2023] and judge-style evaluation [Zheng et al., 2023]
show models can usefully critique generated artifacts. We apply the judge idea
*inside* the serving path — as a gate, not an offline metric.

**Abstention and selective prediction.** Selective QA [Kamath et al., 2020] and
hallucination-abstention work establish that declining to answer is a first-class
capability. We port that framing to the analytics-agent setting, where an
abstention is cheap (the user rephrases) but a wrong number is expensive.

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

**Dataset.** Olist Brazilian E-Commerce (public, ~100k orders, 8 relational
tables). Experiments run on the full dump; the repo also ships a schema-identical
synthetic sample so the harness is reproducible with zero downloads.

**Golden set.** 42 questions in six tiers: lookup (8), aggregation (9),
multi-join (8), temporal (7), ambiguous (4), unanswerable (6). Answerable
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

**Configurations.** Baseline (verification off) vs. AskData (verification on),
each run with two model providers to check the effect is not provider-specific.

## 5. Results

> Numbers below come from `eval/reports/report_*.json`; the table is generated
> by `python -m eval.run`.

### First provider: Qwen2.5-Coder-3B (local, via Ollama) — 2026-07-03

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

[Fill during formatting: Spider (Yu et al., EMNLP 2018); BIRD (Li et al.,
NeurIPS 2023); Self-Consistency (Wang et al., ICLR 2023); Self-Refine (Madaan
et al., NeurIPS 2023); LLM-as-a-judge (Zheng et al., NeurIPS 2023); Selective QA
(Kamath et al., ACL 2020).]
