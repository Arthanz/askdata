"""AskData — Streamlit demo. Run: streamlit run app/app.py"""

import os
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from askdata.agent import AskDataAgent  # noqa: E402
from askdata.charts import chart_for  # noqa: E402
from askdata.config import Settings  # noqa: E402

st.set_page_config(page_title="AskData", page_icon="📊", layout="wide")

STATUS_BADGE = {
    "trusted": ("✅ Trusted", "Passed all verification checks on the first attempt."),
    "repaired": ("🔧 Repaired", "The first attempt failed verification; a corrected query passed."),
    "abstained": ("🛑 Abstained", "AskData could not produce an answer it trusts — by design."),
    "error": ("⚠️ Error", "Infrastructure problem (provider/database)."),
}

EXAMPLES = [
    "What are the top 5 product categories by total sales value?",
    "How is the business trending?",
    "What is the average delivery time in days?",
    "What is the profit margin per product category?",  # unanswerable on purpose
]


@st.cache_resource
def get_agent():
    return AskDataAgent(settings=Settings())


st.title("📊 AskData")
st.caption(
    "A chat-with-your-data agent that **knows when it's wrong** — every answer is "
    "verified before you see it, and the agent abstains rather than guess."
)

settings = Settings()
if not settings.db_path.exists():
    # first run on a fresh deploy: build the synthetic sample automatically
    from askdata.load_data import build

    with st.spinner("First run — building the sample database…"):
        build(settings.db_path)
try:
    settings.resolved_provider()
except RuntimeError as e:
    st.error(str(e))
    st.stop()

with st.sidebar:
    st.subheader("How to read the badges")
    for status, (badge, why) in STATUS_BADGE.items():
        st.markdown(f"**{badge}** — {why}")
    st.divider()
    st.subheader("Try one of these")
    for ex in EXAMPLES:
        if st.button(ex, use_container_width=True):
            st.session_state["pending"] = ex
    st.divider()
    st.caption(f"Provider: `{settings.resolved_provider()}` · DB: `{settings.db_path.name}`")

if "history" not in st.session_state:
    st.session_state.history = []

for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

question = st.chat_input("Ask a question about the e-commerce data…")
if not question and "pending" in st.session_state:
    question = st.session_state.pop("pending")

if question:
    st.session_state.history.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Planning → SQL → executing → verifying…"):
            ans = get_agent().ask(question)

        badge, _ = STATUS_BADGE[ans.status]
        st.markdown(f"**{badge}**" + (f" · {ans.attempts} attempt(s)" if ans.attempts > 1 else ""))
        st.markdown(ans.text)

        if ans.df is not None and ans.status in ("trusted", "repaired"):
            fig = chart_for(ans.df)
            if fig is not None:
                st.plotly_chart(fig, use_container_width=True)
            if ans.df.shape != (1, 1):
                st.dataframe(ans.df, use_container_width=True, hide_index=True)

        with st.expander("Details: SQL + verification checks"):
            if ans.sql:
                st.code(ans.sql, language="sql")
            for c in ans.checks:
                icon = "✅" if c.passed else "❌"
                st.markdown(f"{icon} `{c.name}` {c.detail}")
            st.caption(
                f"{ans.seconds:.1f}s · {ans.input_tokens + ans.output_tokens:,} tokens "
                f"· {ans.attempts} attempt(s)"
            )

    st.session_state.history.append(
        {"role": "assistant", "content": f"**{badge}**\n\n{ans.text}"}
    )
