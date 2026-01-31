# src/web_app/ui_portfolio.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


def _init_holdings_state():
    if "user_holdings" not in st.session_state:
        # default demo holding so page isn't empty
        st.session_state["user_holdings"] = [
            {"Ticker": "MSFT", "Shares": 5.0, "Type": "stock", "Price": 400.0},
            {"Ticker": "AAPL", "Shares": 4.0, "Type": "stock", "Price": 190.0},
            {"Ticker": "SPY", "Shares": 3.0, "Type": "etf", "Price": 480.0},
            {"Ticker": "BND", "Shares": 6.0, "Type": "bond", "Price": 75.0},
        ]


def _compute_portfolio(df: pd.DataFrame):
    """
    Computes Value, AllocationPct, summary metrics, and diversification score.
    Works with manual prices.
    """
    if df is None or df.empty:
        return df, {
            "total_value": 0.0,
            "top_asset": "N/A",
            "top_pct": 0.0,
            "diversification_score": 0.0,
        }

    # Clean + compute
    df = df.copy()
    df["Ticker"] = df["Ticker"].astype(str).str.upper().str.strip()
    df["Shares"] = pd.to_numeric(df["Shares"], errors="coerce").fillna(0.0)
    df["Price"] = pd.to_numeric(df["Price"], errors="coerce").fillna(0.0)
    df["Value"] = df["Shares"] * df["Price"]

    total = float(df["Value"].sum())
    if total > 0:
        df["AllocationPct"] = (df["Value"] / total * 100.0).round(2)
    else:
        df["AllocationPct"] = 0.0

    # Largest holding
    df_sorted = df.sort_values("Value", ascending=False)
    top_asset = "N/A"
    top_pct = 0.0
    if len(df_sorted) > 0:
        top_asset = str(df_sorted.iloc[0]["Ticker"])
        top_pct = float(df_sorted.iloc[0]["AllocationPct"])

    # Diversification score (simple HHI-based)
    score = 0.0
    if total > 0:
        w = (df["Value"] / total).values
        hhi = float((w ** 2).sum())
        score = max(0.0, min(100.0, (1.0 - hhi) * 100.0))

    summary = {
        "total_value": total,
        "top_asset": top_asset,
        "top_pct": top_pct,
        "diversification_score": round(score, 1),
    }
    return df, summary


def _small_pie(df: pd.DataFrame):
    if df is None or df.empty:
        st.info("Add holdings to see allocation.")
        return
    if "Ticker" not in df.columns or "Value" not in df.columns:
        st.info("Holdings missing required columns.")
        return

    alloc_df = df[df["Value"] > 0].copy()
    if alloc_df.empty:
        st.info("Add prices/shares to see allocation.")
        return

    fig, ax = plt.subplots(figsize=(4, 4))
    ax.pie(
        alloc_df["Value"],
        labels=alloc_df["Ticker"],
        autopct="%1.1f%%",
        textprops={"fontsize": 8},
    )
    ax.set_title("Asset Allocation", fontsize=12)
    st.pyplot(fig)


def render_portfolio_tab():
    st.subheader("📊 Portfolio Dashboard")
    st.caption("Add your holdings to view allocation, summary, and diversification (education only).")

    _init_holdings_state()

    # -----------------------------
    # 1) Enter Your Holdings section
    # -----------------------------
    st.markdown("### ✍️ Enter Your Holdings")

    with st.expander("➕ Add a Holding", expanded=True):
        c1, c2, c3, c4 = st.columns([1.2, 1.0, 1.0, 1.0])

        with c1:
            ticker = st.text_input("Ticker Symbol", value="VTI", key="p_ticker").strip().upper()
        with c2:
            shares = st.number_input("Shares", min_value=0.0, value=5.0, step=1.0, key="p_shares")
        with c3:
            htype = st.selectbox("Type", ["stock", "etf", "bond", "crypto", "cash"], index=1, key="p_type")
        with c4:
            price = st.number_input("Price (manual)", min_value=0.0, value=100.0, step=1.0, key="p_price")

        add = st.button("Add Holding", use_container_width=True, key="p_add_btn")

        if add:
            if not ticker:
                st.warning("Please enter a ticker.")
            else:
                st.session_state["user_holdings"].append(
                    {"Ticker": ticker, "Shares": float(shares), "Type": htype, "Price": float(price)}
                )
                st.success(f"Added {ticker} ✅")
                st.rerun()

    # -----------------------------
    # 2) Holdings table + remove
    # -----------------------------
    holdings_df = pd.DataFrame(st.session_state["user_holdings"])

    st.markdown("### 📋 Holdings Details")
    if holdings_df.empty:
        st.info("No holdings yet. Add one above.")
        return

    # Compute values and metrics
    calc_df, summary = _compute_portfolio(holdings_df)

    # Editable grid (user can edit shares/price directly)
    st.caption("Tip: You can edit Shares/Price directly below.")
    edited_df = st.data_editor(
        calc_df[["Ticker", "Type", "Shares", "Price", "Value", "AllocationPct"]],
        use_container_width=True,
        hide_index=True,
        disabled=["Value", "AllocationPct"],
        key="portfolio_editor",
    )

    # Save edits back to session (Shares/Price/Type)
    # Note: data_editor returns a DataFrame
    if isinstance(edited_df, pd.DataFrame):
        saved = []
        for _, r in edited_df.iterrows():
            saved.append(
                {
                    "Ticker": str(r["Ticker"]).upper().strip(),
                    "Shares": float(r["Shares"]),
                    "Type": str(r["Type"]),
                    "Price": float(r["Price"]),
                }
            )
        st.session_state["user_holdings"] = saved

        # recompute after edits
        calc_df, summary = _compute_portfolio(pd.DataFrame(st.session_state["user_holdings"]))

    # Remove holding
    rem_col1, rem_col2 = st.columns([1.2, 0.8])
    with rem_col1:
        remove_ticker = st.selectbox(
            "Remove holding",
            options=[r["Ticker"] for r in st.session_state["user_holdings"]],
            key="remove_ticker",
        )
    with rem_col2:
        if st.button("Remove", use_container_width=True):
            st.session_state["user_holdings"] = [
                h for h in st.session_state["user_holdings"] if h["Ticker"] != remove_ticker
            ]
            st.rerun()

    st.divider()

    # -----------------------------
    # 3) Summary cards
    # -----------------------------
    cards = st.columns(4)
    cards[0].metric("Total Value", f"${summary.get('total_value', 0.0):,.2f}")
    cards[1].metric("Largest Holding", summary.get("top_asset", "N/A"))
    cards[2].metric("Top Holding %", f"{summary.get('top_pct', 0.0):.1f}%")
    cards[3].metric("Diversification Score", f"{summary.get('diversification_score', 0.0)} / 100")

    st.divider()

    # -----------------------------
    # 4) Allocation pie chart (small)
    # -----------------------------
    st.markdown("### 🥧 Asset Allocation")
    _small_pie(calc_df)

    st.divider()
    st.caption("⚠️ Educational use only. Not financial advice.")
