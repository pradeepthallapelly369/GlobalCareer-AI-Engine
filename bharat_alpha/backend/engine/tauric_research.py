"""
BharatAlpha AI — TauricResearch TradingAgents Integration
==========================================================
Wraps the TradingAgents multi-agent LLM framework as "Drona AI" —
a deep research agent that orchestrates fundamental, sentiment,
technical, and news analysts with bull/bear debate for comprehensive
trading decisions.

Uses OpenRouter API (with DeepSeek models) for inference.
"""

import sys
import os
import json
import traceback
from typing import Dict, Any, Optional, Generator
from datetime import datetime

# Add TradingAgents to sys.path so we can import it regardless of working dir
TRADING_AGENTS_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "TradingAgents")
)
if os.path.exists(TRADING_AGENTS_PATH) and TRADING_AGENTS_PATH not in sys.path:
    sys.path.insert(0, TRADING_AGENTS_PATH)

# Load OpenRouter key from TradingAgents .env if present
_TA_ENV = os.path.join(TRADING_AGENTS_PATH, ".env")
if os.path.exists(_TA_ENV):
    from dotenv import load_dotenv
    load_dotenv(_TA_ENV, override=False)



def normalize_ticker(ticker: str) -> str:
    """Normalize user ticker input for TradingAgents and data vendors."""
    t = ticker.strip().upper()
    if "." in t or "-" in t or "=" in t or "^" in t:
        return t
    # Known US mega-caps / ETFs
    known_us = {
        "AAPL", "MSFT", "GOOG", "GOOGL", "AMZN", "META", "NVDA", "TSLA",
        "SPY", "QQQ", "DIA", "IWM", "AMD", "NFLX", "INTC", "BABA", "COIN"
    }
    if t in known_us:
        return t
    # Default to NSE India
    return f"{t}.NS"


class DronaResearchEngine:
    """
    Drona AI — Deep Research Multi-Agent Engine
    Powered by TauricResearch/TradingAgents framework.

    Orchestrates:
    - Fundamental Analyst: Company financials, earnings quality
    - Technical Analyst: MACD, RSI, price patterns
    - Sentiment Analyst: News sentiment, social media mood
    - News Analyst: Macro news, geopolitical events
    - Bull/Bear Researchers: Structured debate on investment thesis
    - Trader: Final trading decision
    - Risk Management: Position sizing, risk assessment
    """

    def __init__(self):
        self._ta_graph = None
        self._config = None
        self._available = False
        self._init_error = None
        self._initialize()

    def _initialize(self):
        """Initialize TradingAgents graph with OpenRouter backend."""
        try:
            from tradingagents.default_config import DEFAULT_CONFIG
            from tradingagents.graph.trading_graph import TradingAgentsGraph

            self._config = DEFAULT_CONFIG.copy()

            # ── LLM backend: OpenRouter with DeepSeek models ────────────────
            self._config["llm_provider"] = "openrouter"
            self._config["deep_think_llm"] = "deepseek/deepseek-v4-pro-0813"
            self._config["quick_think_llm"] = "deepseek/deepseek-v4.1-flash"
            self._config["max_debate_rounds"] = 1
            self._config["max_risk_discuss_rounds"] = 1
            self._config["max_tokens"] = 8192

            self._ta_graph = TradingAgentsGraph(debug=False, config=self._config)
            self._available = True
            print("[DRONA] ✅ TradingAgents initialized — OpenRouter / DeepSeek backend")

        except ImportError as e:
            self._init_error = f"TradingAgents not installed: {e}"
            print(f"[DRONA] ⚠️  {self._init_error}")
            self._available = False
        except Exception as e:
            self._init_error = f"Initialization error: {e}"
            print(f"[DRONA] ⚠️  {self._init_error}")
            traceback.print_exc()
            self._available = False

    def is_available(self) -> bool:
        """Check if TradingAgents framework is ready."""
        return self._available

    def run_deep_research(
        self, ticker: str, analysis_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run full multi-agent deep research on a ticker.

        Args:
            ticker:        NSE/BSE ticker (e.g. 'SBIN.NS', 'RELIANCE.NS', 'AAPL')
            analysis_date: Date string 'YYYY-MM-DD' (defaults to today)

        Returns:
            Structured result dict with decision, reasoning, agents_involved.
        """
        ticker = normalize_ticker(ticker)
        if analysis_date is None:
            analysis_date = datetime.now().strftime("%Y-%m-%d")

        if not self._available or self._ta_graph is None:
            return self._generate_fallback_research(ticker, analysis_date, self._init_error)

        try:
            print(f"[DRONA] 🔬 Running deep research: {ticker} @ {analysis_date}")
            _, raw_decision = self._ta_graph.propagate(ticker, analysis_date)
            decision = self._parse_decision(raw_decision)
            print(f"[DRONA] ✅ Research complete: {ticker} → {decision.get('action')}")
            return {
                "status": "success",
                "engine": "tradingagents_openrouter",
                "ticker": ticker,
                "analysis_date": analysis_date,
                "decision": decision,
                "agents_involved": [
                    "Fundamental Analyst",
                    "Technical Analyst",
                    "Sentiment Analyst",
                    "News Analyst",
                    "Bull Researcher",
                    "Bear Researcher",
                    "Trader",
                    "Risk Manager",
                    "Portfolio Manager",
                ],
                "llm_provider": "openrouter",
                "deep_model": self._config.get("deep_think_llm"),
                "quick_model": self._config.get("quick_think_llm"),
            }
        except Exception as e:
            print(f"[DRONA] ❌ Deep research failed for {ticker}: {e}")
            traceback.print_exc()
            return self._generate_fallback_research(ticker, analysis_date, str(e))

    def _parse_decision(self, raw_decision) -> Dict[str, Any]:
        """Parse TradingAgents raw output into a clean dict."""
        if isinstance(raw_decision, dict):
            action = raw_decision.get("action", raw_decision.get("decision", "HOLD")).upper()
            return {
                "action": action,
                "confidence": raw_decision.get("confidence", 70),
                "reasoning": raw_decision.get("reasoning", str(raw_decision)),
                "risk_assessment": raw_decision.get("risk_assessment", ""),
                "trade_plan": raw_decision.get("trade_plan", {}),
            }
        if isinstance(raw_decision, str):
            text = raw_decision.upper()
            if "BUY" in text:
                action = "BUY"
            elif "SELL" in text:
                action = "SELL"
            else:
                action = "HOLD"
            return {
                "action": action,
                "confidence": 70,
                "reasoning": raw_decision,
                "risk_assessment": "",
                "trade_plan": {},
            }
        return {
            "action": "HOLD",
            "confidence": 50,
            "reasoning": str(raw_decision),
            "risk_assessment": "",
            "trade_plan": {},
        }

    # ── Agent progress SSE stream ────────────────────────────────────────────

    def stream_research_progress(
        self, ticker: str, analysis_date: Optional[str] = None
    ) -> Generator[str, None, None]:
        """
        Server-Sent Events generator that yields JSON progress updates
        as each agent completes its work.

        Yields JSON strings (one per line) of the form:
            {"stage": "...", "agent": "...", "status": "running|done|error", "detail": "..."}
        """
        ticker = normalize_ticker(ticker)
        if analysis_date is None:
            analysis_date = datetime.now().strftime("%Y-%m-%d")

        def _evt(stage: str, agent: str, status: str, detail: str = "") -> str:
            return (
                "data: "
                + json.dumps(
                    {
                        "stage": stage,
                        "agent": agent,
                        "status": status,
                        "detail": detail,
                        "ts": datetime.now().isoformat(),
                    }
                )
                + "\n\n"
            )

        yield _evt("init", "Drona AI", "running", f"Starting deep research for {ticker} on {analysis_date}")

        if not self._available or self._ta_graph is None:
            yield _evt("error", "Drona AI", "error", self._init_error or "Engine unavailable")
            result = self._generate_fallback_research(ticker, analysis_date, self._init_error)
            yield _evt("fallback", "BharatAlpha Fallback", "done", json.dumps(result))
            return

        agents_order = [
            ("market_data", "Market Data Fetcher"),
            ("fundamental", "Fundamental Analyst"),
            ("technical", "Technical Analyst"),
            ("sentiment", "Sentiment Analyst"),
            ("news", "News Analyst"),
            ("bull_bear", "Bull/Bear Researchers"),
            ("trader", "Trader Agent"),
            ("risk", "Risk Manager"),
            ("portfolio", "Portfolio Manager"),
        ]

        for stage, agent_name in agents_order:
            yield _evt(stage, agent_name, "running", f"{agent_name} is analysing {ticker}…")

        # Run the actual analysis (blocking — happens in a thread pool in FastAPI)
        try:
            _, raw_decision = self._ta_graph.propagate(ticker, analysis_date)
            decision = self._parse_decision(raw_decision)
            result = {
                "status": "success",
                "engine": "tradingagents_openrouter",
                "ticker": ticker,
                "analysis_date": analysis_date,
                "decision": decision,
                "agents_involved": [a for _, a in agents_order],
                "llm_provider": "openrouter",
                "deep_model": self._config.get("deep_think_llm"),
                "quick_model": self._config.get("quick_think_llm"),
            }
            for stage, agent_name in agents_order:
                yield _evt(stage, agent_name, "done", f"{agent_name} completed")
            yield _evt("complete", "Drona AI", "done", json.dumps(result))
        except Exception as e:
            yield _evt("error", "Drona AI", "error", str(e))
            result = self._generate_fallback_research(ticker, analysis_date, str(e))
            yield _evt("fallback", "BharatAlpha Fallback", "done", json.dumps(result))

    # ── Fallback (BharatAlpha native analysis) ───────────────────────────────

    def _generate_fallback_research(
        self, ticker: str, date: str, error: str = None
    ) -> Dict[str, Any]:
        """
        Generate a structured fallback response when TradingAgents is unavailable.
        Uses BharatAlpha's own analysis modules as a lightweight alternative.
        """
        from backend.engine.technicals import analyze_stock_technicals
        from backend.engine.fundamentals import analyze_stock_fundamentals
        import yfinance as yf

        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period="6mo").dropna(subset=["Close"])
            if not df.empty and len(df) >= 20:
                tech = analyze_stock_technicals(df)
                fund = analyze_stock_fundamentals(ticker)

                tech_score = tech.get("technical_score", 50)
                quality_score = fund.get("quality_score", 50)
                combined = tech_score * 0.4 + quality_score * 0.6

                if combined >= 75:
                    action, confidence = "BUY", min(90, int(combined))
                elif combined >= 60:
                    action, confidence = "HOLD", int(combined)
                elif combined >= 40:
                    action, confidence = "HOLD", int(combined)
                else:
                    action, confidence = "SELL", int(100 - combined)

                return {
                    "status": "success",
                    "engine": "bharat_alpha_fallback",
                    "ticker": ticker,
                    "analysis_date": date,
                    "decision": {
                        "action": action,
                        "confidence": confidence,
                        "reasoning": (
                            f"BharatAlpha Composite Analysis for {ticker}:\n"
                            f"• Technical Score: {tech_score}/100  (Trend: {tech.get('trend_status', 'N/A')})\n"
                            f"• Quality Score: {quality_score}/100  (Category: {fund.get('category', 'N/A')})\n"
                            f"• RSI: {tech.get('rsi', 'N/A')} | MACD Hist: {tech.get('macd_hist', 'N/A')}\n"
                            f"• Buffett Score: {fund.get('buffett_score', 'N/A')}/100\n"
                            f"• D/E Ratio: {fund.get('debt_to_equity', 'N/A')}\n"
                            f"• PE: {fund.get('pe_ratio', 'N/A')} | PEG: {fund.get('peg_ratio', 'N/A')}"
                        ),
                        "risk_assessment": f"Stop below ₹{tech.get('atr_stop', 'N/A')}",
                        "trade_plan": {},
                    },
                    "agents_involved": [
                        "BharatAlpha Technical Analyst",
                        "BharatAlpha Fundamental Analyst",
                    ],
                    "note": "Using BharatAlpha native analysis (TradingAgents fallback)",
                    "error": error,
                }
        except Exception as e:
            print(f"[DRONA] Fallback also failed for {ticker}: {e}")

        return {
            "status": "error",
            "engine": "none",
            "ticker": ticker,
            "analysis_date": date,
            "decision": {
                "action": "HOLD",
                "confidence": 30,
                "reasoning": "Unable to perform deep research at this time. Please try again later.",
                "risk_assessment": "",
                "trade_plan": {},
            },
            "agents_involved": [],
            "error": error or self._init_error or "Unknown error",
        }


# Singleton instance — imported by main.py
drona_engine = DronaResearchEngine()
