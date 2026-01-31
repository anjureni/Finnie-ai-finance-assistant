# src/agents/goals.py
from typing import Dict, Any
import pandas as pd

from src.agents.base import BaseAgent, AgentResult
from src.core.disclaimers import DISCLAIMER

class GoalsAgent(BaseAgent):
    name = "goals"

    def run(self, state: Dict[str, Any]) -> AgentResult:
        """
        Inputs:
          - state["goal_request"] = {
              "target_amount": float,
              "months": int,
              "monthly_contribution": float,
              "annual_return_pct": float
            }
        Outputs:
          - state["goal_df"] : DataFrame with Month, Balance
          - state["goal_summary"] : dict with reach_month, etc.
        """
        req = state.get("goal_request") or {}

        target_amount = float(req.get("target_amount", 10000.0))
        months = int(req.get("months", 12))
        monthly_contribution = float(req.get("monthly_contribution", 500.0))
        annual_return_pct = float(req.get("annual_return_pct", 5.0))

        months = max(1, months)
        target_amount = max(0.0, target_amount)
        monthly_contribution = max(0.0, monthly_contribution)
        annual_return_pct = max(0.0, annual_return_pct)

        df = _project_goal(
            target_amount=target_amount,
            months=months,
            monthly_contribution=monthly_contribution,
            annual_return_pct=annual_return_pct,
        )

        reach_month = _reach_month(df, target_amount)
        goal_summary = {
            "target_amount": target_amount,
            "months": months,
            "monthly_contribution": monthly_contribution,
            "annual_return_pct": annual_return_pct,
            "reach_month": reach_month,
        }

        state["goal_df"] = df
        state["goal_summary"] = goal_summary

        if reach_month is not None:
            status = f"✅ Estimated target reached around **Month {reach_month}** (projection)."
        else:
            status = "⚠️ Projection does not reach the target within the selected time horizon."

        answer = (
            f"**Goal Projection (Education Only)**\n\n"
            f"- Target: **${target_amount:,.2f}**\n"
            f"- Time horizon: **{months} months**\n"
            f"- Monthly contribution: **${monthly_contribution:,.2f}**\n"
            f"- Expected annual return: **{annual_return_pct:.2f}%**\n\n"
            f"{status}\n\n"
            "Tip: Increasing monthly contributions or extending the time horizon can help. "
            "Returns are not guaranteed.\n\n"
            f"{DISCLAIMER}"
        )

        return AgentResult(answer=answer, sources=[])

def _project_goal(target_amount: float, months: int, monthly_contribution: float, annual_return_pct: float) -> pd.DataFrame:
    r = (annual_return_pct / 100.0) / 12.0
    balance = 0.0
    rows = []
    for m in range(0, months + 1):
        rows.append({"Month": m, "Balance": balance})
        balance = balance * (1 + r) + monthly_contribution
    return pd.DataFrame(rows)

def _reach_month(df: pd.DataFrame, target_amount: float):
    hit = df[df["Balance"] >= target_amount]
    if hit.empty:
        return None
    return int(hit.iloc[0]["Month"])
