# src/agents/portfolio.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List
import pandas as pd


@dataclass
class AgentResult:
    answer: str
    sources: List[str]
    portfolio_df: Any = None
    portfolio_summary: Dict[str, Any] = None


class PortfolioAgent:
    """
    Demo portfolio agent (education only).
    Replace the holdings with your real data later (CSV/DB/user input).
    """

    def __init__(self):
        pass

    def _load_demo_portfolio(self) -> pd.DataFrame:
        # ✅ You can later replace this with real portfolio data source
        rows = [
            {"Asset": "MSFT", "Value": 2000.0, "Class": "Equity"},
            {"Asset": "AAPL", "Value": 1500.0, "Class": "Equity"},
            {"Asset": "SPY",  "Value": 1800.0, "Class": "ETF"},
            {"Asset": "BND",  "Value": 1000.0, "Class": "Bond ETF"},
        ]
        return pd.DataFrame(rows)

    def _diversification_score(self, df: pd.DataFrame) -> float:
        # simple heuristic: more spread = better; concentration reduces score
        total = df["Value"].sum()
        if total <= 0:
            return 0.0
        w = (df["Value"] / total).values
        # Herfindahl-Hirschman Index
        hhi = float((w ** 2).sum())
        score = (1.0 - hhi) * 100.0  # higher = more diversified
        return max(0.0, min(100.0, score))

    def run(self, state: Dict[str, Any]) -> AgentResult:
        df = self._load_demo_portfolio()

        total = float(df["Value"].sum())
        df["AllocationPct"] = (df["Value"] / total * 100.0).round(2)

        top_row = df.sort_values("Value", ascending=False).iloc[0]
        top_asset = str(top_row["Asset"])
        top_pct = float(top_row["AllocationPct"])

        unique_assets = int(df["Asset"].nunique())
        asset_classes = int(df["Class"].nunique())

        score = self._diversification_score(df)

        summary = {
            "total_value": total,
            "top_asset": top_asset,
            "top_pct": top_pct,
            "unique_assets": unique_assets,
            "asset_classes": asset_classes,
            "diversification_score": round(score, 1),
        }

        answer = (
            "**Portfolio Summary (Education Only)**\n\n"
            f"- Total value: **${total:,.2f}**\n"
            f"- Largest holding: **{top_asset}** ({top_pct:.1f}%)\n"
            f"- Unique assets: **{unique_assets}**\n"
            f"- Unique asset classes: **{asset_classes}**\n"
            f"- Diversification score (0–100): **{summary['diversification_score']}**\n\n"
            "Tip: Diversification tends to improve when allocation is spread across multiple assets/classes "
            "and no single holding dominates."
        )

        return AgentResult(
            answer=answer,
            sources=[],  # portfolio agent is not KB-based by default
            portfolio_df=df[["Asset", "Value", "AllocationPct"]],
            portfolio_summary=summary,
        )
