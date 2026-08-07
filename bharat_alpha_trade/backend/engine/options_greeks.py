"""
Black-Scholes Options Greeks Engine for Indian Index & Stock Options.
Calculates Delta, Gamma, Theta, Vega, Rho and solves for Implied Volatility.
"""
import math
import numpy as np
from scipy.stats import norm
from scipy.optimize import brentq

# RBI repo rate as risk-free rate (approx)
RISK_FREE_RATE = 0.065  # 6.5% annual

def d1(S, K, T, r, sigma):
    """Calculate d1 component of Black-Scholes formula."""
    if T <= 0 or sigma <= 0:
        return 0.0
    return (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))

def d2(S, K, T, r, sigma):
    """Calculate d2 component of Black-Scholes formula."""
    return d1(S, K, T, r, sigma) - sigma * math.sqrt(T)

def bs_call_price(S, K, T, r, sigma):
    """Black-Scholes Call option price."""
    if T <= 0:
        return max(S - K, 0)
    _d1 = d1(S, K, T, r, sigma)
    _d2 = d2(S, K, T, r, sigma)
    return S * norm.cdf(_d1) - K * math.exp(-r * T) * norm.cdf(_d2)

def bs_put_price(S, K, T, r, sigma):
    """Black-Scholes Put option price."""
    if T <= 0:
        return max(K - S, 0)
    _d1 = d1(S, K, T, r, sigma)
    _d2 = d2(S, K, T, r, sigma)
    return K * math.exp(-r * T) * norm.cdf(-_d2) - S * norm.cdf(-_d1)

def calculate_delta(S, K, T, r, sigma, option_type="CE"):
    """Delta: Rate of change of option price w.r.t. underlying price."""
    if T <= 0:
        if option_type == "CE":
            return 1.0 if S > K else 0.0
        else:
            return -1.0 if S < K else 0.0
    _d1 = d1(S, K, T, r, sigma)
    if option_type == "CE":
        return round(norm.cdf(_d1), 4)
    else:
        return round(norm.cdf(_d1) - 1, 4)

def calculate_gamma(S, K, T, r, sigma):
    """Gamma: Rate of change of delta w.r.t. underlying price."""
    if T <= 0 or sigma <= 0:
        return 0.0
    _d1 = d1(S, K, T, r, sigma)
    return round(norm.pdf(_d1) / (S * sigma * math.sqrt(T)), 6)

def calculate_theta(S, K, T, r, sigma, option_type="CE"):
    """Theta: Time decay per day (negative for long options)."""
    if T <= 0 or sigma <= 0:
        return 0.0
    _d1 = d1(S, K, T, r, sigma)
    _d2 = d2(S, K, T, r, sigma)
    common = -(S * norm.pdf(_d1) * sigma) / (2 * math.sqrt(T))
    if option_type == "CE":
        theta = common - r * K * math.exp(-r * T) * norm.cdf(_d2)
    else:
        theta = common + r * K * math.exp(-r * T) * norm.cdf(-_d2)
    return round(theta / 365, 2)  # Per day

def calculate_vega(S, K, T, r, sigma):
    """Vega: Sensitivity to 1% change in volatility."""
    if T <= 0 or sigma <= 0:
        return 0.0
    _d1 = d1(S, K, T, r, sigma)
    return round(S * norm.pdf(_d1) * math.sqrt(T) / 100, 2)

def calculate_rho(S, K, T, r, sigma, option_type="CE"):
    """Rho: Sensitivity to 1% change in risk-free rate."""
    if T <= 0:
        return 0.0
    _d2 = d2(S, K, T, r, sigma)
    if option_type == "CE":
        return round(K * T * math.exp(-r * T) * norm.cdf(_d2) / 100, 2)
    else:
        return round(-K * T * math.exp(-r * T) * norm.cdf(-_d2) / 100, 2)

def calculate_all_greeks(S, K, T, r, sigma, option_type="CE"):
    """Calculate all Greeks for a single option."""
    return {
        "delta": calculate_delta(S, K, T, r, sigma, option_type),
        "gamma": calculate_gamma(S, K, T, r, sigma),
        "theta": calculate_theta(S, K, T, r, sigma, option_type),
        "vega": calculate_vega(S, K, T, r, sigma),
        "rho": calculate_rho(S, K, T, r, sigma, option_type),
        "theoretical_price": round(
            bs_call_price(S, K, T, r, sigma) if option_type == "CE"
            else bs_put_price(S, K, T, r, sigma), 2
        )
    }

def solve_implied_volatility(market_price, S, K, T, r, option_type="CE"):
    """
    Solve for Implied Volatility using Brent's method.
    Returns IV as a decimal (e.g. 0.18 = 18%).
    """
    if T <= 0 or market_price <= 0:
        return 0.0

    intrinsic = max(S - K, 0) if option_type == "CE" else max(K - S, 0)
    if market_price < intrinsic:
        return 0.0

    def objective(sigma):
        if option_type == "CE":
            return bs_call_price(S, K, T, r, sigma) - market_price
        else:
            return bs_put_price(S, K, T, r, sigma) - market_price

    try:
        iv = brentq(objective, 0.001, 5.0, xtol=1e-6)
        return round(iv, 4)
    except (ValueError, RuntimeError):
        return 0.0

def days_to_expiry_fraction(days):
    """Convert calendar days to expiry into year fraction."""
    return max(days, 0) / 365.0

def enrich_option_chain_with_greeks(chain_data, spot_price, days_to_expiry, r=RISK_FREE_RATE):
    """
    Takes raw option chain data and enriches each strike with Greeks.
    chain_data: list of dicts with keys: strike, ce_ltp, pe_ltp, ce_oi, pe_oi, ce_volume, pe_volume
    """
    T = days_to_expiry_fraction(days_to_expiry)
    enriched = []

    for row in chain_data:
        strike = row.get("strike", 0)
        ce_ltp = row.get("ce_ltp", 0) or 0
        pe_ltp = row.get("pe_ltp", 0) or 0

        # Solve IV
        ce_iv = solve_implied_volatility(ce_ltp, spot_price, strike, T, r, "CE") if ce_ltp > 0 else 0
        pe_iv = solve_implied_volatility(pe_ltp, spot_price, strike, T, r, "PE") if pe_ltp > 0 else 0

        # Calculate Greeks
        ce_greeks = calculate_all_greeks(spot_price, strike, T, r, ce_iv if ce_iv > 0 else 0.15, "CE")
        pe_greeks = calculate_all_greeks(spot_price, strike, T, r, pe_iv if pe_iv > 0 else 0.15, "PE")

        # Moneyness classification
        diff_pct = abs(spot_price - strike) / spot_price * 100
        if diff_pct < 0.5:
            moneyness = "ATM"
        elif strike < spot_price:
            moneyness = "ITM_CE" if True else "OTM_PE"
        else:
            moneyness = "OTM_CE"

        enriched.append({
            "strike": strike,
            "moneyness": moneyness,
            "ce_ltp": ce_ltp,
            "ce_iv": round(ce_iv * 100, 1),
            "ce_oi": row.get("ce_oi", 0),
            "ce_volume": row.get("ce_volume", 0),
            "ce_delta": ce_greeks["delta"],
            "ce_gamma": ce_greeks["gamma"],
            "ce_theta": ce_greeks["theta"],
            "ce_vega": ce_greeks["vega"],
            "pe_ltp": pe_ltp,
            "pe_iv": round(pe_iv * 100, 1),
            "pe_oi": row.get("pe_oi", 0),
            "pe_volume": row.get("pe_volume", 0),
            "pe_delta": pe_greeks["delta"],
            "pe_gamma": pe_greeks["gamma"],
            "pe_theta": pe_greeks["theta"],
            "pe_vega": pe_greeks["vega"],
        })

    return enriched
