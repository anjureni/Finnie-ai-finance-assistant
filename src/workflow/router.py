# src/workflow/router.py
import re


def _has_ticker_like_token(text: str) -> bool:
    """
    Matches realistic stock tickers:
    - 2–5 uppercase letters
    - excludes common English words (USE, THIS, THAT, etc.)
    - does NOT auto-uppercase the sentence
    """
    if not text:
        return False

    COMMON_WORDS = {
        "THE", "AND", "FOR", "WHY", "WHAT", "WHEN", "WHERE",
        "HOW", "USE", "WITH", "THIS", "THAT", "FROM", "IN",
        "ON", "TO", "OF", "IS", "ARE"
    }

    # Only match tokens that are already uppercase in user input
    tokens = re.findall(r"\b[A-Z]{2,5}\b", text)
    tokens = [t for t in tokens if t not in COMMON_WORDS]

    return len(tokens) > 0


def route_intent(query: str) -> str:
    """
    Routes user query to the correct agent:
    - market
    - portfolio
    - goals
    - finance_qa (default / KB-based education)
    """
    q = (query or "").strip()
    q_lower = q.lower()

    # -------------------------------------------------
    # 1) MARKET: requires BOTH market language AND a real ticker
    # -------------------------------------------------
    market_triggers = ["price", "quote", "trend", "chart", "market", "stock"]
    if any(t in q_lower for t in market_triggers) and _has_ticker_like_token(q):
        return "market"

    # -------------------------------------------------
    # 2) PORTFOLIO: only when clearly about user's portfolio
    # -------------------------------------------------
    portfolio_strong = [
        "my portfolio", "my holdings", "my allocation",
        "rebalance", "largest holding", "asset class",
        "portfolio", "holdings", "allocation", "positions"
    ]
    if any(t in q_lower for t in portfolio_strong):
        return "portfolio"

    # Portfolio + ticker (e.g., "AAPL allocation")
    portfolio_hint_words = ["holdings", "allocation", "rebalance", "portfolio"]
    if _has_ticker_like_token(q) and any(w in q_lower for w in portfolio_hint_words):
        return "portfolio"

    # Diversification is ambiguous → portfolio ONLY if user context exists
    if "diversif" in q_lower and any(
        t in q_lower for t in ["my ", "portfolio", "holdings", "allocation"]
    ):
        return "portfolio"

    # -------------------------------------------------
    # 3) GOALS
    # -------------------------------------------------
    goal_triggers = ["goal", "target", "retirement", "projection", "plan"]
    saving_triggers = ["save", "saving", "contribution", "monthly contribution"]
    if any(t in q_lower for t in goal_triggers) or any(t in q_lower for t in saving_triggers):
        return "goals"

    # -------------------------------------------------
    # 4) DEFAULT → Finance education (RAG / KB)
    # -------------------------------------------------
    return "finance_qa"
