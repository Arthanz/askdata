provider: `openai` · model: `gpt-5.4-mini` · tag: `gpt54mini-judgeqwen-run3`

# AskData evaluation report — 2026-07-04 17:08

| metric | askdata (verification on) |
|---|---|
| n | 150 |
| answered | 90 |
| abstained | 60 |
| correct | 109 |
| accuracy | 0.727 |
| accuracy_answerable | 0.653 |
| confidently_wrong | 13 |
| confidently_wrong_rate | 0.087 |
| hallucinated_unanswerable | 0 |
| repaired | 17 |
| repair_success | 11 |
| avg_attempts | 1.5 |
| avg_seconds | 5.34 |
| total_tokens | 314587 |

## Per-question detail

### askdata (verification on)

| id | tier | status | correct | attempts | failed checks |
|---|---|---|---|---|---|
| L1 | lookup | trusted | True | 1 | - |
| L2 | lookup | trusted | True | 1 | - |
| L3 | lookup | trusted | True | 1 | - |
| L4 | lookup | trusted | True | 1 | - |
| L5 | lookup | repaired | False | 2 | - |
| L6 | lookup | trusted | True | 1 | - |
| L7 | lookup | trusted | True | 1 | - |
| L8 | lookup | trusted | False | 1 | - |
| L9 | lookup | repaired | True | 2 | - |
| L10 | lookup | trusted | True | 1 | - |
| L11 | lookup | trusted | True | 1 | - |
| L12 | lookup | trusted | True | 1 | - |
| L13 | lookup | trusted | True | 1 | - |
| L14 | lookup | trusted | True | 1 | - |
| A1 | aggregation | trusted | True | 1 | - |
| A2 | aggregation | trusted | True | 1 | - |
| A3 | aggregation | trusted | True | 1 | - |
| A4 | aggregation | trusted | True | 1 | - |
| A5 | aggregation | trusted | True | 1 | - |
| A6 | aggregation | trusted | True | 1 | - |
| A7 | aggregation | trusted | True | 1 | - |
| A8 | aggregation | abstained | False | 3 | static.select_only |
| A9 | aggregation | trusted | True | 1 | - |
| A10 | aggregation | trusted | True | 1 | - |
| A11 | aggregation | repaired | True | 2 | - |
| A12 | aggregation | repaired | False | 2 | - |
| A13 | aggregation | trusted | True | 1 | - |
| A14 | aggregation | trusted | True | 1 | - |
| A15 | aggregation | trusted | True | 1 | - |
| A16 | aggregation | repaired | True | 2 | - |
| A17 | aggregation | trusted | True | 1 | - |
| A18 | aggregation | trusted | True | 1 | - |
| J1 | join | trusted | True | 1 | - |
| J2 | join | abstained | False | 3 | static.select_only, static.identifiers |
| J3 | join | trusted | True | 1 | - |
| J4 | join | trusted | True | 1 | - |
| J5 | join | repaired | False | 3 | - |
| J6 | join | trusted | True | 1 | - |
| J7 | join | abstained | False | 3 | static.select_only |
| J8 | join | trusted | True | 1 | - |
| J9 | join | trusted | True | 1 | - |
| J10 | join | trusted | True | 1 | - |
| J11 | join | trusted | True | 1 | - |
| J12 | join | trusted | True | 1 | - |
| J13 | join | trusted | True | 1 | - |
| J14 | join | trusted | True | 1 | - |
| J15 | join | repaired | True | 2 | - |
| J16 | join | trusted | True | 1 | - |
| J17 | join | trusted | True | 1 | - |
| J18 | join | abstained | False | 3 | static.select_only, static.identifiers |
| J19 | join | trusted | True | 1 | - |
| J20 | join | trusted | True | 1 | - |
| T1 | temporal | repaired | True | 2 | - |
| T2 | temporal | trusted | True | 1 | - |
| T3 | temporal | trusted | False | 1 | - |
| T4 | temporal | trusted | True | 1 | - |
| T5 | temporal | repaired | True | 2 | - |
| T6 | temporal | abstained | False | 3 | static.select_only |
| T7 | temporal | trusted | True | 1 | - |
| T8 | temporal | trusted | True | 1 | - |
| T9 | temporal | trusted | False | 1 | - |
| T10 | temporal | abstained | False | 3 | static.select_only |
| T11 | temporal | trusted | False | 1 | - |
| T12 | temporal | trusted | True | 1 | - |
| T13 | temporal | repaired | True | 3 | - |
| T14 | temporal | trusted | True | 1 | - |
| T15 | temporal | trusted | True | 1 | - |
| T16 | temporal | trusted | True | 1 | - |
| M1 | ambiguous | abstained | False | 3 | static.select_only |
| M2 | ambiguous | abstained | False | 3 | static.select_only |
| M3 | ambiguous | abstained | False | 3 | static.select_only |
| M4 | ambiguous | abstained | False | 3 | static.select_only, static.identifiers |
| M5 | ambiguous | abstained | False | 3 | static.select_only |
| M6 | ambiguous | abstained | False | 3 | static.select_only |
| M7 | ambiguous | abstained | False | 3 | static.select_only, static.identifiers |
| M8 | ambiguous | trusted | False | 1 | - |
| M9 | ambiguous | abstained | False | 3 | static.select_only, static.identifiers |
| M10 | ambiguous | abstained | False | 3 | static.select_only |
| M11 | ambiguous | abstained | False | 1 | - |
| M12 | ambiguous | abstained | False | 3 | static.select_only, static.identifiers |
| U1 | unanswerable | abstained | True | 1 | - |
| U2 | unanswerable | abstained | True | 1 | - |
| U3 | unanswerable | abstained | True | 1 | - |
| U4 | unanswerable | abstained | True | 1 | - |
| U5 | unanswerable | abstained | True | 1 | - |
| U6 | unanswerable | abstained | True | 1 | - |
| U7 | unanswerable | abstained | True | 1 | - |
| U8 | unanswerable | abstained | True | 1 | - |
| U9 | unanswerable | abstained | True | 1 | - |
| U10 | unanswerable | abstained | True | 1 | - |
| U11 | unanswerable | abstained | True | 1 | - |
| U12 | unanswerable | abstained | True | 1 | - |
| U13 | unanswerable | abstained | True | 1 | - |
| U14 | unanswerable | abstained | True | 1 | - |
| U15 | unanswerable | abstained | True | 1 | - |
| U16 | unanswerable | abstained | True | 1 | - |
| U17 | unanswerable | abstained | True | 1 | - |
| U18 | unanswerable | abstained | True | 1 | - |
| U19 | unanswerable | abstained | True | 1 | - |
| U20 | unanswerable | abstained | True | 1 | - |
| L15 | lookup | trusted | True | 1 | - |
| L16 | lookup | repaired | True | 3 | - |
| L17 | lookup | trusted | True | 1 | - |
| L18 | lookup | trusted | True | 1 | - |
| L19 | lookup | trusted | True | 1 | - |
| L20 | lookup | trusted | True | 1 | - |
| A19 | aggregation | trusted | True | 1 | - |
| A20 | aggregation | trusted | True | 1 | - |
| A21 | aggregation | abstained | False | 3 | static.select_only |
| A22 | aggregation | repaired | True | 2 | - |
| A23 | aggregation | trusted | True | 1 | - |
| A24 | aggregation | trusted | True | 1 | - |
| A25 | aggregation | trusted | True | 1 | - |
| A26 | aggregation | trusted | True | 1 | - |
| J21 | join | trusted | True | 1 | - |
| J22 | join | trusted | False | 1 | - |
| J23 | join | trusted | True | 1 | - |
| J24 | join | repaired | True | 2 | - |
| J25 | join | abstained | False | 3 | static.select_only |
| J26 | join | trusted | True | 1 | - |
| J27 | join | abstained | False | 3 | static.select_only |
| J28 | join | repaired | True | 3 | - |
| J29 | join | trusted | True | 1 | - |
| J30 | join | repaired | False | 2 | - |
| T17 | temporal | trusted | True | 1 | - |
| T18 | temporal | trusted | False | 1 | - |
| T19 | temporal | trusted | True | 1 | - |
| T20 | temporal | abstained | False | 3 | judge.sql_answers_question |
| T21 | temporal | repaired | False | 2 | - |
| T22 | temporal | trusted | True | 1 | - |
| T23 | temporal | repaired | False | 2 | - |
| T24 | temporal | abstained | False | 3 | static.select_only |
| M13 | ambiguous | abstained | False | 3 | static.select_only |
| M14 | ambiguous | abstained | False | 3 | static.select_only |
| M15 | ambiguous | abstained | False | 3 | static.select_only |
| M16 | ambiguous | abstained | False | 3 | static.select_only, static.identifiers |
| M17 | ambiguous | abstained | False | 3 | static.select_only |
| M18 | ambiguous | abstained | False | 3 | static.select_only, static.identifiers |
| U21 | unanswerable | abstained | True | 1 | - |
| U22 | unanswerable | abstained | True | 1 | - |
| U23 | unanswerable | abstained | True | 1 | - |
| U24 | unanswerable | abstained | True | 1 | - |
| U25 | unanswerable | abstained | True | 1 | - |
| U26 | unanswerable | abstained | True | 1 | - |
| U27 | unanswerable | abstained | True | 1 | - |
| U28 | unanswerable | abstained | True | 1 | - |
| U29 | unanswerable | abstained | True | 1 | - |
| U30 | unanswerable | abstained | True | 1 | - |
| U31 | unanswerable | abstained | True | 1 | - |
| U32 | unanswerable | abstained | True | 1 | - |
