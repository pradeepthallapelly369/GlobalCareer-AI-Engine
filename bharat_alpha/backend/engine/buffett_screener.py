"""
BharatAlpha AI — Warren Buffett Multibagger Stock Screener
============================================================
Scans 100+ NSE stocks and classifies them into investment categories:
  - MULTIBAGGER_CANDIDATE
  - COFFEE_CAN_COMPOUNDER
  - GARP_BUY (Growth at Reasonable Price)
  - DEEP_VALUE_BARGAIN
  - HIGH_GROWTH_ROCKET
  - DIVIDEND_ARISTOCRAT
  - AVOID_OVERVALUED

Outputs ranked by composite Buffett Conviction Score.
"""

import yfinance as yf
import pandas as pd
from backend.engine.technicals import analyze_stock_technicals
from backend.engine.fundamentals import analyze_stock_fundamentals
from backend.engine.trade_planner import generate_trade_plan

# ─── EXPANDED NSE STOCK UNIVERSE ────────────────────────────────────────
# Curated 100+ high-quality Indian stocks across all sectors
BUFFETT_NSE_UNIVERSE = [
    # Large Cap — Nifty 50 Core
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS",
    "BHARTIARTL.NS", "ITC.NS", "SBIN.NS", "LT.NS", "BAJFINANCE.NS",
    "HCLTECH.NS", "KOTAKBANK.NS", "TITAN.NS", "SUNPHARMA.NS", "AXISBANK.NS",
    "MARUTI.NS", "WIPRO.NS", "ULTRACEMCO.NS", "NESTLEIND.NS", "TATASTEEL.NS",
    "POWERGRID.NS", "NTPC.NS", "ONGC.NS", "COALINDIA.NS", "ADANIENT.NS",
    "ADANIPORTS.NS", "BAJAJFINSV.NS", "TECHM.NS", "HINDALCO.NS", "JSWSTEEL.NS",
    "HINDUNILVR.NS", "ASIANPAINT.NS", "DRREDDY.NS", "CIPLA.NS", "EICHERMOT.NS",
    "TATAMOTORS.NS", "M&M.NS", "DIVISLAB.NS", "APOLLOHOSP.NS", "BPCL.NS",
    "TATACONSUM.NS", "HEROMOTOCO.NS", "INDUSINDBK.NS", "GRASIM.NS",
    "BRITANNIA.NS",

    # Mid Cap — Nifty Next 50 / Quality Mid Caps
    "DIXON.NS", "TRENT.NS", "BEL.NS", "HAL.NS", "POLYCAB.NS",
    "PERSISTENT.NS", "COFORGE.NS", "MPHASIS.NS", "LTIM.NS",
    "PIIND.NS", "ASTRAL.NS", "ATUL.NS", "DEEPAKNTR.NS", "NAVINFLUOR.NS",
    "SOLARINDS.NS", "CLEAN.NS", "AFFLE.NS",
    "TATAELXSI.NS", "KPITTECH.NS", "ROUTE.NS", "ZOMATO.NS",
    "DMART.NS", "NAUKRI.NS", "PAYTM.NS",
    "MUTHOOTFIN.NS", "CHOLAFIN.NS", "BAJAJHLDNG.NS",
    "MARICO.NS", "DABUR.NS", "COLPAL.NS", "PIDILITIND.NS", "GODREJCP.NS",

    # Small Cap — High Growth / Multibagger Potential
    "KAYNES.NS", "VBL.NS", "CAMPUS.NS", "BIKAJI.NS",
    "HAPPSTMNDS.NS", "TANLA.NS", "PPLPHARMA.NS",
    "CAMS.NS", "CDSL.NS", "ANGELONE.NS",
    "SYNGENE.NS", "LALPATHLAB.NS", "METROPOLIS.NS",
    "IDFCFIRSTB.NS", "FEDERALBNK.NS", "RBLBANK.NS",
    "JKCEMENT.NS", "RAMCOCEM.NS",
    "CROMPTON.NS", "VOLTAS.NS", "BLUESTARCO.NS",
    "SONACOMS.NS", "MAZAGON.NS", "COCHINSHIP.NS",
    "IRFC.NS", "RVNL.NS", "IRCTC.NS",
    "JINDALSTEL.NS", "RATNAMANI.NS",
]


def run_buffett_scan(max_stocks=None) -> dict:
    """
    Runs the full Warren Buffett / Rakesh Jhunjhunwala style stock screener.
    Returns stocks classified and ranked by Buffett Conviction Score.
    """
    tickers = BUFFETT_NSE_UNIVERSE
    if max_stocks:
        tickers = tickers[:max_stocks]

    all_results = []
    category_buckets = {
        "MULTIBAGGER_CANDIDATE": [],
        "COFFEE_CAN_COMPOUNDER": [],
        "GARP_BUY": [],
        "DEEP_VALUE_BARGAIN": [],
        "HIGH_GROWTH_ROCKET": [],
        "DIVIDEND_ARISTOCRAT": [],
        "MODERATE_QUALITY_CYCLICAL": [],
        "AVOID_OVERVALUED": [],
    }

    scanned = 0
    errors = 0

    for ticker_sym in tickers:
        try:
            stock = yf.Ticker(ticker_sym)
            df = stock.history(period="1y").dropna(subset=["Close"])
            if df.empty or len(df) < 30:
                errors += 1
                continue

            tech = analyze_stock_technicals(df)
            fund = analyze_stock_fundamentals(ticker_sym)
            plan = generate_trade_plan(tech, fund, ticker_sym)

            clean_ticker = ticker_sym.replace(".NS", "").replace(".BO", "")

            company_name = stock.info.get("shortName") or stock.info.get("longName") or f"{clean_ticker} LTD"

            record = {
                "ticker": clean_ticker,
                "company_name": company_name,
                "current_price": tech.get("current_price"),
                "change_pct": tech.get("change_pct"),
                "sector": fund.get("sector"),
                "industry": fund.get("industry"),
                "cap_class": fund.get("cap_class", "MID_CAP"),
                "market_cap_cr": fund.get("market_cap_cr"),

                # Buffett Scores
                "buffett_score": fund.get("buffett_score", 0),
                "moat_score": fund.get("moat_score", 0),
                "growth_score": fund.get("growth_score", 0),
                "balance_sheet_score": fund.get("balance_sheet_score", 0),
                "valuation_score": fund.get("valuation_score", 0),
                "dividend_score": fund.get("dividend_score", 0),
                "technical_score": tech.get("technical_score", 0),

                # Key Metrics Snapshot
                "roe_pct": fund.get("roe_pct"),
                "roce_pct": fund.get("roce_pct"),
                "de_ratio": fund.get("debt_to_equity"),
                "pe_ratio": fund.get("pe_ratio"),
                "peg_ratio": fund.get("peg_ratio"),
                "profit_margin_pct": fund.get("profit_margin_pct"),
                "revenue_growth_pct": fund.get("revenue_growth_pct"),
                "earnings_growth_pct": fund.get("earnings_growth_pct"),
                "fcf_yield_pct": fund.get("fcf_yield_pct"),
                "graham_intrinsic_value": fund.get("graham_intrinsic_value"),
                "margin_of_safety_pct": fund.get("margin_of_safety_pct"),
                "dividend_yield_pct": fund.get("dividend_yield_pct"),

                # Trade Plan
                "category": fund.get("category"),
                "action": plan.get("action"),
                "veteran_score": plan.get("veteran_score"),
                "conviction_stars": plan.get("conviction_stars"),
                "entry_zone": plan.get("entry_zone"),
                "stop_loss": plan.get("stop_loss"),
                "target_1": plan.get("target_1"),
                "target_1_pct": plan.get("target_1_pct"),
                "target_2": plan.get("target_2"),
                "risk_reward": plan.get("risk_reward_ratio"),
                "horizon": plan.get("horizon"),
                "trend_status": tech.get("trend_status"),
                "rsi": tech.get("rsi"),
            }

            all_results.append(record)
            cat = fund.get("category", "MODERATE_QUALITY_CYCLICAL")
            if cat in category_buckets:
                category_buckets[cat].append(record)
            else:
                category_buckets["MODERATE_QUALITY_CYCLICAL"].append(record)

            scanned += 1

        except Exception as e:
            print(f"Buffett scan error for {ticker_sym}: {e}")
            errors += 1
            continue

    # Sort all results by Buffett Score descending
    all_results.sort(key=lambda x: x.get("buffett_score", 0), reverse=True)

    # Sort each category bucket
    for cat in category_buckets:
        category_buckets[cat].sort(key=lambda x: x.get("buffett_score", 0), reverse=True)

    # Top picks summary
    top_multibaggers = category_buckets.get("MULTIBAGGER_CANDIDATE", [])[:10]
    top_compounders = category_buckets.get("COFFEE_CAN_COMPOUNDER", [])[:10]
    top_value = category_buckets.get("DEEP_VALUE_BARGAIN", [])[:10]
    top_growth = category_buckets.get("HIGH_GROWTH_ROCKET", [])[:10]
    top_dividend = category_buckets.get("DIVIDEND_ARISTOCRAT", [])[:10]
    avoid_list = category_buckets.get("AVOID_OVERVALUED", [])[:10]

    return {
        "total_scanned": scanned,
        "total_errors": errors,
        "universe_size": len(tickers),
        "all_ranked": all_results[:50],  # Top 50 by Buffett Score
        "multibagger_candidates": top_multibaggers,
        "coffee_can_compounders": top_compounders,
        "deep_value_bargains": top_value,
        "high_growth_rockets": top_growth,
        "dividend_aristocrats": top_dividend,
        "avoid_overvalued": avoid_list,
        "category_counts": {cat: len(stocks) for cat, stocks in category_buckets.items()}
    }
