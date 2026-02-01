# src/workflow/graph.py
from langgraph.graph import StateGraph, END
from src.workflow.state import FinanceState
from src.workflow.router import route_intent


def build_graph(agents: dict):
    g = StateGraph(FinanceState)

    def router_node(state: FinanceState) -> FinanceState:
        query = state.get("user_query") or state.get("query", "")
        intent = route_intent(query)

        state["intent"] = intent
        state["agent_name"] = intent
        return state

    def run_agent_node(state: FinanceState) -> FinanceState:
        agent_name = state.get("agent_name", "finance_qa")
        agent = agents.get(agent_name) or agents.get("finance_qa")

        # run agent
        result = agent.run(state)

        # always set core response
        state["answer"] = getattr(result, "answer", "") if result is not None else ""
        state["sources"] = getattr(result, "sources", []) if result is not None else []

        for key in [
            # market
            "market_df", "market_fetched_at", "market_ticker", "market_is_mock",
            # portfolio
            "portfolio_df", "portfolio_summary",
            # goals
            "goal_df", "goal_summary",
        ]:
            if result is not None and hasattr(result, key):
                state[key] = getattr(result, key)

        return state

    g.add_node("router", router_node)
    g.add_node("run_agent", run_agent_node)

    g.set_entry_point("router")
    g.add_edge("router", "run_agent")
    g.add_edge("run_agent", END)

    return g.compile()
