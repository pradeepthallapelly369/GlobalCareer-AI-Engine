"""Default stock universe for the notebook.

Nifty 50 constituents (NSE, `.NS` suffix) plus a sector map and a
mapping of NSE symbols to their US-listed ADRs. The ADR map is used
by the data router to query Alpha Vantage for fundamentals (AV free
tier doesn't cover NSE-only tickers, so we use AV for the ADR subset
and fall back to yfinance for the rest).
"""
from __future__ import annotations

from typing import Optional


# Nifty 50 — current constituents (NSE).
NIFTY_50: list[str] = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
    "HINDUNILVR.NS", "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "KOTAKBANK.NS",
    "LT.NS", "HCLTECH.NS", "AXISBANK.NS", "ASIANPAINT.NS", "MARUTI.NS",
    "SUNPHARMA.NS", "TITAN.NS", "BAJFINANCE.NS", "WIPRO.NS", "ONGC.NS",
    "NTPC.NS", "POWERGRID.NS", "M&M.NS", "TATASTEEL.NS", "ULTRACEMCO.NS",
    "TECHM.NS", "INDUSINDBK.NS", "NESTLEIND.NS", "BAJAJFINSV.NS", "DRREDDY.NS",
    "CIPLA.NS", "GRASIM.NS", "BRITANNIA.NS", "EICHERMOT.NS", "DIVISLAB.NS",
    "HEROMOTOCO.NS", "BAJAJ-AUTO.NS", "HINDALCO.NS", "APOLLOHOSP.NS",
    "SBILIFE.NS", "HDFCLIFE.NS", "TATACONSUM.NS", "ADANIENT.NS",
    "ADANIPORTS.NS", "LTIM.NS", "BPCL.NS", "COALINDIA.NS", "IOC.NS",
    "JSWSTEEL.NS", "SHRIRAMFIN.NS",
]


SECTOR_MAP: dict[str, str] = {
    # IT
    "TCS.NS": "IT", "INFY.NS": "IT", "HCLTECH.NS": "IT", "WIPRO.NS": "IT",
    "TECHM.NS": "IT", "LTIM.NS": "IT",
    # Banking
    "HDFCBANK.NS": "Banking", "ICICIBANK.NS": "Banking", "SBIN.NS": "Banking",
    "KOTAKBANK.NS": "Banking", "AXISBANK.NS": "Banking", "INDUSINDBK.NS": "Banking",
    "SBILIFE.NS": "Insurance", "HDFCLIFE.NS": "Insurance", "SHRIRAMFIN.NS": "NBFC",
    # Energy
    "RELIANCE.NS": "Energy", "ONGC.NS": "Energy", "BPCL.NS": "Energy",
    "IOC.NS": "Energy", "COALINDIA.NS": "Energy",
    # Consumer
    "HINDUNILVR.NS": "FMCG", "ITC.NS": "FMCG", "NESTLEIND.NS": "FMCG",
    "BRITANNIA.NS": "FMCG", "TATACONSUM.NS": "FMCG",
    # Auto
    "MARUTI.NS": "Auto", "M&M.NS": "Auto", "TATAMOTORS.NS": "Auto",
    "EICHERMOT.NS": "Auto", "HEROMOTOCO.NS": "Auto", "BAJAJ-AUTO.NS": "Auto",
    # Pharma
    "SUNPHARMA.NS": "Pharma", "DRREDDY.NS": "Pharma", "CIPLA.NS": "Pharma",
    "DIVISLAB.NS": "Pharma",
    # Industrials / Capital goods
    "LT.NS": "Capital Goods", "BHARTIARTL.NS": "Telecom",
    "TITAN.NS": "Consumer Durables", "ASIANPAINT.NS": "Paints",
    "BAJFINANCE.NS": "NBFC", "BAJAJFINSV.NS": "NBFC",
    "GRASIM.NS": "Cement", "ULTRACEMCO.NS": "Cement",
    "TATASTEEL.NS": "Metals", "HINDALCO.NS": "Metals", "JSWSTEEL.NS": "Metals",
    "POWERGRID.NS": "Power", "NTPC.NS": "Power",
    "APOLLOHOSP.NS": "Healthcare",
    "ADANIENT.NS": "Conglomerate", "ADANIPORTS.NS": "Infrastructure",
}


# Mapping of NSE symbols → US-listed ADR tickers recognized by Alpha Vantage.
# Only well-known, actively-traded ADRs are listed; everything else falls
# back to yfinance.
ADR_MAPPING: dict[str, str] = {
    "INFY.NS": "INFY",        # Infosys
    "HDFCBANK.NS": "HDB",     # HDFC Bank
    "ICICIBANK.NS": "IBN",    # ICICI Bank
    "WIPRO.NS": "WIT",        # Wipro
    "DRREDDY.NS": "RDY",      # Dr. Reddy's
    "TATAMOTORS.NS": "TTM",   # Tata Motors
    "VEDL.NS": "VEDL",        # Vedanta (not in Nifty 50 but illustrative)
    "HINDALCO.NS": "HINDALCO",# Not a current ADR — included for completeness
}


def get_default_universe() -> list[str]:
    """Return the default Nifty 50 universe as a fresh list."""
    return list(NIFTY_50)


def to_alphavantage_symbol(sym: str) -> Optional[str]:
    """Return the Alpha Vantage ticker for an NSE symbol, or None."""
    return ADR_MAPPING.get(sym)


def sector_of(sym: str) -> str:
    """Return the sector label for a symbol, defaulting to 'Other'."""
    return SECTOR_MAP.get(sym, "Other")


def mini_universe() -> list[str]:
    """A 5-symbol smoke-test universe used by the notebook's quick-validate path."""
    return ["INFY.NS", "TCS.NS", "HDFCBANK.NS", "RELIANCE.NS", "ITC.NS"]
