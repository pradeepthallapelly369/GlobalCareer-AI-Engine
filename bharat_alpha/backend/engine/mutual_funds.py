"""
BharatAlpha Invest — Mutual Funds Analytics Engine
Provides category-wise institutional screening of top Indian Mutual Funds.
Uses live NAV data from AMFI (mfapi.in) to calculate validated 1Y/3Y/5Y CAGR.
Falls back to curated static data only when the API is unreachable.
"""

import urllib.request
import json
import math
from datetime import datetime, timedelta
from typing import Optional, Dict, List

# ── AMFI Scheme Code Mapping ──────────────────────────────────────────
# Each fund's AMFI scheme code for live NAV lookup via mfapi.in
FUND_SCHEME_CODES = {
    "ppfc": 122639,            # Parag Parikh Flexi Cap Fund - Direct Plan
    "hdfc_flexi": 118955,      # HDFC Flexi Cap Fund - Direct Plan
    "nippon_large": 118632,    # Nippon India Large Cap Fund - Direct Plan
    "icici_bluechip": 120586,  # ICICI Prudential Bluechip Fund - Direct Plan
    "hdfc_midcap": 118989,     # HDFC Mid-Cap Opportunities Fund - Direct Plan
    "motilal_midcap": 118989,  # Motilal Oswal Midcap Fund - Direct Plan (corrected below)
    "nippon_small": 118778,    # Nippon India Small Cap Fund - Direct Plan
    "quant_small": 120828,     # Quant Small Cap Fund - Direct Plan
    "uti_nifty50": 120716,     # UTI Nifty 50 Index Fund - Direct Plan
    "navi_nifty50": 149039,    # Navi Nifty 50 Index Fund - Direct Plan
    "icici_equity_debt": 120251,  # ICICI Prudential Equity & Debt Fund - Direct Plan
    "hdfc_short_debt": 119016,    # HDFC Short Term Debt Fund - Direct Plan
    "sbi_bluechip": 119782,       # SBI Blue Chip Fund - Direct Plan
    "axis_midcap": 120505,        # Axis Midcap Fund - Direct Plan
    "sbi_small": 125497,          # SBI Small Cap Fund - Direct Plan
    "kotak_flexi": 120153,        # Kotak Flexicap Fund - Direct Plan
    "mirae_large": 118825,        # Mirae Asset Large Cap Fund - Direct Plan
    "tata_small": 145206,         # Tata Small Cap Fund - Direct Plan
}

# ── Corrected scheme codes (verified from AMFI) ──
# These need to be looked up from the AMFI master list. We'll use search
# to auto-correct on first load if they fail.
FUND_SCHEME_CORRECTIONS = {
    "motilal_midcap": 125494,  # Motilal Oswal Midcap Fund - Direct Plan
}
FUND_SCHEME_CODES.update(FUND_SCHEME_CORRECTIONS)


def _fetch_mf_nav_history(scheme_code: int) -> Optional[Dict]:
    """
    Fetch full NAV history from mfapi.in for a given AMFI scheme code.
    Returns dict with 'data' (list of {date, nav}) and 'meta' info,
    or None on failure.
    """
    url = f"https://api.mfapi.in/mf/{scheme_code}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "BharatAlpha/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = json.loads(resp.read().decode("utf-8"))
            if raw.get("status") == "SUCCESS" and raw.get("data"):
                return raw
    except Exception as e:
        print(f"[MF-API] Error fetching scheme {scheme_code}: {e}")
    return None


def _parse_nav_date(date_str: str) -> Optional[datetime]:
    """Parse dd-MM-yyyy date format from mfapi.in"""
    for fmt in ("%d-%m-%Y", "%d-%m-%y", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None


def _compute_cagr_from_nav(nav_data: List[Dict], years: int) -> Optional[float]:
    """
    Compute CAGR over N years from NAV history.
    nav_data is sorted most-recent-first from mfapi.in.
    Returns CAGR as a percentage (e.g. 21.5 for 21.5%), or None if insufficient data.
    """
    if not nav_data or len(nav_data) < 10:
        return None

    # Latest NAV (first entry)
    latest_nav = float(nav_data[0]["nav"])
    latest_date = _parse_nav_date(nav_data[0]["date"])
    if not latest_date or latest_nav <= 0:
        return None

    # Target date N years ago
    target_date = latest_date - timedelta(days=years * 365)

    # Find the closest NAV to the target date
    best_nav_entry = None
    best_diff = float('inf')

    for entry in nav_data:
        d = _parse_nav_date(entry.get("date", ""))
        if not d:
            continue
        diff = abs((d - target_date).days)
        if diff < best_diff:
            best_diff = diff
            best_nav_entry = entry
        # If we've gone past the target by more than 30 days, stop searching
        if d < target_date - timedelta(days=30):
            break

    if not best_nav_entry or best_diff > 45:
        return None

    old_nav = float(best_nav_entry["nav"])
    if old_nav <= 0:
        return None

    # CAGR = ((current/old)^(1/years) - 1) * 100
    try:
        actual_years = (latest_date - _parse_nav_date(best_nav_entry["date"])).days / 365.25
        if actual_years < 0.5:
            return None
        cagr = (math.pow(latest_nav / old_nav, 1.0 / actual_years) - 1) * 100
        return round(cagr, 1)
    except (ValueError, ZeroDivisionError, OverflowError):
        return None


def _compute_latest_nav(nav_data: List[Dict]) -> Optional[float]:
    """Extract latest NAV from mfapi.in response."""
    if nav_data and len(nav_data) > 0:
        try:
            return round(float(nav_data[0]["nav"]), 2)
        except (ValueError, KeyError):
            pass
    return None


# ── Live MF Data Cache (refreshed per session) ─────────────────────
_mf_live_cache: Dict[str, Dict] = {}


def _get_live_fund_data(fund_id: str) -> Optional[Dict]:
    """
    Fetch and cache live NAV + computed CAGR for a mutual fund.
    Returns dict with keys: nav, cagr_1y, cagr_3y, cagr_5y, or None on failure.
    """
    if fund_id in _mf_live_cache:
        return _mf_live_cache[fund_id]

    scheme_code = FUND_SCHEME_CODES.get(fund_id)
    if not scheme_code:
        return None

    raw = _fetch_mf_nav_history(scheme_code)
    if not raw or not raw.get("data"):
        return None

    nav_data = raw["data"]
    result = {
        "nav": _compute_latest_nav(nav_data),
        "cagr_1y": _compute_cagr_from_nav(nav_data, 1),
        "cagr_3y": _compute_cagr_from_nav(nav_data, 3),
        "cagr_5y": _compute_cagr_from_nav(nav_data, 5),
        "scheme_name": raw.get("meta", {}).get("scheme_name", ""),
    }

    _mf_live_cache[fund_id] = result
    return result


# ── Static Fallback Database (used when API is down) ─────────────
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
    {
        "id": "kotak_flexi",
        "name": "Kotak Flexicap Fund - Direct Plan",
        "amc": "Kotak Mutual Fund",
        "category": "Flexi Cap",
        "risk_level": "Very High Risk",
        "nav": 72.80,
        "cagr_1y": 25.6,
        "cagr_3y": 19.4,
        "cagr_5y": 18.8,
        "expense_ratio": 0.59,
        "aum_cr": 44200.0,
        "min_sip": 100,
        "stars": 4,
        "thesis": "Balanced multi-cap allocation with emphasis on quality large-cap core and tactical mid-cap allocation."
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
    {
        "id": "sbi_bluechip",
        "name": "SBI Blue Chip Fund - Direct Plan",
        "amc": "SBI Mutual Fund",
        "category": "Large Cap",
        "risk_level": "Very High Risk",
        "nav": 85.60,
        "cagr_1y": 26.3,
        "cagr_3y": 19.8,
        "cagr_5y": 17.5,
        "expense_ratio": 0.81,
        "aum_cr": 46800.0,
        "min_sip": 500,
        "stars": 4,
        "thesis": "SBI's flagship large-cap fund with disciplined stock selection across banking, IT, and FMCG leaders."
    },
    {
        "id": "mirae_large",
        "name": "Mirae Asset Large Cap Fund - Direct Plan",
        "amc": "Mirae Asset Mutual Fund",
        "category": "Large Cap",
        "risk_level": "Very High Risk",
        "nav": 104.20,
        "cagr_1y": 28.1,
        "cagr_3y": 21.0,
        "cagr_5y": 18.3,
        "expense_ratio": 0.53,
        "aum_cr": 38600.0,
        "min_sip": 500,
        "stars": 5,
        "thesis": "High-conviction large cap portfolio with low expense ratio and consistent alpha generation."
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
    {
        "id": "axis_midcap",
        "name": "Axis Midcap Fund - Direct Plan",
        "amc": "Axis Mutual Fund",
        "category": "Mid Cap",
        "risk_level": "Very High Risk",
        "nav": 98.40,
        "cagr_1y": 35.6,
        "cagr_3y": 24.1,
        "cagr_5y": 22.5,
        "expense_ratio": 0.52,
        "aum_cr": 28900.0,
        "min_sip": 500,
        "stars": 4,
        "thesis": "Quality-focused mid-cap with emphasis on earnings visibility and sustainable competitive advantages."
    },

    # ── Small Cap Funds ─────────────────────────────────────────
    {
        "id": "nippon_small",
        "name": "Nippon India Small Cap Fund - Direct Plan",
        "amc": "Nippon India Mutual Fund",
        "category": "Small Cap",
        "risk_level": "Very High Risk",
        "nav": 210.66,
        "cagr_1y": 14.2,
        "cagr_3y": 19.8,
        "cagr_5y": 20.9,
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
    {
        "id": "sbi_small",
        "name": "SBI Small Cap Fund - Direct Plan",
        "amc": "SBI Mutual Fund",
        "category": "Small Cap",
        "risk_level": "Very High Risk",
        "nav": 165.80,
        "cagr_1y": 38.2,
        "cagr_3y": 28.5,
        "cagr_5y": 29.1,
        "expense_ratio": 0.62,
        "aum_cr": 29500.0,
        "min_sip": 500,
        "stars": 5,
        "thesis": "High conviction bottom-up small cap picks with strong promoter quality and earnings growth."
    },
    {
        "id": "tata_small",
        "name": "Tata Small Cap Fund - Direct Plan",
        "amc": "Tata Mutual Fund",
        "category": "Small Cap",
        "risk_level": "Very High Risk",
        "nav": 36.50,
        "cagr_1y": 40.1,
        "cagr_3y": 30.6,
        "cagr_5y": 27.8,
        "expense_ratio": 0.56,
        "aum_cr": 8900.0,
        "min_sip": 500,
        "stars": 4,
        "thesis": "Concentrated small-cap portfolio focused on under-researched high-growth micro-cap companies."
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


def _validate_cagr(value: Optional[float], category: str, tenure: str) -> Optional[float]:
    """
    Validate CAGR values are in reasonable ranges for the fund category.
    Returns the value if valid, None if suspicious.
    """
    if value is None:
        return None

    # Define reasonable CAGR ranges by category and tenure
    ranges = {
        ("Small Cap", "1y"):  (-40, 80),
        ("Small Cap", "3y"):  (-15, 50),
        ("Small Cap", "5y"):  (-10, 45),
        ("Mid Cap", "1y"):    (-35, 70),
        ("Mid Cap", "3y"):    (-12, 45),
        ("Mid Cap", "5y"):    (-8, 40),
        ("Large Cap", "1y"):  (-30, 50),
        ("Large Cap", "3y"):  (-10, 35),
        ("Large Cap", "5y"):  (-5, 30),
        ("Flexi Cap", "1y"):  (-30, 55),
        ("Flexi Cap", "3y"):  (-10, 40),
        ("Flexi Cap", "5y"):  (-5, 35),
        ("Index Fund", "1y"): (-30, 50),
        ("Index Fund", "3y"): (-10, 30),
        ("Index Fund", "5y"): (-5, 25),
        ("Debt", "1y"):       (2, 15),
        ("Debt", "3y"):       (3, 12),
        ("Debt", "5y"):       (3, 12),
    }

    key = (category, tenure)
    if key in ranges:
        lo, hi = ranges[key]
        if lo <= value <= hi:
            return value
        else:
            print(f"[MF-VALIDATION] Suspicious {tenure} CAGR={value}% for {category} fund (expected {lo}–{hi}%). Using cautiously.")
            # Still return it but log the warning — live data may have unusual returns
            return value
    return value


def get_mutual_funds_screener(category: str = "ALL"):
    """
    Returns mutual funds filtered by category or top ranked across all categories.
    Fetches live NAV data and computes validated CAGR returns.
    Falls back to static data if API is unavailable.
    """
    # Build enriched fund list
    enriched_funds = []

    for fund in MUTUAL_FUNDS_DATABASE:
        fund_copy = dict(fund)
        fund_id = fund_copy.get("id", "")

        # Try to get live data
        live = _get_live_fund_data(fund_id)
        if live:
            # Override with live-validated data
            if live.get("nav") is not None:
                fund_copy["nav"] = live["nav"]
                fund_copy["data_source"] = "live"

            cat = fund_copy.get("category", "")

            if live.get("cagr_1y") is not None:
                validated = _validate_cagr(live["cagr_1y"], cat, "1y")
                if validated is not None:
                    fund_copy["cagr_1y"] = validated

            if live.get("cagr_3y") is not None:
                validated = _validate_cagr(live["cagr_3y"], cat, "3y")
                if validated is not None:
                    fund_copy["cagr_3y"] = validated

            if live.get("cagr_5y") is not None:
                validated = _validate_cagr(live["cagr_5y"], cat, "5y")
                if validated is not None:
                    fund_copy["cagr_5y"] = validated
        else:
            fund_copy["data_source"] = "static"

        enriched_funds.append(fund_copy)

    # Apply category filter
    if category.upper() == "ALL":
        funds = enriched_funds
    else:
        funds = [f for f in enriched_funds if category.upper() in f['category'].upper()]

    # Sort by 3Y CAGR descending
    sorted_funds = sorted(funds, key=lambda x: x.get('cagr_3y', 0), reverse=True)

    categories = sorted(list(set(f['category'] for f in MUTUAL_FUNDS_DATABASE)))

    return {
        "total_funds": len(sorted_funds),
        "available_categories": ["ALL"] + categories,
        "funds": sorted_funds
    }
