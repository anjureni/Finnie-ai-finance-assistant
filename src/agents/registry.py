# src/agents/registry.py

from src.agents.finance_qa import FinanceQAAgent
from src.agents.market import MarketAgent
from src.agents.portfolio import PortfolioAgent
from src.agents.goals import GoalsAgent


def build_agents():
    """
    Central agent registry.

    IMPORTANT:
    - Agents must NOT import this file (no: from src.agents.registry import build_agents)
    - Only UI / graph code should call build_agents()
    """
    return {
        "finance_qa": FinanceQAAgent(),
        "market": MarketAgent(),
        "portfolio": PortfolioAgent(),
        "goals": GoalsAgent(),
    }
