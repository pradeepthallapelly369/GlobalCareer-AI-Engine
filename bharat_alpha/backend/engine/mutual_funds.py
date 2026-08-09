"""
BharatAlpha Invest — Mutual Funds Analytics Engine
Provides category-wise institutional screening of top Indian Mutual Funds.
"""

MUTUAL_FUNDS_DATABASE = [
    # ── Flexi Cap & Multicap Funds ─────────────────────────────
    {
        "id": "ppfc",
        "name": "Parag Parikh Flexi Cap Fund - Direct Plan",
        "amc": "PPFAS Mutual Fund",
        "category": "Flexi Cap",
        "risk_level": "Very High Risk",
        "nav": 84.52,
        "cagr_1y": 28.4,
        "cagr_3y": 21.8,
        "cagr_5y": 24.5,
        "expense_ratio": 0.58,
        "aum_cr": 72450.0,
        "min_sip": 1000,
        "stars": 5,
        "thesis": "Quality-oriented global diversification with low portfolio turnover and high alpha retention."
    },
    {
        "id": "hdfc_flexi",
        "name": "HDFC Flexi Cap Fund - Direct Plan",
        "amc": "HDFC Mutual Fund",
        "category": "Flexi Cap",
        "risk_level": "Very High Risk",
        "nav": 1820.40,
        "cagr_1y": 34.2,
        "cagr_3y": 26.1,
        "cagr_5y": 21.9,
        "expense_ratio": 0.76,
        "aum_cr": 58900.0,
        "min_sip": 1000,
        "stars": 5,
        "thesis": "Value + Growth GARP strategy focusing on financial recovery and industrial expansion."
    },
    
    # ── Large Cap Funds ─────────────────────────────────────────
    {
        "id": "nippon_large",
        "name": "Nippon India Large Cap Fund - Direct Plan",
        "amc": "Nippon India Mutual Fund",
        "category": "Large Cap",
        "risk_level": "Very High Risk",
        "nav": 89.15,
        "cagr_1y": 32.8,
        "cagr_3y": 23.4,
        "cagr_5y": 20.1,
        "expense_ratio": 0.72,
        "aum_cr": 31200.0,
        "min_sip": 100,
        "stars": 5,
        "thesis": "Focuses on top 100 market leaders with high return on capital and steady cash flows."
    },
    {
        "id": "icici_bluechip",
        "name": "ICICI Prudential Bluechip Fund - Direct Plan",
        "amc": "ICICI Prudential Mutual Fund",
        "category": "Large Cap",
        "risk_level": "Very High Risk",
        "nav": 112.30,
        "cagr_1y": 27.5,
        "cagr_3y": 20.2,
        "cagr_5y": 18.9,
        "expense_ratio": 0.88,
        "aum_cr": 53400.0,
        "min_sip": 100,
        "stars": 4,
        "thesis": "Consistent bluechip compounder with conservative downside protection strategy."
    },

    # ── Mid Cap Funds ──────────────────────────────────────────
    {
        "id": "hdfc_midcap",
        "name": "HDFC Mid-Cap Opportunities Fund - Direct Plan",
        "amc": "HDFC Mutual Fund",
        "category": "Mid Cap",
        "risk_level": "Very High Risk",
        "nav": 178.60,
        "cagr_1y": 42.1,
        "cagr_3y": 29.8,
        "cagr_5y": 26.4,
        "expense_ratio": 0.73,
        "aum_cr": 71800.0,
        "min_sip": 1000,
        "stars": 5,
        "thesis": "Identifies high-growth mid-sized businesses with competitive moat and market share expansion."
    },
    {
        "id": "motilal_midcap",
        "name": "Motilal Oswal Midcap Fund - Direct Plan",
        "amc": "Motilal Oswal Mutual Fund",
        "category": "Mid Cap",
        "risk_level": "Very High Risk",
        "nav": 108.90,
        "cagr_1y": 56.4,
        "cagr_3y": 35.2,
        "cagr_5y": 28.7,
        "expense_ratio": 0.65,
        "aum_cr": 16400.0,
        "min_sip": 500,
        "stars": 5,
        "thesis": "High conviction focused mid-cap portfolio operating on 'QGLP' (Quality, Growth, Longevity, Price) principle."
    },

    # ── Small Cap Funds ─────────────────────────────────────────
    {
        "id": "nippon_small",
        "name": "Nippon India Small Cap Fund - Direct Plan",
        "amc": "Nippon India Mutual Fund",
        "category": "Small Cap",
        "risk_level": "Very High Risk",
        "nav": 184.20,
        "cagr_1y": 45.6,
        "cagr_3y": 33.1,
        "cagr_5y": 32.8,
        "expense_ratio": 0.67,
        "aum_cr": 56200.0,
        "min_sip": 100,
        "stars": 5,
        "thesis": "Massive bottom-up stock selection matrix across 150+ high growth emerging small-cap companies."
    },
    {
        "id": "quant_small",
        "name": "Quant Small Cap Fund - Direct Plan",
        "amc": "Quant Mutual Fund",
        "category": "Small Cap",
        "risk_level": "Very High Risk",
        "nav": 268.40,
        "cagr_1y": 48.9,
        "cagr_3y": 34.7,
        "cagr_5y": 37.2,
        "expense_ratio": 0.64,
        "aum_cr": 24100.0,
        "min_sip": 1000,
        "stars": 5,
        "thesis": "Proprietary VLRT (Value, Liquidity, Risk, Timing) quantitative algorithmic allocation framework."
    },

    # ── Index Funds ─────────────────────────────────────────────
    {
        "id": "uti_nifty50",
        "name": "UTI Nifty 50 Index Fund - Direct Plan",
        "amc": "UTI Mutual Fund",
        "category": "Index Fund",
        "risk_level": "Very High Risk",
        "nav": 174.10,
        "cagr_1y": 24.8,
        "cagr_3y": 16.9,
        "cagr_5y": 16.2,
        "expense_ratio": 0.05,
        "aum_cr": 19800.0,
        "min_sip": 500,
        "stars": 5,
        "thesis": "Lowest tracking error and minimal expense ratio (0.05%) tracking India's top 50 industrial titans."
    },
    {
        "id": "navi_nifty50",
        "name": "Navi Nifty 50 Index Fund - Direct Plan",
        "amc": "Navi Mutual Fund",
        "category": "Index Fund",
        "risk_level": "Very High Risk",
        "nav": 15.80,
        "cagr_1y": 24.7,
        "cagr_3y": 16.8,
        "cagr_5y": 16.1,
        "expense_ratio": 0.06,
        "aum_cr": 2100.0,
        "min_sip": 100,
        "stars": 4,
        "thesis": "Ultra-low cost index tracking for passive long-term wealth accumulation."
    },

    # ── Hybrid & Debt Funds ────────────────────────────────────
    {
        "id": "icici_equity_debt",
        "name": "ICICI Prudential Equity & Debt Fund - Direct Plan",
        "amc": "ICICI Prudential Mutual Fund",
        "category": "Aggressive Hybrid",
        "risk_level": "High Risk",
        "nav": 365.20,
        "cagr_1y": 31.4,
        "cagr_3y": 23.8,
        "cagr_5y": 21.3,
        "expense_ratio": 0.77,
        "aum_cr": 37600.0,
        "min_sip": 100,
        "stars": 5,
        "thesis": "Dynamic asset allocation balancing 65-80% equity with high quality G-Sec bonds."
    },
    {
        "id": "hdfc_short_debt",
        "name": "HDFC Short Term Debt Fund - Direct Plan",
        "amc": "HDFC Mutual Fund",
        "category": "Debt",
        "risk_level": "Moderate Risk",
        "nav": 30.15,
        "cagr_1y": 7.4,
        "cagr_3y": 6.8,
        "cagr_5y": 6.9,
        "expense_ratio": 0.35,
        "aum_cr": 14200.0,
        "min_sip": 1000,
        "stars": 4,
        "thesis": "High credit quality SOV/AAA rated debt instruments with 1-3 year duration for stable capital preservation."
    }
]

def get_mutual_funds_screener(category: str = "ALL"):
    """
    Returns mutual funds filtered by category or top ranked across all categories.
    """
    if category.upper() == "ALL":
        funds = MUTUAL_FUNDS_DATABASE
    else:
        funds = [f for f in MUTUAL_FUNDS_DATABASE if category.upper() in f['category'].upper()]
        
    # Sort by 3Y CAGR descending
    sorted_funds = sorted(funds, key=lambda x: x['cagr_3y'], reverse=True)
    
    categories = sorted(list(set(f['category'] for f in MUTUAL_FUNDS_DATABASE)))
    
    return {
        "total_funds": len(sorted_funds),
        "available_categories": ["ALL"] + categories,
        "funds": sorted_funds
    }
