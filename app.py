
import streamlit as st
from src.web_app.session import init_session
from src.web_app.ui_chat import render_chat_tab
from src.web_app.ui_portfolio import render_portfolio_tab
from src.web_app.ui_market import render_market_tab
from src.web_app.ui_goals import render_goals_tab

st.set_page_config(
    page_title="AI Finance Assistant",
    page_icon="📈",
    layout="wide",
)

# -------------------------------
# App Header
# -------------------------------
st.markdown(
    """
    <div style="display:flex; align-items:baseline; gap:10px;">
        <span style="font-size:32px; font-weight:700;">
            🤖 Finnie
        </span>
        <span style="
            font-size:18px;
            font-weight:400;
            color:#666;
            letter-spacing:0.5px;
        ">
            Personal Finance Assistant
        </span>
    </div>
    """,
    unsafe_allow_html=True,
)


# Small, subtle disclaimer (non-intrusive)
st.markdown(
    """
    <div style="
        font-size:12px;
        color:#777;
        margin-top:4px;
        margin-bottom:12px;
    ">
        ⚠️ <b>Educational use only.</b>
        Not financial, legal, or tax advice.
        Please consult a licensed professional before making decisions.
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<hr style='margin-top:6px; margin-bottom:10px;'>", unsafe_allow_html=True)


# Initialize session memory
init_session()

# Tabs
tab_chat, tab_portfolio, tab_market, tab_goals = st.tabs(
    ["💬 Ask Finnie", "📊 Portfolio Dashboard", "📈 Market Overview", "🎯 Goal Planner"]
)

with tab_chat:
    render_chat_tab()

with tab_portfolio:
    render_portfolio_tab()

with tab_market:
    render_market_tab()

with tab_goals:
    render_goals_tab()
