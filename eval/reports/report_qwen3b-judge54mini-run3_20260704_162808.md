provider: `ollama` · model: `qwen2.5-coder:3b` · tag: `qwen3b-judge54mini-run3`

# AskData evaluation report — 2026-07-04 16:28

| metric | askdata (verification on) |
|---|---|
| n | 150 |
| answered | 36 |
| abstained | 114 |
| correct | 64 |
| accuracy | 0.427 |
| accuracy_answerable | 0.271 |
| confidently_wrong | 4 |
| confidently_wrong_rate | 0.027 |
| hallucinated_unanswerable | 0 |
| repaired | 5 |
| repair_success | 5 |
| avg_attempts | 1.59 |
| avg_seconds | 8.26 |
| total_tokens | 278368 |

## Per-question detail

### askdata (verification on)

| id | tier | status | correct | attempts | failed checks |
|---|---|---|---|---|---|
| L1 | lookup | trusted | True | 1 | - |
| L2 | lookup | trusted | True | 1 | - |
| L3 | lookup | abstained | False | 2 | static.identifiers |
| L4 | lookup | trusted | True | 1 | - |
| L5 | lookup | trusted | False | 1 | - |
| L6 | lookup | trusted | True | 1 | - |
| L7 | lookup | abstained | False | 1 | - |
| L8 | lookup | abstained | False | 2 | - |
| L9 | lookup | abstained | False | 2 | judge.sql_answers_question |
| L10 | lookup | trusted | True | 1 | - |
| L11 | lookup | abstained | False | 2 | static.identifiers |
| L12 | lookup | abstained | False | 2 | - |
| L13 | lookup | trusted | True | 1 | - |
| L14 | lookup | repaired | True | 2 | - |
| A1 | aggregation | repaired | True | 2 | - |
| A2 | aggregation | trusted | True | 1 | - |
| A3 | aggregation | trusted | True | 1 | - |
| A4 | aggregation | trusted | True | 1 | - |
| A5 | aggregation | trusted | True | 1 | - |
| A6 | aggregation | abstained | False | 3 | judge.sql_answers_question |
| A7 | aggregation | trusted | True | 1 | - |
| A8 | aggregation | abstained | False | 2 | judge.sql_answers_question |
| A9 | aggregation | abstained | False | 2 | - |
| A10 | aggregation | abstained | False | 3 | static.identifiers |
| A11 | aggregation | trusted | True | 1 | - |
| A12 | aggregation | abstained | False | 2 | judge.sql_answers_question |
| A13 | aggregation | abstained | False | 3 | judge.sql_answers_question |
| A14 | aggregation | abstained | False | 2 | - |
| A15 | aggregation | abstained | False | 2 | judge.sql_answers_question |
| A16 | aggregation | repaired | True | 2 | - |
| A17 | aggregation | abstained | False | 2 | static.identifiers |
| A18 | aggregation | abstained | False | 1 | - |
| J1 | join | abstained | False | 2 | static.identifiers |
| J2 | join | abstained | False | 2 | static.identifiers |
| J3 | join | abstained | False | 2 | - |
| J4 | join | trusted | False | 1 | - |
| J5 | join | abstained | False | 3 | - |
| J6 | join | abstained | False | 2 | judge.sql_answers_question |
| J7 | join | abstained | False | 1 | - |
| J8 | join | trusted | True | 1 | - |
| J9 | join | trusted | True | 1 | - |
| J10 | join | trusted | True | 1 | - |
| J11 | join | abstained | False | 2 | - |
| J12 | join | abstained | False | 1 | - |
| J13 | join | abstained | False | 3 | - |
| J14 | join | abstained | False | 2 | - |
| J15 | join | abstained | False | 3 | static.select_only, static.identifiers |
| J16 | join | repaired | True | 3 | - |
| J17 | join | abstained | False | 2 | static.identifiers |
| J18 | join | abstained | False | 1 | - |
| J19 | join | abstained | False | 3 | static.select_only, static.identifiers |
| J20 | join | abstained | False | 3 | static.identifiers |
| T1 | temporal | abstained | False | 2 | - |
| T2 | temporal | trusted | False | 1 | - |
| T3 | temporal | abstained | False | 2 | - |
| T4 | temporal | trusted | True | 1 | - |
| T5 | temporal | abstained | False | 2 | - |
| T6 | temporal | abstained | False | 3 | - |
| T7 | temporal | trusted | True | 1 | - |
| T8 | temporal | trusted | True | 1 | - |
| T9 | temporal | abstained | False | 1 | - |
| T10 | temporal | abstained | False | 3 | judge.sql_answers_question |
| T11 | temporal | abstained | False | 3 | static.identifiers |
| T12 | temporal | abstained | False | 2 | static.identifiers |
| T13 | temporal | abstained | False | 1 | - |
| T14 | temporal | abstained | False | 2 | static.identifiers |
| T15 | temporal | abstained | False | 3 | static.identifiers |
| T16 | temporal | abstained | False | 1 | - |
| M1 | ambiguous | abstained | False | 1 | - |
| M2 | ambiguous | abstained | False | 3 | static.select_only, static.identifiers |
| M3 | ambiguous | abstained | False | 1 | - |
| M4 | ambiguous | abstained | False | 1 | - |
| M5 | ambiguous | abstained | False | 1 | - |
| M6 | ambiguous | abstained | False | 1 | - |
| M7 | ambiguous | abstained | False | 2 | static.identifiers |
| M8 | ambiguous | abstained | False | 1 | - |
| M9 | ambiguous | abstained | False | 1 | - |
| M10 | ambiguous | trusted | True | 1 | - |
| M11 | ambiguous | abstained | False | 2 | judge.sql_answers_question |
| M12 | ambiguous | abstained | False | 1 | - |
| U1 | unanswerable | abstained | True | 1 | - |
| U2 | unanswerable | abstained | True | 1 | - |
| U3 | unanswerable | abstained | True | 1 | - |
| U4 | unanswerable | abstained | True | 1 | - |
| U5 | unanswerable | abstained | True | 2 | - |
| U6 | unanswerable | abstained | True | 1 | - |
| U7 | unanswerable | abstained | True | 1 | - |
| U8 | unanswerable | abstained | True | 1 | - |
| U9 | unanswerable | abstained | True | 1 | - |
| U10 | unanswerable | abstained | True | 1 | - |
| U11 | unanswerable | abstained | True | 1 | - |
| U12 | unanswerable | abstained | True | 1 | - |
| U13 | unanswerable | abstained | True | 1 | - |
| U14 | unanswerable | abstained | True | 2 | judge.sql_answers_question |
| U15 | unanswerable | abstained | True | 2 | static.select_only, static.identifiers |
| U16 | unanswerable | abstained | True | 2 | static.identifiers |
| U17 | unanswerable | abstained | True | 1 | - |
| U18 | unanswerable | abstained | True | 1 | - |
| U19 | unanswerable | abstained | True | 1 | - |
| U20 | unanswerable | abstained | True | 1 | - |
| L15 | lookup | trusted | True | 1 | - |
| L16 | lookup | trusted | True | 1 | - |
| L17 | lookup | abstained | False | 1 | - |
| L18 | lookup | abstained | False | 1 | - |
| L19 | lookup | abstained | False | 3 | judge.sql_answers_question |
| L20 | lookup | trusted | True | 1 | - |
| A19 | aggregation | trusted | True | 1 | - |
| A20 | aggregation | trusted | True | 1 | - |
| A21 | aggregation | abstained | False | 2 | judge.sql_answers_question |
| A22 | aggregation | abstained | False | 1 | - |
| A23 | aggregation | abstained | False | 2 | judge.sql_answers_question |
| A24 | aggregation | repaired | True | 2 | - |
| A25 | aggregation | trusted | True | 1 | - |
| A26 | aggregation | trusted | True | 1 | - |
| J21 | join | abstained | False | 2 | static.identifiers |
| J22 | join | abstained | False | 2 | static.identifiers |
| J23 | join | trusted | False | 1 | - |
| J24 | join | abstained | False | 3 | - |
| J25 | join | abstained | False | 3 | sanity.not_all_null |
| J26 | join | abstained | False | 2 | static.identifiers |
| J27 | join | abstained | False | 2 | - |
| J28 | join | abstained | False | 3 | static.select_only, static.identifiers |
| J29 | join | abstained | False | 3 | - |
| J30 | join | abstained | False | 3 | static.select_only |
| T17 | temporal | trusted | True | 1 | - |
| T18 | temporal | abstained | False | 1 | - |
| T19 | temporal | abstained | False | 3 | - |
| T20 | temporal | abstained | False | 2 | judge.sql_answers_question |
| T21 | temporal | abstained | False | 1 | - |
| T22 | temporal | abstained | False | 2 | - |
| T23 | temporal | abstained | False | 2 | static.select_only, static.identifiers |
| T24 | temporal | abstained | False | 2 | static.select_only, static.identifiers |
| M13 | ambiguous | abstained | False | 2 | static.select_only, static.identifiers |
| M14 | ambiguous | abstained | False | 1 | - |
| M15 | ambiguous | abstained | False | 1 | - |
| M16 | ambiguous | abstained | False | 1 | - |
| M17 | ambiguous | abstained | False | 3 | static.select_only, static.identifiers |
| M18 | ambiguous | abstained | False | 1 | - |
| U21 | unanswerable | abstained | True | 1 | - |
| U22 | unanswerable | abstained | True | 1 | - |
| U23 | unanswerable | abstained | True | 1 | - |
| U24 | unanswerable | abstained | True | 1 | - |
| U25 | unanswerable | abstained | True | 1 | - |
| U26 | unanswerable | abstained | True | 1 | - |
| U27 | unanswerable | abstained | True | 1 | - |
| U28 | unanswerable | abstained | True | 2 | static.select_only |
| U29 | unanswerable | abstained | True | 1 | - |
| U30 | unanswerable | abstained | True | 1 | - |
| U31 | unanswerable | abstained | True | 1 | - |
| U32 | unanswerable | abstained | True | 1 | - |
