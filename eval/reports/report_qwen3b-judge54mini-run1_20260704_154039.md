provider: `ollama` · model: `qwen2.5-coder:3b` · tag: `qwen3b-judge54mini-run1`

# AskData evaluation report — 2026-07-04 15:40

| metric | askdata (verification on) |
|---|---|
| n | 150 |
| answered | 37 |
| abstained | 113 |
| correct | 66 |
| accuracy | 0.44 |
| accuracy_answerable | 0.288 |
| confidently_wrong | 3 |
| confidently_wrong_rate | 0.02 |
| hallucinated_unanswerable | 0 |
| repaired | 4 |
| repair_success | 3 |
| avg_attempts | 1.55 |
| avg_seconds | 29.28 |
| total_tokens | 273453 |

## Per-question detail

### askdata (verification on)

| id | tier | status | correct | attempts | failed checks |
|---|---|---|---|---|---|
| L1 | lookup | trusted | True | 1 | - |
| L2 | lookup | trusted | True | 1 | - |
| L3 | lookup | trusted | True | 1 | - |
| L4 | lookup | trusted | True | 1 | - |
| L5 | lookup | trusted | False | 1 | - |
| L6 | lookup | trusted | True | 1 | - |
| L7 | lookup | trusted | True | 1 | - |
| L8 | lookup | repaired | False | 2 | - |
| L9 | lookup | abstained | False | 2 | judge.sql_answers_question |
| L10 | lookup | abstained | False | 2 | judge.sql_answers_question |
| L11 | lookup | abstained | False | 3 | judge.sql_answers_question |
| L12 | lookup | trusted | True | 1 | - |
| L13 | lookup | abstained | False | 2 | static.select_only, static.identifiers |
| L14 | lookup | abstained | False | 3 | judge.sql_answers_question |
| A1 | aggregation | abstained | False | 2 | judge.sql_answers_question |
| A2 | aggregation | trusted | True | 1 | - |
| A3 | aggregation | trusted | True | 1 | - |
| A4 | aggregation | trusted | True | 1 | - |
| A5 | aggregation | trusted | True | 1 | - |
| A6 | aggregation | abstained | False | 2 | sanity.not_all_null |
| A7 | aggregation | trusted | True | 1 | - |
| A8 | aggregation | abstained | False | 2 | static.identifiers |
| A9 | aggregation | abstained | False | 2 | - |
| A10 | aggregation | abstained | False | 3 | static.select_only |
| A11 | aggregation | trusted | True | 1 | - |
| A12 | aggregation | abstained | False | 3 | - |
| A13 | aggregation | abstained | False | 2 | judge.sql_answers_question |
| A14 | aggregation | trusted | True | 1 | - |
| A15 | aggregation | abstained | False | 2 | judge.sql_answers_question |
| A16 | aggregation | trusted | True | 1 | - |
| A17 | aggregation | trusted | True | 1 | - |
| A18 | aggregation | trusted | True | 1 | - |
| J1 | join | abstained | False | 2 | - |
| J2 | join | abstained | False | 2 | static.identifiers |
| J3 | join | abstained | False | 3 | static.select_only, static.identifiers |
| J4 | join | trusted | True | 1 | - |
| J5 | join | abstained | False | 2 | - |
| J6 | join | abstained | False | 3 | static.select_only, static.identifiers |
| J7 | join | abstained | False | 3 | static.select_only, static.identifiers |
| J8 | join | abstained | False | 3 | static.select_only, static.identifiers |
| J9 | join | trusted | True | 1 | - |
| J10 | join | trusted | True | 1 | - |
| J11 | join | abstained | False | 2 | static.identifiers |
| J12 | join | abstained | False | 2 | - |
| J13 | join | abstained | False | 2 | static.select_only, static.identifiers |
| J14 | join | abstained | False | 2 | static.identifiers |
| J15 | join | abstained | False | 3 | static.select_only, static.identifiers |
| J16 | join | abstained | False | 2 | - |
| J17 | join | abstained | False | 2 | static.identifiers |
| J18 | join | abstained | False | 2 | - |
| J19 | join | abstained | False | 2 | - |
| J20 | join | trusted | True | 1 | - |
| T1 | temporal | trusted | True | 1 | - |
| T2 | temporal | trusted | True | 1 | - |
| T3 | temporal | abstained | False | 1 | - |
| T4 | temporal | abstained | False | 2 | judge.sql_answers_question |
| T5 | temporal | abstained | False | 1 | - |
| T6 | temporal | abstained | False | 2 | static.identifiers |
| T7 | temporal | abstained | False | 2 | static.identifiers |
| T8 | temporal | repaired | True | 3 | - |
| T9 | temporal | abstained | False | 1 | - |
| T10 | temporal | abstained | False | 1 | - |
| T11 | temporal | abstained | False | 2 | - |
| T12 | temporal | abstained | False | 2 | - |
| T13 | temporal | abstained | False | 2 | - |
| T14 | temporal | abstained | False | 2 | static.identifiers |
| T15 | temporal | trusted | False | 1 | - |
| T16 | temporal | abstained | False | 2 | static.select_only, static.identifiers |
| M1 | ambiguous | abstained | False | 1 | - |
| M2 | ambiguous | abstained | False | 2 | static.identifiers |
| M3 | ambiguous | abstained | False | 1 | - |
| M4 | ambiguous | abstained | False | 1 | - |
| M5 | ambiguous | abstained | False | 1 | - |
| M6 | ambiguous | abstained | False | 1 | - |
| M7 | ambiguous | abstained | False | 2 | - |
| M8 | ambiguous | abstained | False | 1 | - |
| M9 | ambiguous | abstained | False | 1 | - |
| M10 | ambiguous | abstained | False | 3 | static.identifiers |
| M11 | ambiguous | abstained | False | 1 | - |
| M12 | ambiguous | abstained | False | 1 | - |
| U1 | unanswerable | abstained | True | 1 | - |
| U2 | unanswerable | abstained | True | 1 | - |
| U3 | unanswerable | abstained | True | 3 | static.select_only, static.identifiers |
| U4 | unanswerable | abstained | True | 1 | - |
| U5 | unanswerable | abstained | True | 1 | - |
| U6 | unanswerable | abstained | True | 1 | - |
| U7 | unanswerable | abstained | True | 1 | - |
| U8 | unanswerable | abstained | True | 3 | judge.sql_answers_question |
| U9 | unanswerable | abstained | True | 1 | - |
| U10 | unanswerable | abstained | True | 1 | - |
| U11 | unanswerable | abstained | True | 2 | static.identifiers |
| U12 | unanswerable | abstained | True | 1 | - |
| U13 | unanswerable | abstained | True | 1 | - |
| U14 | unanswerable | abstained | True | 1 | - |
| U15 | unanswerable | abstained | True | 1 | - |
| U16 | unanswerable | abstained | True | 1 | - |
| U17 | unanswerable | abstained | True | 1 | - |
| U18 | unanswerable | abstained | True | 1 | - |
| U19 | unanswerable | abstained | True | 1 | - |
| U20 | unanswerable | abstained | True | 1 | - |
| L15 | lookup | abstained | False | 2 | - |
| L16 | lookup | trusted | True | 1 | - |
| L17 | lookup | abstained | False | 1 | - |
| L18 | lookup | trusted | True | 1 | - |
| L19 | lookup | abstained | False | 3 | static.identifiers |
| L20 | lookup | trusted | True | 1 | - |
| A19 | aggregation | trusted | True | 1 | - |
| A20 | aggregation | repaired | True | 2 | - |
| A21 | aggregation | abstained | False | 2 | - |
| A22 | aggregation | abstained | False | 2 | - |
| A23 | aggregation | abstained | False | 2 | static.identifiers |
| A24 | aggregation | repaired | True | 2 | - |
| A25 | aggregation | trusted | True | 1 | - |
| A26 | aggregation | trusted | True | 1 | - |
| J21 | join | abstained | False | 2 | - |
| J22 | join | abstained | False | 1 | - |
| J23 | join | abstained | False | 3 | static.select_only, static.identifiers |
| J24 | join | abstained | False | 3 | static.identifiers |
| J25 | join | abstained | False | 2 | - |
| J26 | join | abstained | False | 3 | - |
| J27 | join | abstained | False | 2 | - |
| J28 | join | abstained | False | 2 | - |
| J29 | join | abstained | False | 2 | - |
| J30 | join | abstained | False | 1 | - |
| T17 | temporal | trusted | True | 1 | - |
| T18 | temporal | abstained | False | 2 | static.identifiers |
| T19 | temporal | abstained | False | 2 | judge.sql_answers_question |
| T20 | temporal | trusted | True | 1 | - |
| T21 | temporal | abstained | False | 2 | static.identifiers |
| T22 | temporal | abstained | False | 1 | - |
| T23 | temporal | abstained | False | 1 | - |
| T24 | temporal | abstained | False | 1 | - |
| M13 | ambiguous | abstained | False | 1 | - |
| M14 | ambiguous | abstained | False | 1 | - |
| M15 | ambiguous | abstained | False | 1 | - |
| M16 | ambiguous | abstained | False | 1 | - |
| M17 | ambiguous | abstained | False | 1 | - |
| M18 | ambiguous | abstained | False | 1 | - |
| U21 | unanswerable | abstained | True | 1 | - |
| U22 | unanswerable | abstained | True | 2 | - |
| U23 | unanswerable | abstained | True | 2 | static.select_only, static.identifiers |
| U24 | unanswerable | abstained | True | 1 | - |
| U25 | unanswerable | abstained | True | 1 | - |
| U26 | unanswerable | abstained | True | 1 | - |
| U27 | unanswerable | abstained | True | 1 | - |
| U28 | unanswerable | abstained | True | 1 | - |
| U29 | unanswerable | abstained | True | 1 | - |
| U30 | unanswerable | abstained | True | 1 | - |
| U31 | unanswerable | abstained | True | 2 | static.select_only, static.identifiers |
| U32 | unanswerable | abstained | True | 1 | - |
