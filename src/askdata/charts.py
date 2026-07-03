"""Pick a sensible chart for a result dataframe (used by the Streamlit app)."""

from __future__ import annotations

import pandas as pd


def chart_for(df: pd.DataFrame):
    """Return a plotly figure, or None when a table/metric is the better display."""
    import plotly.express as px

    if df is None or df.empty or df.shape == (1, 1):
        return None
    num = df.select_dtypes("number").columns.tolist()
    dt = [c for c in df.columns if pd.api.types.is_datetime64_any_dtype(df[c])]
    cat = [c for c in df.columns if c not in num and c not in dt]

    if dt and num:
        d = df.sort_values(dt[0])
        return px.line(d, x=dt[0], y=num[0], markers=True)
    if cat and num and 2 <= len(df) <= 50:
        d = df.sort_values(num[0], ascending=False)
        return px.bar(d, x=cat[0], y=num[0])
    if len(num) >= 2 and len(df) > 2:
        return px.scatter(df, x=num[0], y=num[1])
    return None
