# src/web_app/ui_chat.py
import streamlit as st
import matplotlib.pyplot as plt

from src.web_app.session import add_chat_message

@st.cache_resource
def _get_graph():
    from src.agents.registry import build_agents
    from src.workflow.graph import build_graph
    agents = build_agents()
    return build_graph(agents)



def _render_payload(agent: str, payload: dict):
    if agent == "market":
        df = payload.get("market_df")
        fetched_at = payload.get("market_fetched_at")
        ticker = payload.get("market_ticker") or "Market"
        is_mock = payload.get("market_is_mock", False)

        if ticker:
            st.markdown(f"**📈 Market Snapshot: {ticker}**")
        if fetched_at:
            st.caption(f"Data updated: {fetched_at}")
        if is_mock:
            st.warning("Using fallback/mock data (API issue).")

        if df is not None and len(df) > 0:
            fig, ax = plt.subplots()
            ax.plot(df["Date"], df["Close"])
            ax.set_title(f"{ticker} Trend")
            ax.set_xlabel("Date")
            ax.set_ylabel("Price")
            st.pyplot(fig)
        else:
            st.info("No market data available to plot.")

    elif agent == "portfolio":
        df = payload.get("portfolio_df")
        summary = payload.get("portfolio_summary") or {}

        st.markdown("**📊 Portfolio Snapshot**")
        st.write(f"Total Value: **${summary.get('total_value', 0.0):,.2f}**")
        st.write(f"Largest Holding: **{summary.get('top_asset','N/A')}** ({summary.get('top_pct',0.0):.1f}%)")
        st.write(f"Diversification Score: **{summary.get('diversification_score', 0)}**")

        if df is not None and len(df) > 0:
            fig1, ax1 = plt.subplots()
            ax1.pie(df["Value"], labels=df["Asset"], autopct="%1.1f%%")
            ax1.set_title("Allocation (%)")
            st.pyplot(fig1)

            fig2, ax2 = plt.subplots()
            ax2.bar(df["Asset"], df["AllocationPct"])
            ax2.set_title("Allocation % by Asset")
            ax2.set_xlabel("Asset")
            ax2.set_ylabel("Allocation (%)")
            st.pyplot(fig2)

    elif agent == "goals":
        df = payload.get("goal_df")
        summary = payload.get("goal_summary") or {}
        target = float(summary.get("target_amount", 0.0))

        st.markdown("**🎯 Goal Projection Snapshot**")
        st.write(f"Target: **${target:,.2f}**")
        st.write(f"Months: **{summary.get('months', 0)}**")
        st.write(f"Monthly Contribution: **${summary.get('monthly_contribution', 0.0):,.2f}**")
        st.write(f"Expected Return: **{summary.get('annual_return_pct', 0.0):.2f}%**")

        if df is not None and len(df) > 0:
            fig, ax = plt.subplots()
            ax.plot(df["Month"], df["Balance"])
            ax.axhline(y=target, linestyle="--")
            ax.set_title("Goal Projection")
            ax.set_xlabel("Month")
            ax.set_ylabel("Balance")
            st.pyplot(fig)


def _sanitize_history(history):
    fixed = []
    for m in (history or []):
        if isinstance(m, dict):
            fixed.append({**m, "role": m.get("role", "user"), "content": m.get("content", "")})
        else:
            fixed.append({"role": "user", "content": str(m)})
    return fixed


def render_chat_tab():
    st.subheader("💬 Ask Finnie")
    st.caption("Auto agent routing via LangGraph. Chat renders mini dashboards based on the selected agent.")

    # Render chat history
    for msg in st.session_state.chat_history:
        if not isinstance(msg, dict):
            continue
        with st.chat_message(msg.get("role", "assistant")):
            st.markdown(msg.get("content", ""))

            if msg.get("agent"):
                st.caption(f"🤖 Agent used: **{msg['agent']}**")

            payload = msg.get("payload") or {}
            if msg.get("role") == "assistant" and msg.get("agent") and payload:
                _render_payload(msg["agent"], payload)

            if msg.get("sources"):
                st.markdown("**Sources:**")
                for s in msg["sources"]:
                    st.write(s)

    # Input
    user_text = st.chat_input("Ask a finance question...")
    if not user_text:
        return

    add_chat_message("user", user_text)

    safe_history = _sanitize_history(st.session_state.chat_history)

    graph = _get_graph()
    state_in = {
        "user_query": user_text,  # router uses this
        "query": user_text,       # backward compatibility
        "history": safe_history,
    }

    state_out = graph.invoke(state_in)

    agent_used = state_out.get("agent_name", "unknown")
    answer = state_out.get("answer", "Sorry, I couldn't generate an answer.")
    sources = state_out.get("sources", []) or []

    payload = {}
    if agent_used == "market":
        payload = {
            "market_df": state_out.get("market_df"),
            "market_fetched_at": state_out.get("market_fetched_at"),
            "market_ticker": state_out.get("market_ticker"),
            "market_is_mock": state_out.get("market_is_mock", False),
        }
    elif agent_used == "portfolio":
        payload = {
            "portfolio_df": state_out.get("portfolio_df"),
            "portfolio_summary": state_out.get("portfolio_summary"),
        }
    elif agent_used == "goals":
        payload = {
            "goal_df": state_out.get("goal_df"),
            "goal_summary": state_out.get("goal_summary"),
        }

    add_chat_message(
        "assistant",
        answer,
        sources=sources,
        agent=agent_used,
        payload=payload,
    )

    st.rerun()
