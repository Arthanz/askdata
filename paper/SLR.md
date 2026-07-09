# Systematic literature review — verification and reliability for LLM data-analytics agents

Companion file to `DRAFT.md`. Every reference in the paper was checked against
its source (ACL Anthology, arXiv, VLDB, ACM DL, Kaggle) on 2026-07-10: title,
author list, venue, year, page numbers where cited, and the specific claim the
draft makes about it. One error was found and fixed (the MAC-SQL author
"L.-W. Chai" is Linzheng Chai, so "L. Chai"). Everything else matched.

## Scope and method

The review covers the four threads the paper builds on: text-to-SQL generation
and its benchmarks, reliability and unanswerable questions, self-verification
and critique, and selective prediction. Papers entered the set either because
they define the benchmark landscape the paper positions against (Spider, BIRD
and their successors), or because they are the closest prior work to one of the
paper's components (judge, repair loop, abstention). Inclusion required a
published venue or a widely cited arXiv report; blog posts and leaderboard
entries were excluded.

Questions the review needed to answer:

1. Do existing text-to-SQL benchmarks measure behavior on unanswerable or
   ambiguous questions? (Mostly no; EHRSQL and TrustSQL are the exceptions.)
2. Is there prior work separating the ability to generate SQL from the ability
   to judge it? (No — this is the gap the generator–judge factorial fills.)
3. What forms of LLM self-verification are established, and where does an
   execution-grounded judge sit among them?

## Thread 1 — text-to-SQL generation and benchmarks

**[1] Spider (Yu et al., EMNLP 2018, pp. 3911–3921).** 10,181 questions and
5,693 SQL queries over 200 databases in 138 domains. Made cross-domain
generalization and execution-based evaluation the standard. Every question is
answerable, so abstention is never measured. Verified: venue, pages, the 200
databases figure.

**[3] Distilled test suites (Zhong, Yu & Klein, EMNLP 2020, pp. 396–411).**
Hardens execution-match evaluation: a small suite of databases with high code
coverage for the gold query gives a tight upper bound on semantic accuracy.
They found the original Spider metric produced 2.5% false negatives on average.
This motivates the paper's relaxed result-equivalence scoring. Verified.

**[4] Rajkumar, Li & Bahdanau (arXiv:2204.00498, 2022).** Codex without any
fine-tuning is already a strong Spider baseline; the paper catalogues its
failure modes. Establishes prompting-only text-to-SQL as a serious approach,
which is the setting AskData assumes. Verified.

**[5] DIN-SQL (Pourreza & Rafiei, NeurIPS 2023).** Decomposes generation into
sub-problems with a self-correction stage; roughly +10% few-shot across three
LLMs, state of the art on Spider (85.3%) at publication. Its self-correction
is generation-side; there is no external gate. Verified.

**[6] DAIL-SQL (Gao et al., PVLDB 17(5), 2024, pp. 1132–1145).** Systematic
benchmark of prompt designs (question representation, example selection and
organization); 86.6% execution accuracy on Spider. Verified: volume, issue,
pages, authors.

**[7] CHESS (Talaei et al., arXiv:2405.16755, 2024).** Agentic pipeline with an
Information Retriever and a Schema Selector that prunes large schemas (about 5×
fewer tokens). Relevant as the schema-retrieval flavor of agentic text-to-SQL;
AskData instead passes a full introspected schema because the Olist schema is
small. Verified.

**[8] MAC-SQL (Wang et al., COLING 2025, pp. 540–557).** Three collaborating
agents: Selector, Decomposer, Refiner. The Refiner regenerates SQL on execution
errors, the closest prior mechanism to the paper's repair loop, but it reacts
to hard failures rather than judging silently-wrong results. Verified; author
initial corrected.

**[9] Spider 2.0 (Lei et al., ICLR 2025).** 632 enterprise workflow problems;
o1-preview solves 21.3%. Raises difficulty, keeps every task answerable, so the
confidently-wrong axis remains unmeasured. Verified.

**[2] BIRD (Li et al., NeurIPS 2023 D&B).** 12,751 pairs, 95 databases, 33.4 GB,
dirty data, execution-efficiency analysis. Like Spider, all questions are
answerable. Verified.

## Thread 2 — reliability and unanswerable questions

**[10] EHRSQL (Lee et al., NeurIPS 2022 D&B).** First text-to-SQL benchmark
with unanswerable questions: 33% of each of the validation and test splits,
which the draft rounds to "about a third" — confirmed exact. Hospital setting;
the 2024 shared task made abstention a first-class metric. The paper's golden
set follows its precedent of weighting unanswerable questions heavily. Verified.

**[11] TrustSQL (Lee et al., arXiv:2403.15879, 2024).** Re-annotates ATIS,
Advising, and EHRSQL with infeasible questions ("three datasets" in the draft —
confirmed) and scores with an explicit penalty for wrong answers over
abstentions. Scores a model's own abstention decisions; the paper instead
measures how much an external layer improves a generator not trained to
abstain. Verified.

**[12] Feng et al. (ACL 2024, pp. 14664–14690).** "Don't hallucinate, abstain":
multi-LLM collaboration to identify knowledge gaps; abstention measurably
reduces hallucination in open-domain QA. Won an ACL 2024 SAC award. Verified.

## Thread 3 — self-verification and critique

**[13] Ji et al. (ACM Computing Surveys 55(12), 2023).** Standard survey of
hallucination in natural language generation. Verified against the ACM DL
record.

**[14] Huang et al. (ACM TOIS 2025; arXiv:2311.05232).** LLM-era hallucination
survey with taxonomy; accepted at TOIS (DOI 10.1145/3703155), matching the
draft's dual citation. Verified.

**[15] SelfCheckGPT (Manakul, Liusie & Gales, EMNLP 2023, pp. 9004–9017).**
Detects hallucination by sampling several generations and measuring
consistency. Sampling-based, no external grounding; the paper's judge instead
sees the executed result. Verified.

**[16] Self-consistency (Wang et al., ICLR 2023).** Samples diverse reasoning
paths and takes the majority answer. Verified.

**[17] Self-Refine (Madaan et al., NeurIPS 2023).** The model critiques its own
output and regenerates from the critique, iteratively. The paper's repair loop
instantiates this pattern for SQL with the critique coming from checks rather
than free-form self-feedback. Verified.

**[18] Reflexion (Shinn et al., NeurIPS 2023).** Verbal reinforcement: the
agent stores self-reflections in episodic memory and improves across episodes.
Verified. (The arXiv v3 author list adds E. Berman; the NeurIPS proceedings
list, which the draft cites, has five authors.)

**[19] CRITIC (Gou et al., ICLR 2024).** Grounds critique in external tool
calls. Closest in spirit to the paper's judge, which is grounded in the
executed result preview. Verified.

**[20] Kadavath et al. (arXiv:2207.05221, 2022).** Larger models are well
calibrated about what they know (P(True), P(IK)). This calibration result is
why an LLM judge is plausible at all. Verified.

**[21] Zheng et al. (NeurIPS 2023 D&B).** MT-Bench and Chatbot Arena; GPT-4
judges agree with humans over 80%, with documented position, verbosity, and
self-enhancement biases. The paper moves the judge from offline evaluation into
the serving path. Verified.

**[22] Gu et al. (arXiv:2411.15594, 2024).** Survey of LLM-as-a-judge
reliability strategies and applications. Verified.

## Thread 4 — selective prediction

**[23] Kamath, Jia & Liang (ACL 2020, pp. 5684–5696).** Trains a calibrator to
predict QA errors under domain shift and abstain; beats raw model confidence
(56% vs 48% coverage at 80% accuracy). Verified.

**[24] Cole et al. (EMNLP 2023, pp. 530–543).** Selective answering of
ambiguous questions; sampling-based confidence works better than likelihood on
ambiguous inputs. Directly relevant to the golden set's ambiguous tier.
Verified.

## Infrastructure references

**[25] ReAct (Yao et al., ICLR 2023).** Interleaved reasoning and acting; the
architectural style of the AskData agent loop. Verified.

**[26] Olist (Kaggle, 2018).** About 100k orders from a Brazilian marketplace.
The loader ingests 8 tables (7 olist_* CSVs plus the category-name
translation), matching the "8 relational tables" in §4. Verified against
`src/askdata/load_data.py`.

## Gap analysis

Across the four threads, no prior work does all three of: (a) measure the
confidently-wrong rate rather than accuracy, (b) intervene with a
model-agnostic layer rather than propose a benchmark or a new generator, and
(c) decouple judge capability from generator capability. EHRSQL and TrustSQL
supply (a) in benchmark form. Self-Refine, Reflexion, and CRITIC supply the
repair pattern but never measure it against silent wrong answers over data.
The generator–judge factorial in §5.2 has no direct precedent in the
text-to-SQL literature that this review found.
