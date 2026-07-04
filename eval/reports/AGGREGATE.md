# Aggregated eval results

## ollama — `qwen2.5-coder:3b` (3 runs)

| metric | baseline | verified |
|---|---|---|
| accuracy | 0.471 ± 0.017 | 0.431 ± 0.014 |
| accuracy (answerable) | 0.336 ± 0.021 | 0.282 ± 0.020 |
| confidently-wrong rate | 0.151 ± 0.010 | 0.109 ± 0.028 |
| abstained (n) | 87.667 ± 1.155 | 100.333 ± 3.055 |
| hallucinated unanswerable (n) | 1.000 ± 0.000 | 0.667 ± 0.577 |
| repaired (n) | 5.333 ± 1.528 | 6.000 ± 1.000 |
| avg seconds / question | 7.007 ± 0.090 | 8.873 ± 1.036 |
| total tokens | 192226.667 ± 4967.566 | 252184.333 ± 2566.016 |

Paired confidently-wrong outcomes across 3 run(s): baseline-only CW on 53 question-runs, verified-only CW on 34; exact McNemar p = 0.053.

## openai — `gpt-4o-mini` (3 runs)

| metric | baseline | verified |
|---|---|---|
| accuracy | 0.687 ± 0.007 | 0.684 ± 0.015 |
| accuracy (answerable) | 0.605 ± 0.005 | 0.599 ± 0.020 |
| confidently-wrong rate | 0.211 ± 0.014 | 0.162 ± 0.010 |
| abstained (n) | 47.000 ± 2.000 | 55.000 ± 3.606 |
| hallucinated unanswerable (n) | 0.333 ± 0.577 | 0.000 ± 0.000 |
| repaired (n) | 6.000 ± 2.646 | 6.333 ± 3.512 |
| avg seconds / question | 2.260 ± 0.159 | 3.357 ± 0.214 |
| total tokens | 139426.333 ± 784.578 | 244593.000 ± 3884.868 |

Paired confidently-wrong outcomes across 3 run(s): baseline-only CW on 28 question-runs, verified-only CW on 6; exact McNemar p = 0.0002.
