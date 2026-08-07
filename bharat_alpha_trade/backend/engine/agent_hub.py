"""
BharatAlpha Trade — Autonomous Multi-Agent Trading Engine
Supports Options Chain Greeks analysis, strategy suggestions,
and automated Paper & Real (Fyers/Zerodha) order execution.
"""

from typing import Dict, List, Any, Optional
import datetime
from backend.engine.options_greeks import calculate_all_greeks, enrich_option_chain_with_greeks
from backend.engine.options_strategies import build_strategy_legs, analyze_strategy
from backend.broker.fyers_connector import FyersConnector
from backend.broker.zerodha_connector import ZerodhaConnector

class TradeAgentEngine:
    def __init__(self):
        self.fyers = FyersConnector()
        self.zerodha = ZerodhaConnector()
        
        # In-memory paper trading ledger
        self.paper_positions = [
            {
                "id": "trade_001",
                "symbol": "NIFTY",
                "action": "SELL",
                "type": "CE",
                "strike": 24600,
                "qty": 25,
                "entry_premium": 180.0,
                "status": "FILLED",
                "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                "id": "trade_002",
                "symbol": "NIFTY",
                "action": "SELL",
                "type": "PE",
                "strike": 24600,
                "qty": 25,
                "entry_premium": 170.0,
                "status": "FILLED",
                "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        ]

    def process_chat(self, query: str, agent: str = "arya") -> Dict[str, Any]:
        """Handles user questions for options trading & strategy recommendations."""
        query_lower = query.lower()
        
        if "iron condor" in query_lower:
            strat = analyze_strategy("IRON_CONDOR", spot_price=24600)
            reply = (
                f"⚡ **Arya AI Option Strategy Recommendation**:\n\n"
                f"**NIFTY Iron Condor Setup**:\n"
                f"• Buy 24200 PE & Sell 24400 PE (Put Credit Spread)\n"
                f"• Sell 24800 CE & Buy 25000 CE (Call Credit Spread)\n"
                f"• **Net Premium Credit**: ₹{strat.get('net_premium_total', 2500):.2f}\n"
                f"• **Max Profit**: ₹{strat.get('max_profit', 2500):.2f} per lot\n"
                f"• **Max Loss**: ₹{strat.get('max_loss', -2500):.2f}\n\n"
                f"Click **Execute Iron Condor** to place order in Paper or Live Broker mode."
            )
            trade_obj = {
                "action": "EXECUTE_STRATEGY",
                "strategy": "IRON_CONDOR",
                "symbol": "NIFTY",
                "details": strat
            }
        elif "straddle" in query_lower:
            strat = analyze_strategy("SHORT_STRADDLE", spot_price=24600)
            reply = (
                f"⚡ **Arya AI Short Straddle Analysis**:\n\n"
                f"**NIFTY 24600 ATM Short Straddle**:\n"
                f"• Sell 24600 CE @ ₹180 & Sell 24600 PE @ ₹170\n"
                f"• Total Premium Collected: ₹350/lot (₹8,750 per lot)\n"
                f"• Upper Breakeven: ₹24,950 | Lower Breakeven: ₹24,250\n"
                f"• High Theta Decay (+₹420/day capture)."
            )
            trade_obj = {
                "action": "EXECUTE_STRATEGY",
                "strategy": "SHORT_STRADDLE",
                "symbol": "NIFTY",
                "details": strat
            }
        else:
            reply = (
                f"⚡ **Arya AI Options Quantitative Cockpit**:\n\n"
                f"• **NIFTY Spot Price**: ₹24,600 | **Days to Expiry**: 5 Days\n"
                f"• **ATM Strike (24600)**: CE Delta (+0.52), PE Delta (-0.48), ATM Gamma (0.0018), Theta (-14.2/day).\n"
                f"• **Strategy Suggestion**: Market is exhibiting range-bound compression. Favorable conditions for Short Straddle or Iron Condor delta-neutral income strategies."
            )
            trade_obj = None

        return {
            "status": "success",
            "reply": reply,
            "trade_action": trade_obj
        }

    def execute_trade(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Executes trade in Paper Trading or Real Broker mode."""
        symbol = payload.get("symbol", "NIFTY")
        action = payload.get("action", "BUY")
        mode = payload.get("mode", "paper") # paper or real
        broker = payload.get("broker", "fyers") # fyers or zerodha
        strategy_type = payload.get("strategy", "SINGLE_LEG")
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if mode == "real":
            # Attempt live broker execution
            if broker == "fyers":
                broker_res = self.fyers.place_order(symbol, action, payload.get("qty", 25), payload.get("price", 0))
            else:
                broker_res = self.zerodha.place_order(symbol, action, payload.get("qty", 25), payload.get("price", 0))
            
            return {
                "status": "success" if broker_res.get("status") == "success" else "error",
                "message": f"Real Broker Execution ({broker.upper()}): {broker_res.get('message')}",
                "order_details": broker_res
            }
        else:
            # Paper trading mode
            new_pos = {
                "id": f"trade_{len(self.paper_positions) + 1:03d}",
                "symbol": symbol,
                "action": action,
                "type": payload.get("type", "CE"),
                "strike": payload.get("strike", 24600),
                "qty": payload.get("qty", 25),
                "entry_premium": payload.get("entry_price", 180.0),
                "status": "FILLED",
                "time": timestamp,
                "mode": "PAPER"
            }
            self.paper_positions.insert(0, new_pos)
            
            return {
                "status": "success",
                "message": f"✅ Paper Trade Executed Successfully! Order ID: {new_pos['id']}",
                "position": new_pos,
                "total_positions": len(self.paper_positions)
            }

    def get_positions(self) -> List[Dict[str, Any]]:
        return self.paper_positions
