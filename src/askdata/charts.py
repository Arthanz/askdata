"""Pick a sensible chart for a result dataframe (used by the Streamlit app)."""

from __future__ import annotations

import re

import pandas as pd

# Olist money columns are Brazilian reais. Name-based heuristic: money-ish
# words, minus count/ratio/score-ish names that also contain them.
MONEY_RE = re.compile(r"price|payment|revenue|freight|sales|spent|amount|total|gmv", re.IGNORECASE)
NOT_MONEY_RE = re.compile(
    r"n_|_n$|count|orders|items|reviews|days|score|installment|rate|pct|ratio|qty|photos",
    re.IGNORECASE,
)


def money_columns(df: pd.DataFrame) -> list[str]:
    return [
        c for c in df.select_dtypes("number").columns
        if MONEY_RE.search(c) and not NOT_MONEY_RE.search(c)
    ]


def chart_for(df: pd.DataFrame):
    """Return a plotly figure, or None when a table/metric is the better display."""
    import plotly.express as px

    if df is None or df.empty or df.shape == (1, 1):
        return None
    num = df.select_dtypes("number").columns.tolist()
    dt = [c for c in df.columns if pd.api.types.is_datetime64_any_dtype(df[c])]
    cat = [c for c in df.columns if c not in num and c not in dt]

    money = set(money_columns(df))

    def _fmt(fig, ycol):
        if ycol in money:
            fig.update_yaxes(tickprefix="R$ ", tickformat=",.2f")
        return fig

    if dt and num:
        d = df.sort_values(dt[0])
        return _fmt(px.line(d, x=dt[0], y=num[0], markers=True), num[0])
    if cat and num and 2 <= len(df) <= 50:
        d = df.sort_values(num[0], ascending=False)
        return _fmt(px.bar(d, x=cat[0], y=num[0]), num[0])
    if len(num) >= 2 and len(df) > 2:
        return px.scatter(df, x=num[0], y=num[1])
    return None
