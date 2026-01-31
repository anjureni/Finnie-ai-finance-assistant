# src/agents/market.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from datetime import datetime
import os
import re

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()


@dataclass
class AgentResult:
    answer: str
    sources: List[str]
    market_df: Any = None
    market_fetched_at: Any = None
    market_ticker: Optional[str] = None
    market_is_mock: bool = False


class MarketAgent:
    def __init__(self):
        self.alpha_key = os.getenv("ALPHAVANTAGE_API_KEY", "")

    def _extract_ticker(self, text: str) -> str:
        # match tickers like AAPL, MSFT, SPY, QQQ
        m = re.findall(r"\b[A-Z]{1,5}\b", (text or "").upper())
        return m[0] if m else "SPY"

    def _extract_period(self, text: str) -> str:
        # match 5d, 1mo, 3mo, 6mo, 1y
        m = re.findall(r"\b(5d|1mo|3mo|6mo|1y)\b", (text or "").lower())
        return m[0] if m else "1mo"

    def _period_to_points(self, period: str) -> int:
        return {"5d": 6, "1mo": 30, "3mo": 90, "6mo": 180, "1y": 365}.get(period, 30)

    def _mock_df(self, points: int = 30) -> pd.DataFrame:
        dates = pd.date_range(end=pd.Timestamp.today().normalize(), periods=points)
        # simple synthetic series
        base = 100.0
        close = [base]
        for _ in range(1, points):
            close.append(close[-1] * 1.002)  # gentle uptrend
        return pd.DataFrame({"Date": dates, "Close": close})

    def _fetch_alpha_vantage_daily(self, ticker: str) -> Optional[pd.DataFrame]:
        if not self.alpha_key:
            return None

        url = "https://www.alphavantage.co/query"
        params = {
            "function": "TIME_SERIES_DAILY_ADJUSTED",
            "symbol": ticker,
            "apikey": self.alpha_key,
            "outputsize": "compact",
        }

        r = requests.get(url, params=params, timeout=20)
        data = r.json()

        ts = data.get("Time Series (Daily)")
        if not ts:
            return None

        rows = []
        for dt, vals in ts.items():
            # adjusted close preferred
            c = vals.get("5. adjusted close") or vals.get("4. close")
            if c is None:
                continue
            rows.append({"Date": pd.to_datetime(dt), "Close": float(c)})

        df = pd.DataFrame(rows).sort_values("Date")
        return df if len(df) else None

    def run(self, state: Dict[str, Any]) -> AgentResult:
        q = state.get("user_query") or state.get("query") or ""
        ticker = self._extract_ticker(q)
        period = self._extract_period(q)
        points = self._period_to_points(period)

        fetched_at = datetime.now().strftime("%Y-%m-%d %I:%M %p")

        df = self._fetch_alpha_vantage_daily(ticker)
        is_mock = False

        if df is None:
            df = self._mock_df(points)
            is_mock = True
        else:
            df = df.tail(points).reset_index(drop=True)

        # compute simple trend stats
        start = float(df["Close"].iloc[0])
        end = float(df["Close"].iloc[-1])
        pct = ((end - start) / start * 100.0) if start else 0.0
        direction = "up" if pct >= 0 else "down"

        answer = (
            f"**Market Snapshot (Education Only)**\n\n"
            f"Ticker: **{ticker}**\n"
            f"Period: **{period}**\n"
            f"Period trend: **{direction} ({pct:.2f}%)**\n"
            f"Start Close: **{start:.2f}**\n"
            f"End Close: **{end:.2f}**\n\n"
            f"Educational note: Trends describe past movement; they do not predict future performance."
        )

        return AgentResult(
            answer=answer,
            sources=[],
            market_df=df,
            market_fetched_at=fetched_at,
            market_ticker=ticker,
            market_is_mock=is_mock,
        )
