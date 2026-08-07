"""
Options Strategy Templates & Payoff Calculator.
7 institutional-grade preset strategies for Nifty / Bank Nifty options.
"""
import numpy as np
from backend.engine.options_greeks import (
    bs_call_price, bs_put_price, calculate_all_greeks,
    solve_implied_volatility, days_to_expiry_fraction, RISK_FREE_RATE
)

STRATEGY_CATALOG = {
    "SHORT_STRADDLE": {
        "name": "Short Straddle",
        "legs": 2,
        "view": "Neutral / Low Volatility",
        "description": "Sell ATM Call + Sell ATM Put. Profit if price stays near current level.",
    },
    "SHORT_STRANGLE": {
        "name": "Short Strangle",
        "legs": 2,
        "view": "Neutral / Range-Bound",
        "description": "Sell OTM Call + Sell OTM Put. Wider profit zone than straddle.",
    },
    "LONG_STRADDLE": {
        "name": "Long Straddle",
        "legs": 2,
        "view": "High Volatility / Event Play",
        "description": "Buy ATM Call + Buy ATM Put. Profit from big move in either direction.",
    },
    "IRON_CONDOR": {
        "name": "Iron Condor",
        "legs": 4,
        "view": "Neutral / Premium Collection",
        "description": "Sell OTM Call + Buy far OTM Call + Sell OTM Put + Buy far OTM Put.",
    },
    "BULL_CALL_SPREAD": {
        "name": "Bull Call Spread",
        "legs": 2,
        "view": "Moderately Bullish",
        "description": "Buy ATM Call + Sell OTM Call. Limited risk bullish bet.",
    },
    "BEAR_PUT_SPREAD": {
        "name": "Bear Put Spread",
        "legs": 2,
        "view": "Moderately Bearish",
        "description": "Buy ATM Put + Sell OTM Put. Limited risk bearish bet.",
    },
    "JADE_LIZARD": {
        "name": "Jade Lizard",
        "legs": 3,
        "view": "Neutral to Bullish",
        "description": "Sell OTM Put + Sell OTM Call + Buy far OTM Call. No upside risk if credit > call spread width.",
    },
}

def _round_to_strike(price, step=50):
    """Round price to nearest strike interval (50 for Nifty, 100 for Bank Nifty)."""
    return int(round(price / step) * step)

def build_strategy_legs(strategy_key, spot_price, strike_step=50, premiums=None):
    """
    Build the option legs for a given strategy around the spot price.
    premiums: optional dict mapping strike -> {"ce": price, "pe": price}
    """
    atm = _round_to_strike(spot_price, strike_step)
    otm_offset_1 = strike_step * 4  # ~200 pts for Nifty
    otm_offset_2 = strike_step * 8  # ~400 pts for Nifty

    def _get_premium(strike, opt_type, fallback=150):
        if premiums and strike in premiums:
            return premiums[strike].get(opt_type.lower(), fallback)
        return fallback

    legs = []

    if strategy_key == "SHORT_STRADDLE":
        legs = [
            {"action": "SELL", "type": "CE", "strike": atm, "qty": 1, "premium": _get_premium(atm, "ce", 180)},
            {"action": "SELL", "type": "PE", "strike": atm, "qty": 1, "premium": _get_premium(atm, "pe", 170)},
        ]
    elif strategy_key == "SHORT_STRANGLE":
        legs = [
            {"action": "SELL", "type": "CE", "strike": atm + otm_offset_1, "qty": 1, "premium": _get_premium(atm + otm_offset_1, "ce", 80)},
            {"action": "SELL", "type": "PE", "strike": atm - otm_offset_1, "qty": 1, "premium": _get_premium(atm - otm_offset_1, "pe", 75)},
        ]
    elif strategy_key == "LONG_STRADDLE":
        legs = [
            {"action": "BUY", "type": "CE", "strike": atm, "qty": 1, "premium": _get_premium(atm, "ce", 180)},
            {"action": "BUY", "type": "PE", "strike": atm, "qty": 1, "premium": _get_premium(atm, "pe", 170)},
        ]
    elif strategy_key == "IRON_CONDOR":
        legs = [
            {"action": "SELL", "type": "CE", "strike": atm + otm_offset_1, "qty": 1, "premium": _get_premium(atm + otm_offset_1, "ce", 80)},
            {"action": "BUY", "type": "CE", "strike": atm + otm_offset_2, "qty": 1, "premium": _get_premium(atm + otm_offset_2, "ce", 30)},
            {"action": "SELL", "type": "PE", "strike": atm - otm_offset_1, "qty": 1, "premium": _get_premium(atm - otm_offset_1, "pe", 75)},
            {"action": "BUY", "type": "PE", "strike": atm - otm_offset_2, "qty": 1, "premium": _get_premium(atm - otm_offset_2, "pe", 25)},
        ]
    elif strategy_key == "BULL_CALL_SPREAD":
        legs = [
            {"action": "BUY", "type": "CE", "strike": atm, "qty": 1, "premium": _get_premium(atm, "ce", 180)},
            {"action": "SELL", "type": "CE", "strike": atm + otm_offset_1, "qty": 1, "premium": _get_premium(atm + otm_offset_1, "ce", 80)},
        ]
    elif strategy_key == "BEAR_PUT_SPREAD":
        legs = [
            {"action": "BUY", "type": "PE", "strike": atm, "qty": 1, "premium": _get_premium(atm, "pe", 170)},
            {"action": "SELL", "type": "PE", "strike": atm - otm_offset_1, "qty": 1, "premium": _get_premium(atm - otm_offset_1, "pe", 75)},
        ]
    elif strategy_key == "JADE_LIZARD":
        legs = [
            {"action": "SELL", "type": "PE", "strike": atm - otm_offset_1, "qty": 1, "premium": _get_premium(atm - otm_offset_1, "pe", 75)},
            {"action": "SELL", "type": "CE", "strike": atm + otm_offset_1, "qty": 1, "premium": _get_premium(atm + otm_offset_1, "ce", 80)},
            {"action": "BUY", "type": "CE", "strike": atm + otm_offset_2, "qty": 1, "premium": _get_premium(atm + otm_offset_2, "ce", 30)},
        ]

    return legs

def calculate_payoff_at_expiry(legs, price_at_expiry, lot_size=25):
    """Calculate P&L at expiry for given underlying price."""
    total_pnl = 0.0
    for leg in legs:
        strike = leg["strike"]
        premium = leg["premium"]
        qty_mult = 1 if leg["action"] == "BUY" else -1

        if leg["type"] == "CE":
            intrinsic = max(price_at_expiry - strike, 0)
        else:
            intrinsic = max(strike - price_at_expiry, 0)

        leg_pnl = (intrinsic - premium) * qty_mult * lot_size
        total_pnl += leg_pnl

    return round(total_pnl, 2)

def generate_payoff_curve(legs, spot_price, lot_size=25, num_points=80):
    """Generate payoff curve data for charting."""
    all_strikes = [leg["strike"] for leg in legs]
    low = min(all_strikes) - 600
    high = max(all_strikes) + 600
    prices = np.linspace(low, high, num_points)

    curve = []
    for p in prices:
        pnl = calculate_payoff_at_expiry(legs, float(p), lot_size)
        curve.append({"price": round(float(p), 0), "pnl": pnl})

    return curve

def analyze_strategy(strategy_key, spot_price, lot_size=25, strike_step=50, premiums=None):
    """Full strategy analysis: legs, payoff curve, max P/L, breakevens."""
    meta = STRATEGY_CATALOG.get(strategy_key)
    if not meta:
        return {"error": f"Unknown strategy: {strategy_key}"}

    legs = build_strategy_legs(strategy_key, spot_price, strike_step, premiums)
    curve = generate_payoff_curve(legs, spot_price, lot_size)

    pnl_values = [pt["pnl"] for pt in curve]
    max_profit = max(pnl_values)
    max_loss = min(pnl_values)

    # Find breakeven points (where P&L crosses zero)
    breakevens = []
    for i in range(1, len(curve)):
        if (curve[i-1]["pnl"] < 0 and curve[i]["pnl"] >= 0) or \
           (curve[i-1]["pnl"] >= 0 and curve[i]["pnl"] < 0):
            breakevens.append(round(curve[i]["price"], 0))

    # Net premium received/paid
    net_premium = 0
    for leg in legs:
        if leg["action"] == "SELL":
            net_premium += leg["premium"]
        else:
            net_premium -= leg["premium"]
    net_premium_total = round(net_premium * lot_size, 2)

    return {
        "strategy_key": strategy_key,
        "name": meta["name"],
        "view": meta["view"],
        "description": meta["description"],
        "num_legs": meta["legs"],
        "legs": legs,
        "lot_size": lot_size,
        "spot_price": spot_price,
        "net_premium_per_lot": round(net_premium, 2),
        "net_premium_total": net_premium_total,
        "max_profit": max_profit,
        "max_loss": max_loss,
        "breakevens": breakevens,
        "payoff_curve": curve,
    }
