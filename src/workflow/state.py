# src/workflow/state.py
from typing import TypedDict, List, Dict, Any

class FinanceState(TypedDict, total=False):
    # core
    user_query: str               # <-- NEW: clean user question for routing
    context: str                  # <-- NEW: retrieved KB context for finance_qa
    query: str                    # kept for backward compatibility
    history: List[Dict[str, Any]]

    # orchestration
    intent: str
    agent_name: str

    # response
    answer: str
    sources: List[str]

    # market
    market_request: Dict[str, Any]
    market_df: Any
    market_fetched_at: Any
    market_is_mock: bool

    # portfolio
    portfolio_request: Dict[str, Any]
    portfolio_df: Any
    portfolio_summary: Dict[str, Any]

    # goals
    goal_request: Dict[str, Any]
    goal_df: Any
    goal_summary: Dict[str, Any]
