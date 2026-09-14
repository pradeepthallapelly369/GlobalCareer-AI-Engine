"""
BharatAlpha AI — TauricResearch TradingAgents Integration
==========================================================
Wraps the TradingAgents multi-agent LLM framework as "Drona AI" —
a deep research agent that orchestrates fundamental, sentiment,
technical, and news analysts with bull/bear debate for comprehensive
trading decisions.

Uses local Ollama LLM backend for inference.
"""

import sys
import os
import json
import traceback
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

# Add TradingAgents to path
TRADING_AGENTS_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "..", "..", "..", "TradingAgents"
)
if os.path.exists(TRADING_AGENTS_PATH):
    sys.path.insert(0, TRADING_AGENTS_PATH)


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
        """Initialize TradingAgents graph with Ollama backend."""
        try:
            from tradingagents.default_config import DEFAULT_CONFIG
            from tradingagents.graph.trading_graph import TradingAgentsGraph

            self._config = DEFAULT_CONFIG.copy()
            # Configure for local Ollama
            self._config["llm_provider"] = "ollama"
            self._config["deep_think_llm"] = "llama3.1:8b"
            self._config["quick_think_llm"] = "llama3.1:8b"
            self._config["max_debate_rounds"] = 1
            self._config["max_risk_discuss_rounds"] = 1
            self._config["data_vendors"] = {
                "core_stock_apis": "yfinance",
                "technical_indicators": "yfinance",
                "fundamental_data": "yfinance",
                "news_data": "yfinance",
                "macro_data": "fred",
                "prediction_markets": "polymarket",
            }
            # Use Indian benchmark for NSE tickers
            self._config["benchmark_map"] = {
                ".NS": "^NSEI",
                ".BO": "^BSESN",
                "": "SPY",
            }

            self._ta_graph = TradingAgentsGraph(debug=False, config=self._config)
            self._available = True
            print("[DRONA] TradingAgents framework initialized successfully with Ollama backend")

        except ImportError as e:
            self._init_error = f"TradingAgents not installed: {e}"
            print(f"[DRONA] {self._init_error}")
            self._available = False
        except Exception as e:
            self._init_error = f"Initialization error: {e}"
            print(f"[DRONA] {self._init_error}")
            traceback.print_exc()
            self._available = False

    def is_available(self) -> bool:
        """Check if TradingAgents framework is ready."""
        return self._available

    def run_deep_research(self, ticker: str, analysis_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Run full multi-agent deep research on a ticker.
        
        Args:
            ticker: Stock symbol (e.g., 'RELIANCE.NS', 'SBIN.NS', 'AAPL')
            analysis_date: Date string 'YYYY-MM-DD' (defaults to today)
        
        Returns:
            Comprehensive analysis dict with decision, confidence, and agent reports.
        """
        # Ensure .NS suffix for Indian stocks
        clean_ticker = ticker.upper().strip()
        if not any(clean_ticker.endswith(sfx) for sfx in [".NS", ".BO", ".HK", ".T", ".L"]):
            if not clean_ticker.endswith("-USD"):
                clean_ticker = f"{clean_ticker}.NS"

        if not analysis_date:
            analysis_date = datetime.now().strftime("%Y-%m-%d")

        if not self._available:
            return self._generate_fallback_research(clean_ticker, analysis_date)

        try:
            print(f"[DRONA] Starting deep research for {clean_ticker} on {analysis_date}...")
            _, decision = self._ta_graph.propagate(clean_ticker, analysis_date)

            return {
                "status": "success",
                "engine": "tauric_tradingagents",
                "ticker": clean_ticker,
                "analysis_date": analysis_date,
                "decision": self._parse_decision(decision),
                "raw_decision": str(decision) if decision else "No decision generated",
                "framework_version": "v0.4.0",
            }

        except Exception as e:
            print(f"[DRONA] Research error for {clean_ticker}: {e}")
            traceback.print_exc()
            return self._generate_fallback_research(clean_ticker, analysis_date, str(e))

    def _parse_decision(self, decision) -> Dict[str, Any]:
        """Parse TradingAgents decision output into structured format."""
        if not decision:
            return {
                "action": "HOLD",
                "confidence": 50,
                "reasoning": "No decision generated by the research framework.",
            }

        # TradingAgents returns decision as a string or structured object
        decision_str = str(decision).lower()

        # Extract action
        if "strong buy" in decision_str or "strongly recommend buying" in decision_str:
            action = "STRONG_BUY"
            confidence = 85
        elif "buy" in decision_str:
            action = "BUY"
            confidence = 70
        elif "strong sell" in decision_str or "strongly recommend selling" in decision_str:
            action = "STRONG_SELL"
            confidence = 85
        elif "sell" in decision_str:
            action = "SELL"
            confidence = 70
        else:
            action = "HOLD"
            confidence = 50

        return {
            "action": action,
            "confidence": confidence,
            "reasoning": str(decision)[:2000],
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
        }

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

                # Generate decision based on combined scores
                tech_score = tech.get("technical_score", 50)
                quality_score = fund.get("quality_score", 50)
                combined = (tech_score * 0.4 + quality_score * 0.6)

                if combined >= 75:
                    action = "BUY"
                    confidence = min(90, int(combined))
                elif combined >= 60:
                    action = "HOLD"
                    confidence = int(combined)
                elif combined >= 40:
                    action = "HOLD"
                    confidence = int(combined)
                else:
                    action = "SELL"
                    confidence = int(100 - combined)

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
                            f"• Technical Score: {tech_score}/100 (Trend: {tech.get('trend_status', 'N/A')})\n"
                            f"• Quality Score: {quality_score}/100 (Category: {fund.get('category', 'N/A')})\n"
                            f"• RSI: {tech.get('rsi', 'N/A')} | MACD Hist: {tech.get('macd_hist', 'N/A')}\n"
                            f"• Buffett Score: {fund.get('buffett_score', 'N/A')}/100\n"
                            f"• D/E Ratio: {fund.get('debt_to_equity', 'N/A')}\n"
                            f"• PE: {fund.get('pe_ratio', 'N/A')} | PEG: {fund.get('peg_ratio', 'N/A')}"
                        ),
                        "agents_involved": [
                            "BharatAlpha Technical Analyst",
                            "BharatAlpha Fundamental Analyst",
                        ],
                    },
                    "note": "Using BharatAlpha native analysis (TradingAgents framework unavailable)",
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
                "agents_involved": [],
            },
            "error": error or self._init_error or "Unknown error",
        }


# Singleton instance
drona_engine = DronaResearchEngine()
