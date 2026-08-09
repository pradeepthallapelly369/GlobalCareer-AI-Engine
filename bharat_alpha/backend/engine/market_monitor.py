"""
BharatAlpha AI — Daily Market Intelligence Monitor
=====================================================
Tracks real-time market movers across the NSE:
  - Top Gainers (by % change)
  - Top Losers (by % change)
  - Unusual Volume Spikes (institutional accumulation signals)
  - Sector Performance Heatmap
  - Market Breadth (Advance/Decline ratio)
"""

import yfinance as yf
import pandas as pd
from typing import Dict, List, Any


# ─── BROAD NSE WATCHLIST FOR DAILY MONITORING ───────────────────────────
DAILY_MONITOR_TICKERS = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS",
    "BHARTIARTL.NS", "ITC.NS", "SBIN.NS", "LT.NS", "BAJFINANCE.NS",
    "HCLTECH.NS", "KOTAKBANK.NS", "TITAN.NS", "SUNPHARMA.NS", "AXISBANK.NS",
    "MARUTI.NS", "WIPRO.NS", "ULTRACEMCO.NS", "NESTLEIND.NS", "TATASTEEL.NS",
    "POWERGRID.NS", "NTPC.NS", "ONGC.NS", "COALINDIA.NS",
    "TECHM.NS", "HINDALCO.NS", "JSWSTEEL.NS",
    "HINDUNILVR.NS", "ASIANPAINT.NS", "DRREDDY.NS", "CIPLA.NS",
    "TATAMOTORS.NS", "M&M.NS", "DIVISLAB.NS", "APOLLOHOSP.NS", "BPCL.NS",
    "TATACONSUM.NS", "HEROMOTOCO.NS", "BRITANNIA.NS",
    "DIXON.NS", "TRENT.NS", "BEL.NS", "HAL.NS", "POLYCAB.NS",
    "PERSISTENT.NS", "COFORGE.NS", "KPITTECH.NS", "TATAELXSI.NS",
    "ZOMATO.NS", "DMART.NS", "NAUKRI.NS",
    "PIDILITIND.NS", "DABUR.NS", "MARICO.NS", "COLPAL.NS",
    "CHOLAFIN.NS", "MUTHOOTFIN.NS",
    "IRCTC.NS", "RVNL.NS", "HAL.NS", "MAZAGON.NS",
    "CDSL.NS", "CAMS.NS", "ANGELONE.NS",
]

# Sector classification
SECTOR_MAP = {
    "RELIANCE": "Energy", "ONGC": "Energy", "BPCL": "Energy", "COALINDIA": "Energy",
    "TCS": "IT", "INFY": "IT", "HCLTECH": "IT", "WIPRO": "IT", "TECHM": "IT",
    "PERSISTENT": "IT", "COFORGE": "IT", "KPITTECH": "IT", "TATAELXSI": "IT",
    "HDFCBANK": "Banking", "ICICIBANK": "Banking", "SBIN": "Banking", "KOTAKBANK": "Banking",
    "AXISBANK": "Banking", "INDUSINDBK": "Banking", "IDFCFIRSTB": "Banking",
    "BAJFINANCE": "NBFC", "CHOLAFIN": "NBFC", "MUTHOOTFIN": "NBFC",
    "BHARTIARTL": "Telecom", "ITC": "FMCG", "HINDUNILVR": "FMCG",
    "NESTLEIND": "FMCG", "BRITANNIA": "FMCG", "DABUR": "FMCG",
    "MARICO": "FMCG", "COLPAL": "FMCG", "TATACONSUM": "FMCG",
    "SUNPHARMA": "Pharma", "DRREDDY": "Pharma", "CIPLA": "Pharma", "DIVISLAB": "Pharma",
    "APOLLOHOSP": "Healthcare",
    "TATASTEEL": "Metals", "JSWSTEEL": "Metals", "HINDALCO": "Metals",
    "LT": "Infra", "ULTRACEMCO": "Infra", "POWERGRID": "Infra", "NTPC": "Power",
    "TITAN": "Consumer", "ASIANPAINT": "Consumer", "PIDILITIND": "Consumer",
    "TATAMOTORS": "Auto", "MARUTI": "Auto", "M&M": "Auto", "HEROMOTOCO": "Auto", "EICHERMOT": "Auto",
    "DIXON": "Electronics", "POLYCAB": "Electronics",
    "HAL": "Defence", "BEL": "Defence", "MAZAGON": "Defence",
    "ZOMATO": "Internet", "DMART": "Retail", "NAUKRI": "Internet",
    "TRENT": "Retail",
    "IRCTC": "Railways", "RVNL": "Railways",
    "CDSL": "Capital Mkts", "CAMS": "Capital Mkts", "ANGELONE": "Capital Mkts",
}


def get_daily_market_movers() -> Dict[str, Any]:
    """
    Fetches today's market movers — gainers, losers, and volume spikes
    from the monitored NSE universe.
    """
    movers = []
    advancing = 0
    declining = 0
    unchanged = 0
    sector_performance = {}

    for ticker_sym in DAILY_MONITOR_TICKERS:
        try:
            stock = yf.Ticker(ticker_sym)
            df = stock.history(period="5d")
            if df.empty or len(df) < 2:
                continue

            curr_close = float(df["Close"].iloc[-1])
            prev_close = float(df["Close"].iloc[-2])
            change = round(curr_close - prev_close, 2)
            change_pct = round(((curr_close - prev_close) / prev_close) * 100, 2)

            # Volume analysis
            curr_vol = int(df["Volume"].iloc[-1])
            avg_vol_5d = int(df["Volume"].mean())
            vol_ratio = round(curr_vol / avg_vol_5d, 2) if avg_vol_5d > 0 else 1.0

            clean_ticker = ticker_sym.replace(".NS", "").replace(".BO", "")
            company_name = stock.info.get("shortName") or clean_ticker

            sector = SECTOR_MAP.get(clean_ticker, "Other")

            record = {
                "ticker": clean_ticker,
                "company_name": company_name,
                "price": round(curr_close, 2),
                "change": change,
                "change_pct": change_pct,
                "volume": curr_vol,
                "avg_volume": avg_vol_5d,
                "volume_ratio": vol_ratio,
                "sector": sector,
                "is_volume_spike": vol_ratio >= 2.0,
            }
            movers.append(record)

            # Market breadth
            if change_pct > 0.1:
                advancing += 1
            elif change_pct < -0.1:
                declining += 1
            else:
                unchanged += 1

            # Sector tracking
            if sector not in sector_performance:
                sector_performance[sector] = {"total_change_pct": 0, "count": 0, "stocks": []}
            sector_performance[sector]["total_change_pct"] += change_pct
            sector_performance[sector]["count"] += 1
            sector_performance[sector]["stocks"].append(clean_ticker)

        except Exception as e:
            print(f"Market monitor error for {ticker_sym}: {e}")
            continue

    # Sort for gainers and losers
    movers.sort(key=lambda x: x["change_pct"], reverse=True)
    top_gainers = movers[:10]
    top_losers = list(reversed(movers[-10:]))

    # Volume spikes
    volume_spikes = [m for m in movers if m.get("is_volume_spike")]
    volume_spikes.sort(key=lambda x: x["volume_ratio"], reverse=True)

    # Sector heatmap
    sector_heatmap = []
    for sector, data in sector_performance.items():
        avg_change = round(data["total_change_pct"] / data["count"], 2) if data["count"] > 0 else 0
        sector_heatmap.append({
            "sector": sector,
            "avg_change_pct": avg_change,
            "stock_count": data["count"],
            "sentiment": "BULLISH" if avg_change >= 0.5 else ("BEARISH" if avg_change <= -0.5 else "NEUTRAL"),
        })
    sector_heatmap.sort(key=lambda x: x["avg_change_pct"], reverse=True)

    # Market breadth
    total_stocks = advancing + declining + unchanged
    ad_ratio = round(advancing / declining, 2) if declining > 0 else advancing
    if ad_ratio >= 2.0:
        market_mood = "STRONG_BULLISH"
    elif ad_ratio >= 1.2:
        market_mood = "BULLISH"
    elif ad_ratio >= 0.8:
        market_mood = "NEUTRAL"
    elif ad_ratio >= 0.5:
        market_mood = "BEARISH"
    else:
        market_mood = "STRONG_BEARISH"

    return {
        "status": "success",
        "total_tracked": total_stocks,
        "top_gainers": top_gainers,
        "top_losers": top_losers,
        "volume_spikes": volume_spikes[:10],
        "sector_heatmap": sector_heatmap,
        "market_breadth": {
            "advancing": advancing,
            "declining": declining,
            "unchanged": unchanged,
            "ad_ratio": ad_ratio,
            "market_mood": market_mood,
        },
    }
