"""
Live Market Data Feed & Tick Engine for BharatAlpha Trade.
Provides live tick updates, index quotes, and option price updates.
"""

import time
import random
from typing import Dict, Any

class MarketFeedEngine:
    def __init__(self):
        # Base prices
        self.indices = {
            "NIFTY": {"symbol": "NSE:NIFTY50-INDEX", "name": "NIFTY 50", "price": 24628.50, "change": +45.20, "change_pct": +0.18, "high": 24680.0, "low": 24550.0},
            "BANKNIFTY": {"symbol": "NSE:NIFTYBANK-INDEX", "name": "BANK NIFTY", "price": 52340.25, "change": -120.40, "change_pct": -0.23, "high": 52500.0, "low": 52150.0},
            "FINNIFTY": {"symbol": "NSE:FINNIFTY-INDEX", "name": "FIN NIFTY", "price": 23410.10, "change": +32.15, "change_pct": +0.14, "high": 23460.0, "low": 23350.0},
            "SENSEX": {"symbol": "BSE:SENSEX-INDEX", "name": "BSE SENSEX", "price": 80720.80, "change": +180.50, "change_pct": +0.22, "high": 80900.0, "low": 80450.0},
        }

    def get_live_ticks(self) -> Dict[str, Any]:
        """
        Returns real-time tick updates with slight random Brownian walk
        simulating live exchange streaming ticks.
        """
        ticks = {}
        for key, data in self.indices.items():
            # Small random tick fluctuation (-0.05% to +0.05%)
            delta = round(random.uniform(-1.5, 1.8), 2)
            if key == "BANKNIFTY" or key == "SENSEX":
                delta = round(random.uniform(-4.5, 5.2), 2)

            data["price"] = round(data["price"] + delta, 2)
            data["change"] = round(data["change"] + delta, 2)
            data["change_pct"] = round((data["change"] / (data["price"] - data["change"])) * 100, 2)
            data["last_tick_direction"] = "UP" if delta >= 0 else "DOWN"
            data["last_tick_delta"] = delta
            data["high"] = max(data["high"], data["price"])
            data["low"] = min(data["low"], data["price"])
            
            ticks[key] = {**data}

        return {
            "status": "success",
            "timestamp": time.strftime("%H:%M:%S"),
            "ticks": ticks
        }

market_feed = MarketFeedEngine()
