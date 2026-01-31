# src/web_app/ui_market.py
import streamlit as st
import matplotlib.pyplot as plt


# --- Page config data ---
POPULAR_TICKERS = [
    ("AAPL", "Apple"),
    ("MSFT", "Microsoft"),
    ("NVDA", "NVIDIA"),
    ("AMZN", "Amazon"),
    ("GOOGL", "Alphabet"),
    ("TSLA", "Tesla"),
    ("META", "Meta"),
]

# ETFs as index proxies (simple + works with most market APIs)
MAJOR_INDICES = [
    ("SPY", "S&P 500 (ETF proxy)"),
    ("QQQ", "Nasdaq 100 (ETF proxy)"),
    ("DIA", "Dow 30 (ETF proxy)"),
]


@st.cache_resource
def _get_graph():
    # ✅ Lazy imports to avoid circular import at startup
    from src.agents.registry import build_agents
    from src.workflow.graph import build_graph

    agents = build_agents()
    return build_graph(agents)


def _invoke_market(ticker: str, period: str = "1mo"):
    """
    Calls LangGraph with a market query.
    Your MarketAgent should parse ticker and period if you support it.
    """
    graph = _get_graph()

    # prompt designed to route to market and fetch trend
    q = f"Show me the price trend chart for {ticker} for {period}"
    state_in = {"user_query": q, "query": q, "history": st.session_state.get("chat_history", [])}
    out = graph.invoke(state_in)
    return out


def _safe_metric_value(x, default="—"):
    if x is None:
        return default
    try:
        # if numeric, format
        if isinstance(x, (int, float)):
            return f"{x:,.2f}"
        return str(x)
    except Exception:
        return default


def _plot_price(df, title: str):
    if df is None or len(df) == 0 or "Date" not in df.columns or "Close" not in df.columns:
        st.info("No market data available to plot.")
        return
    fig, ax = plt.subplots()
    ax.plot(df["Date"], df["Close"])
    ax.set_title(title)
    ax.set_xlabel("Date")
    ax.set_ylabel("Close")
    st.pyplot(fig)


def _extract_basic_numbers(out: dict):
    """
    Tries to pull a 'last close' and simple % change from the returned market_df.
    Works even if your agent is mock.
    """
    df = out.get("market_df")
    if df is None or len(df) < 2 or "Close" not in df.columns:
        return None, None

    try:
        last = float(df["Close"].iloc[-1])
        prev = float(df["Close"].iloc[-2])
        pct = ((last - prev) / prev) * 100.0 if prev else None
        return last, pct
    except Exception:
        return None, None


def _ensure_market_cache():
    if "market_cache" not in st.session_state:
        st.session_state["market_cache"] = {}


def _refresh_many(tickers, period="1mo"):
    """
    Fetch many tickers and store in session cache.
    """
    _ensure_market_cache()
    for t, _name in tickers:
        st.session_state["market_cache"][f"{t}:{period}"] = _invoke_market(t, period=period)


def render_market_tab():
    st.subheader("📈 Market Overview")
    st.caption("Real-time market data (if APIs configured). Education only. Prices may be delayed.")

    _ensure_market_cache()

    # Top bar controls
    top_l, top_r = st.columns([1, 1])
    with top_l:
        period = st.selectbox("History period", ["5d", "1mo", "3mo", "6mo", "1y"], index=1, key="market_period")
    with top_r:
        if st.button("🔄 Refresh All", use_container_width=True, key="market_refresh_all"):
            _refresh_many(MAJOR_INDICES + POPULAR_TICKERS, period=period)

    # Auto-load once (first view)
    if st.session_state.get("market_autoloaded") != period:
        _refresh_many(MAJOR_INDICES + POPULAR_TICKERS, period=period)
        st.session_state["market_autoloaded"] = period

    st.divider()

    # -----------------------------
    # Major Indices (metric cards)
    # -----------------------------
    st.markdown("### 🌐 Major Indices")
    cols = st.columns(len(MAJOR_INDICES))
    for i, (ticker, label) in enumerate(MAJOR_INDICES):
        out = st.session_state["market_cache"].get(f"{ticker}:{period}", {}) or {}
        last, pct = _extract_basic_numbers(out)
        delta = f"{pct:+.2f}%" if pct is not None else None

        cols[i].metric(
            label=label,
            value=_safe_metric_value(last),
            delta=delta,
        )

    st.divider()

    # -----------------------------
    # Stock Lookup
    # -----------------------------
    st.markdown("### 🔎 Stock Lookup")
    l1, l2, l3 = st.columns([1.2, 0.8, 0.6])

    with l1:
        lookup_ticker = st.text_input("Enter ticker symbol", value="AAPL", key="lookup_ticker").strip().upper()
    with l2:
        lookup_period = st.selectbox("History Period", ["5d", "1mo", "3mo", "6mo", "1y"], index=1, key="lookup_period")
    with l3:
        lookup_btn = st.button("Look Up", use_container_width=True, key="lookup_btn")

    if lookup_btn and lookup_ticker:
        st.session_state["lookup_out"] = _invoke_market(lookup_ticker, period=lookup_period)

    lookup_out = st.session_state.get("lookup_out")
    if isinstance(lookup_out, dict):
        st.markdown(f"**{lookup_ticker} Snapshot (Education Only)**")
        st.write(lookup_out.get("answer", ""))

        fetched_at = lookup_out.get("market_fetched_at")
        if fetched_at:
            st.caption(f"Last updated: {fetched_at}")

        _plot_price(lookup_out.get("market_df"), f"{lookup_ticker} — {lookup_period} Trend")

    st.divider()

    # -----------------------------
    # Popular Stocks (grid cards)
    # -----------------------------
    st.markdown("### ⭐ Popular Stocks")

    # 7 stocks => show as 4 + 3 columns grid
    rows = [POPULAR_TICKERS[:4], POPULAR_TICKERS[4:]]
    for row in rows:
        cols = st.columns(len(row))
        for i, (ticker, name) in enumerate(row):
            out = st.session_state["market_cache"].get(f"{ticker}:{period}", {}) or {}
            last, pct = _extract_basic_numbers(out)
            delta = f"{pct:+.2f}%" if pct is not None else None

            with cols[i]:
                st.markdown(f"**{ticker}** — {name}")
                st.metric("Last Price", _safe_metric_value(last), delta=delta)

    st.divider()
    st.caption("⚠️ Educational use only. Not financial advice.")
