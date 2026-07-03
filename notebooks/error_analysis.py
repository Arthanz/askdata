# %% [markdown]
# # Error analysis — failure-mode taxonomy (paper §6)
#
# Run AFTER `python -m eval.run` has produced a report in `eval/reports/`.
# Percent-format notebook: open in VS Code / Jupyter (via jupytext) and run cells.

# %%
import json
from pathlib import Path

import pandas as pd

reports = sorted(Path("../eval/reports").glob("report_*.json"))
assert reports, "No reports found — run `python -m eval.run` first."
data = json.loads(reports[-1].read_text())
print("Loaded:", reports[-1].name, "| configs:", list(data))

# %% [markdown]
# ## Headline comparison

# %%
summary = pd.DataFrame({name: cfg["summary"] for name, cfg in data.items()})
summary

# %% [markdown]
# ## Where the baseline is confidently wrong
# These rows are the raw material for the taxonomy. For each, read the SQL and
# classify: (a) silent wrong-question SQL, (b) invented schema, (c) proxy
# fabrication, (d) unresolved ambiguity, (e) degenerate result.

# %%
baseline = pd.DataFrame(next(cfg["rows"] for name, cfg in data.items() if "baseline" in name))
wrong = baseline[(baseline.status.isin(["trusted", "repaired"])) & (~baseline.correct)]
wrong[["id", "tier", "question", "sql", "answer"]]

# %%
# Manual classification — fill in after reading each row above.
TAXONOMY: dict[str, str] = {
    # "J2": "silent_wrong_question",
    # "U1": "proxy_fabrication",
}
pd.Series(TAXONOMY).value_counts() if TAXONOMY else "classify rows above, then rerun"

# %% [markdown]
# ## What did verification catch?
# Failed-check frequency in the verified config → the ablation table (paper §5).

# %%
verified = pd.DataFrame(next(cfg["rows"] for name, cfg in data.items() if "askdata" in name))
checks = verified.explode("failed_checks").dropna(subset=["failed_checks"])
checks.groupby("failed_checks").size().sort_values(ascending=False)

# %%
# Repairs: questions the baseline got wrong that the verified agent fixed or abstained on.
merged = baseline[["id", "correct", "status"]].merge(
    verified[["id", "correct", "status"]], on="id", suffixes=("_base", "_verified")
)
merged[(~merged.correct_base) & (merged.correct_verified | (merged.status_verified == "abstained"))]
