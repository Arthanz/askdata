provider: `ollama` · model: `qwen2.5-coder:3b` · tag: `qwen3b-judge54mini-run2`

# AskData evaluation report — 2026-07-04 16:07

| metric | askdata (verification on) |
|---|---|
| n | 150 |
| answered | 35 |
| abstained | 115 |
| correct | 64 |
| accuracy | 0.427 |
| accuracy_answerable | 0.271 |
| confidently_wrong | 3 |
| confidently_wrong_rate | 0.02 |
| hallucinated_unanswerable | 0 |
| repaired | 7 |
| repair_success | 7 |
| avg_attempts | 1.63 |
| avg_seconds | 10.62 |
| total_tokens | 284953 |

## Per-question detail

### askdata (verification on)

| id | tier | status | correct | attempts | failed checks |
|---|---|---|---|---|---|
| L1 | lookup | trusted | True | 1 | - |
| L2 | lookup | abstained | False | 2 | judge.sql_answers_question |
| L3 | lookup | trusted | True | 1 | - |
| L4 | lookup | trusted | True | 1 | - |
| L5 | lookup | trusted | False | 1 | - |
| L6 | lookup | abstained | False | 3 | static.select_only, static.identifiers |
| L7 | lookup | trusted | True | 1 | - |
| L8 | lookup | trusted | False | 1 | - |
| L9 | lookup | repaired | True | 2 | - |
| L10 | lookup | abstained | False | 2 | static.identifiers |
| L11 | lookup | abstained | False | 2 | judge.sql_answers_question |
| L12 | lookup | abstained | False | 2 | - |
| L13 | lookup | trusted | True | 1 | - |
| L14 | lookup | abstained | False | 3 | judge.sql_answers_question |
| A1 | aggregation | abstained | False | 2 | judge.sql_answers_question |
| A2 | aggregation | trusted | True | 1 | - |
| A3 | aggregation | trusted | True | 1 | - |
| A4 | aggregation | repaired | True | 2 | - |
| A5 | aggregation | abstained | False | 2 | - |
| A6 | aggregation | abstained | False | 2 | - |
| A7 | aggregation | repaired | True | 2 | - |
| A8 | aggregation | abstained | False | 2 | - |
| A9 | aggregation | abstained | False | 2 | judge.sql_answers_question |
| A10 | aggregation | abstained | False | 3 | judge.sql_answers_question |
| A11 | aggregation | trusted | True | 1 | - |
| A12 | aggregation | abstained | False | 2 | - |
| A13 | aggregation | abstained | False | 2 | static.identifiers |
| A14 | aggregation | trusted | True | 1 | - |
| A15 | aggregation | abstained | False | 1 | - |
| A16 | aggregation | abstained | False | 1 | - |
| A17 | aggregation | trusted | True | 1 | - |
| A18 | aggregation | abstained | False | 2 | judge.sql_answers_question |
| J1 | join | abstained | False | 3 | static.identifiers |
| J2 | join | abstained | False | 2 | static.identifiers |
| J3 | join | abstained | False | 1 | - |
| J4 | join | trusted | True | 1 | - |
| J5 | join | abstained | False | 3 | static.select_only, static.identifiers |
| J6 | join | abstained | False | 2 | judge.sql_answers_question |
| J7 | join | abstained | False | 1 | - |
| J8 | join | abstained | False | 2 | - |
| J9 | join | abstained | False | 1 | - |
| J10 | join | abstained | False | 3 | static.select_only, static.identifiers |
| J11 | join | abstained | False | 2 | judge.sql_answers_question |
| J12 | join | abstained | False | 2 | - |
| J13 | join | trusted | True | 1 | - |
| J14 | join | abstained | False | 3 | static.select_only, static.identifiers |
| J15 | join | trusted | False | 1 | - |
| J16 | join | trusted | True | 1 | - |
| J17 | join | abstained | False | 1 | - |
| J18 | join | abstained | False | 3 | static.select_only, static.identifiers |
| J19 | join | abstained | False | 2 | judge.sql_answers_question |
| J20 | join | trusted | True | 1 | - |
| T1 | temporal | repaired | True | 2 | - |
| T2 | temporal | trusted | True | 1 | - |
| T3 | temporal | abstained | False | 3 | static.select_only |
| T4 | temporal | trusted | True | 1 | - |
| T5 | temporal | abstained | False | 2 | static.select_only, static.identifiers |
| T6 | temporal | abstained | False | 2 | judge.sql_answers_question |
| T7 | temporal | trusted | True | 1 | - |
| T8 | temporal | abstained | False | 2 | - |
| T9 | temporal | abstained | False | 1 | - |
| T10 | temporal | abstained | False | 3 | judge.sql_answers_question |
| T11 | temporal | abstained | False | 2 | - |
| T12 | temporal | abstained | False | 3 | static.identifiers |
| T13 | temporal | abstained | False | 2 | static.identifiers |
| T14 | temporal | abstained | False | 2 | static.identifiers |
| T15 | temporal | abstained | False | 2 | static.identifiers |
| T16 | temporal | abstained | False | 2 | static.identifiers |
| M1 | ambiguous | abstained | False | 2 | static.identifiers |
| M2 | ambiguous | abstained | False | 1 | - |
| M3 | ambiguous | abstained | False | 1 | - |
| M4 | ambiguous | abstained | False | 1 | - |
| M5 | ambiguous | abstained | False | 1 | - |
| M6 | ambiguous | abstained | False | 1 | - |
| M7 | ambiguous | abstained | False | 3 | static.select_only, static.identifiers |
| M8 | ambiguous | abstained | False | 2 | judge.sql_answers_question |
| M9 | ambiguous | abstained | False | 1 | - |
| M10 | ambiguous | abstained | False | 1 | - |
| M11 | ambiguous | abstained | False | 1 | - |
| M12 | ambiguous | abstained | False | 1 | - |
| U1 | unanswerable | abstained | True | 2 | static.identifiers |
| U2 | unanswerable | abstained | True | 1 | - |
| U3 | unanswerable | abstained | True | 1 | - |
| U4 | unanswerable | abstained | True | 1 | - |
| U5 | unanswerable | abstained | True | 2 | judge.sql_answers_question |
| U6 | unanswerable | abstained | True | 1 | - |
| U7 | unanswerable | abstained | True | 2 | static.identifiers |
| U8 | unanswerable | abstained | True | 1 | - |
| U9 | unanswerable | abstained | True | 2 | static.identifiers |
| U10 | unanswerable | abstained | True | 1 | - |
| U11 | unanswerable | abstained | True | 1 | - |
| U12 | unanswerable | abstained | True | 1 | - |
| U13 | unanswerable | abstained | True | 1 | - |
| U14 | unanswerable | abstained | True | 2 | static.select_only, static.identifiers |
| U15 | unanswerable | abstained | True | 1 | - |
| U16 | unanswerable | abstained | True | 2 | static.identifiers |
| U17 | unanswerable | abstained | True | 1 | - |
| U18 | unanswerable | abstained | True | 1 | - |
| U19 | unanswerable | abstained | True | 1 | - |
| U20 | unanswerable | abstained | True | 1 | - |
| L15 | lookup | abstained | False | 3 | static.select_only, static.identifiers |
| L16 | lookup | trusted | True | 1 | - |
| L17 | lookup | abstained | False | 1 | - |
| L18 | lookup | trusted | True | 1 | - |
| L19 | lookup | repaired | True | 3 | - |
| L20 | lookup | abstained | False | 3 | static.select_only, static.identifiers |
| A19 | aggregation | trusted | True | 1 | - |
| A20 | aggregation | repaired | True | 3 | - |
| A21 | aggregation | abstained | False | 2 | - |
| A22 | aggregation | trusted | True | 1 | - |
| A23 | aggregation | abstained | False | 2 | judge.sql_answers_question |
| A24 | aggregation | trusted | True | 1 | - |
| A25 | aggregation | abstained | False | 3 | - |
| A26 | aggregation | trusted | True | 1 | - |
| J21 | join | abstained | False | 2 | static.identifiers |
| J22 | join | abstained | False | 1 | - |
| J23 | join | repaired | True | 2 | - |
| J24 | join | abstained | False | 2 | static.identifiers |
| J25 | join | abstained | False | 2 | - |
| J26 | join | abstained | False | 2 | judge.sql_answers_question |
| J27 | join | abstained | False | 2 | - |
| J28 | join | abstained | False | 3 | judge.sql_answers_question |
| J29 | join | abstained | False | 3 | static.select_only, static.identifiers |
| J30 | join | abstained | False | 2 | - |
| T17 | temporal | trusted | True | 1 | - |
| T18 | temporal | abstained | False | 1 | - |
| T19 | temporal | abstained | False | 2 | judge.sql_answers_question |
| T20 | temporal | trusted | True | 1 | - |
| T21 | temporal | abstained | False | 2 | static.identifiers |
| T22 | temporal | abstained | False | 3 | static.select_only |
| T23 | temporal | abstained | False | 3 | static.identifiers |
| T24 | temporal | abstained | False | 1 | - |
| M13 | ambiguous | abstained | False | 1 | - |
| M14 | ambiguous | abstained | False | 1 | - |
| M15 | ambiguous | abstained | False | 1 | - |
| M16 | ambiguous | abstained | False | 1 | - |
| M17 | ambiguous | abstained | False | 1 | - |
| M18 | ambiguous | abstained | False | 1 | - |
| U21 | unanswerable | abstained | True | 2 | static.identifiers |
| U22 | unanswerable | abstained | True | 2 | static.identifiers |
| U23 | unanswerable | abstained | True | 1 | - |
| U24 | unanswerable | abstained | True | 1 | - |
| U25 | unanswerable | abstained | True | 1 | - |
| U26 | unanswerable | abstained | True | 2 | static.select_only, static.identifiers |
| U27 | unanswerable | abstained | True | 1 | - |
| U28 | unanswerable | abstained | True | 1 | - |
| U29 | unanswerable | abstained | True | 1 | - |
| U30 | unanswerable | abstained | True | 1 | - |
| U31 | unanswerable | abstained | True | 1 | - |
| U32 | unanswerable | abstained | True | 2 | static.identifiers |
