import yfinance as yf
import pandas as pd
from backend.engine.technicals import analyze_stock_technicals
from backend.engine.fundamentals import analyze_stock_fundamentals
from backend.engine.trade_planner import generate_trade_plan

DEFAULT_NSE_UNIVERSE = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS",
    "DIXON.NS", "TATAELXSI.NS", "LT.NS", "SBIN.NS", "BAJFINANCE.NS",
    "SUNPHARMA.NS", "BHARTIARTL.NS", "ITC.NS", "TRENT.NS", "BEL.NS",
    "HAL.NS", "POLYCAB.NS", "VBL.NS", "KAYNES.NS", "TATASTEEL.NS",
    "TATAMOTORS.NS", "M&M.NS", "DIVISLAB.NS", "APOLLOHOSP.NS", "BPCL.NS",
    "TATACONSUM.NS", "HEROMOTOCO.NS", "INDUSINDBK.NS", "GRASIM.NS", "BRITANNIA.NS",
    "TATAPOWER.NS", "JIOFIN.NS", "ZOMATO.NS", "PERSISTENT.NS", "COFORGE.NS",
    "TITAN.NS", "WIPRO.NS", "ULTRACEMCO.NS", "NESTLEIND.NS", "POWERGRID.NS"
]

def run_screener_scan(tickers=None) -> dict:
    """
    Executes full quantitative screening scan across NSE universe.
    Separates picks into Long-Term Investing and Short-Term Trading recommendations.
    """
    if not tickers:
        tickers = DEFAULT_NSE_UNIVERSE

    long_term_picks = []
    short_term_picks = []
    
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period="1y").dropna(subset=['Close'])
            if df.empty or len(df) < 30:
                continue
                
            tech = analyze_stock_technicals(df)
            fund = analyze_stock_fundamentals(ticker)
            plan = generate_trade_plan(tech, fund, ticker)
            
            clean_symbol = ticker.replace(".NS", "").replace(".BO", "")
            
            record = {
                "ticker": clean_symbol,
                "full_symbol": ticker,
                "current_price": tech.get("current_price"),
                "change_pct": tech.get("change_pct"),
                "sector": fund.get("sector"),
                "quality_score": fund.get("quality_score"),
                "technical_score": tech.get("technical_score"),
                "valuation_score": fund.get("valuation_score"),
                "veteran_score": plan.get("veteran_score"),
                "conviction_stars": plan.get("conviction_stars"),
                "action": plan.get("action"),
                "horizon": plan.get("horizon"),
                "entry_zone": plan.get("entry_zone"),
                "stop_loss": plan.get("stop_loss"),
                "target_1": plan.get("target_1"),
                "target_2": plan.get("target_2"),
                "risk_reward": plan.get("risk_reward_ratio"),
                "category": fund.get("category"),
                "vcp_active": tech.get("vcp", {}).get("is_vcp", False),
                "trend_status": tech.get("trend_status")
            }
            
            # Long-Term Criteria: High Quality + Good Valuation / Coffee Can / GARP
            if fund.get("quality_score", 0) >= 60 or fund.get("category") in ["COFFEE_CAN_COMPOUNDER", "GARP_BUY", "DEEP_VALUE_BARGAIN"]:
                long_term_picks.append(record)
                
            # Short-Term Criteria: High Technical Score + Bullish Trend or VCP Breakout
            if tech.get("technical_score", 0) >= 60 or tech.get("vcp", {}).get("is_vcp"):
                short_term_picks.append(record)
                
        except Exception as e:
            print(f"Error screening {ticker}: {e}")
            continue

    # Sort long term by quality & veteran score
    long_term_picks.sort(key=lambda x: x["veteran_score"], reverse=True)
    # Sort short term by technical score
    short_term_picks.sort(key=lambda x: x["technical_score"], reverse=True)

    return {
        "total_scanned": len(tickers),
        "long_term_picks": long_term_picks[:10],
        "short_term_picks": short_term_picks[:10]
    }
