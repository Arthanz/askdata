# Aggregated eval results

## ollama — `qwen2.5-coder:3b`, judge = `openai:gpt-5.4-mini` (3 runs)

| metric | baseline | verified |
|---|---|---|
| accuracy | — | 0.431 ± 0.008 |
| accuracy (answerable) | — | 0.277 ± 0.010 |
| confidently-wrong rate | — | 0.022 ± 0.004 |
| abstained (n) | — | 114.000 ± 1.000 |
| hallucinated unanswerable (n) | — | 0.000 ± 0.000 |
| repaired (n) | — | 5.333 ± 1.528 |
| avg seconds / question | — | 16.053 ± 11.515 |
| total tokens | — | 278924.667 ± 5770.174 |

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

## openai — `gpt-5.4` (3 runs)

| metric | baseline | verified |
|---|---|---|
| accuracy | 0.784 ± 0.010 | 0.776 ± 0.008 |
| accuracy (answerable) | 0.731 ± 0.010 | 0.714 ± 0.010 |
| confidently-wrong rate | 0.200 ± 0.007 | 0.167 ± 0.017 |
| abstained (n) | 33.667 ± 1.528 | 40.667 ± 2.082 |
| hallucinated unanswerable (n) | 0.667 ± 0.577 | 0.000 ± 0.000 |
| repaired (n) | 2.000 ± 1.000 | 13.333 ± 3.055 |
| avg seconds / question | 3.343 ± 0.127 | 5.347 ± 0.202 |
| total tokens | 145435.333 ± 1153.653 | 293941.333 ± 214.048 |

Paired confidently-wrong outcomes across 3 run(s): baseline-only CW on 21 question-runs, verified-only CW on 6; exact McNemar p = 0.0059.

## openai — `gpt-5.4-mini`, judge = `ollama:qwen2.5-coder:3b` (3 runs)

| metric | baseline | verified |
|---|---|---|
| accuracy | — | 0.722 ± 0.020 |
| accuracy (answerable) | — | 0.650 ± 0.021 |
| confidently-wrong rate | — | 0.094 ± 0.012 |
| abstained (n) | — | 59.333 ± 1.155 |
| hallucinated unanswerable (n) | — | 0.333 ± 0.577 |
| repaired (n) | — | 17.667 ± 1.155 |
| avg seconds / question | — | 5.387 ± 0.117 |
| total tokens | — | 313969.667 ± 3319.337 |

## openai — `gpt-5.4-mini` (3 runs)

| metric | baseline | verified |
|---|---|---|
| accuracy | 0.773 ± 0.000 | 0.727 ± 0.007 |
| accuracy (answerable) | 0.720 ± 0.000 | 0.653 ± 0.009 |
| confidently-wrong rate | 0.218 ± 0.004 | 0.067 ± 0.007 |
| abstained (n) | 32.333 ± 0.577 | 63.000 ± 1.000 |
| hallucinated unanswerable (n) | 1.000 ± 0.000 | 0.000 ± 0.000 |
| repaired (n) | 3.000 ± 2.000 | 15.333 ± 6.110 |
| avg seconds / question | 2.907 ± 0.045 | 4.670 ± 0.170 |
| total tokens | 149129.667 ± 1835.979 | 317952.667 ± 6525.414 |

Paired confidently-wrong outcomes across 3 run(s): baseline-only CW on 75 question-runs, verified-only CW on 7; exact McNemar p = 1.7e-15.

## openai — `gpt-5.4-nano` (3 runs)

| metric | baseline | verified |
|---|---|---|
| accuracy | 0.740 ± 0.013 | 0.676 ± 0.010 |
| accuracy (answerable) | 0.681 ± 0.013 | 0.590 ± 0.013 |
| confidently-wrong rate | 0.247 ± 0.018 | 0.147 ± 0.029 |
| abstained (n) | 32.667 ± 1.528 | 58.333 ± 4.726 |
| hallucinated unanswerable (n) | 1.333 ± 0.577 | 0.333 ± 0.577 |
| repaired (n) | 5.000 ± 2.000 | 16.667 ± 4.726 |
| avg seconds / question | 4.893 ± 3.314 | 4.873 ± 0.189 |
| total tokens | 148092.333 ± 3685.788 | 314757.667 ± 7114.784 |

Paired confidently-wrong outcomes across 3 run(s): baseline-only CW on 60 question-runs, verified-only CW on 15; exact McNemar p = 1.6e-07.
