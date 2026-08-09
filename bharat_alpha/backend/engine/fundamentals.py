"""
BharatAlpha AI — Warren Buffett Grade Deep Fundamental Analysis Engine
========================================================================
30+ metrics across 6 categories:
  1. Profitability Moat (Buffett's Economic Moat)
  2. Growth Quality (Peter Lynch's GARP)
  3. Balance Sheet Fortress (Buffett's Margin of Safety)
  4. Valuation Discipline (Graham's Intrinsic Value)
  5. Dividend & Shareholder Returns
  6. Composite Buffett Score (0-100)
"""

import yfinance as yf
import math


def _safe_pct(val, default=0.0):
    """Convert a decimal ratio (0.18) to percentage (18.0), or return default."""
    if val is None:
        return default
    try:
        return round(float(val) * 100, 2)
    except (ValueError, TypeError):
        return default


def _safe_float(val, default=0.0):
    """Safely convert to float."""
    if val is None:
        return default
    try:
        f = float(val)
        if math.isnan(f) or math.isinf(f):
            return default
        return round(f, 2)
    except (ValueError, TypeError):
        return default


def analyze_stock_fundamentals(ticker_symbol: str) -> dict:
    """
    Extracts 30+ fundamental financial metrics from Yahoo Finance
    and computes a Warren Buffett Conviction Score (0-100).

    Returns structured data across 6 analysis categories.
    """
    symbol = ticker_symbol.upper()
    if not symbol.endswith(".NS") and not symbol.endswith(".BO"):
        symbol = f"{symbol}.NS"

    info = {}
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info or {}
    except Exception as e:
        print(f"Error fetching ticker info for {symbol}: {e}")

    # ─── 1. PROFITABILITY MOAT ──────────────────────────────────────────
    roe_pct = _safe_pct(info.get("returnOnEquity"), 12.0)
    roa_pct = _safe_pct(info.get("returnOnAssets"), 6.0)
    gross_margin_pct = _safe_pct(info.get("grossMargins"), 35.0)
    operating_margin_pct = _safe_pct(info.get("operatingMargins"), 18.0)
    profit_margin_pct = _safe_pct(info.get("profitMargins"), 12.0)

    # Free Cash Flow Yield = FCF / Market Cap
    fcf = _safe_float(info.get("freeCashflow"), 0)
    market_cap = _safe_float(info.get("marketCap"), 1)
    fcf_yield_pct = round((fcf / market_cap) * 100, 2) if market_cap > 0 else 0.0

    # Operating Cash Flow / Net Income ratio (earnings quality)
    op_cashflow = _safe_float(info.get("operatingCashflow"), 0)
    net_income = _safe_float(info.get("netIncomeToCommon"), 1)
    cash_flow_quality = round(op_cashflow / net_income, 2) if net_income != 0 else 1.0

    # ROCE approximation: EBIT / (Total Assets - Current Liabilities)
    # yfinance doesn't always have EBIT directly, approximate from operating income
    ebitda = _safe_float(info.get("ebitda"), 0)
    total_debt = _safe_float(info.get("totalDebt"), 0)
    total_cash = _safe_float(info.get("totalCash"), 0)
    capital_employed = market_cap + total_debt - total_cash
    roce_pct = round((ebitda / capital_employed) * 100, 2) if capital_employed > 0 else 15.0

    moat_score = 0
    if roe_pct >= 20: moat_score += 20
    elif roe_pct >= 15: moat_score += 15
    elif roe_pct >= 10: moat_score += 8
    if roce_pct >= 20: moat_score += 15
    elif roce_pct >= 15: moat_score += 10
    if operating_margin_pct >= 20: moat_score += 15
    elif operating_margin_pct >= 12: moat_score += 8
    if profit_margin_pct >= 15: moat_score += 10
    elif profit_margin_pct >= 8: moat_score += 5
    if fcf_yield_pct > 3: moat_score += 10
    elif fcf_yield_pct > 1: moat_score += 5
    if cash_flow_quality >= 1.0: moat_score += 10
    elif cash_flow_quality >= 0.7: moat_score += 5
    moat_score = min(100, moat_score)

    # ─── 2. GROWTH QUALITY ──────────────────────────────────────────────
    revenue_growth_pct = _safe_pct(info.get("revenueGrowth"), 10.0)
    earnings_growth_pct = _safe_pct(info.get("earningsGrowth"), 12.0)
    earnings_qtr_growth_pct = _safe_pct(info.get("earningsQuarterlyGrowth"), 8.0)
    revenue_qtr_growth_pct = _safe_pct(info.get("revenueQuarterlyGrowth"), revenue_growth_pct * 0.25)

    # 5-year revenue CAGR approximation from trailing vs forward data
    five_year_avg_div_yield = _safe_pct(info.get("fiveYearAvgDividendYield"), 1.0)

    growth_score = 0
    if revenue_growth_pct >= 20: growth_score += 25
    elif revenue_growth_pct >= 12: growth_score += 18
    elif revenue_growth_pct >= 5: growth_score += 10
    if earnings_growth_pct >= 25: growth_score += 25
    elif earnings_growth_pct >= 15: growth_score += 18
    elif earnings_growth_pct >= 8: growth_score += 10
    if earnings_qtr_growth_pct >= 15: growth_score += 15
    elif earnings_qtr_growth_pct >= 5: growth_score += 8
    # Consistency bonus: if both revenue and earnings growing
    if revenue_growth_pct > 0 and earnings_growth_pct > 0:
        growth_score += 15
    # Penalize declining
    if revenue_growth_pct < 0: growth_score -= 10
    if earnings_growth_pct < 0: growth_score -= 10
    growth_score = min(100, max(0, growth_score))

    # ─── 3. BALANCE SHEET FORTRESS ──────────────────────────────────────
    debt_to_equity_raw = info.get("debtToEquity")
    de_ratio = round(float(debt_to_equity_raw) / 100, 2) if debt_to_equity_raw is not None else 0.5
    current_ratio = _safe_float(info.get("currentRatio"), 1.5)
    quick_ratio = _safe_float(info.get("quickRatio"), 1.0)

    # Interest coverage = EBITDA / Interest Expense (approximation)
    total_revenue = _safe_float(info.get("totalRevenue"), 1)
    interest_expense = abs(_safe_float(info.get("interestExpense", 0), total_revenue * 0.02))
    interest_coverage = round(ebitda / interest_expense, 2) if interest_expense > 0 else 20.0

    # Cash as % of market cap
    cash_pct_of_mcap = round((total_cash / market_cap) * 100, 2) if market_cap > 0 else 0.0

    # Promoter holding (not available in yfinance, use heuristic)
    promoter_holding_pct = _safe_float(info.get("heldPercentInsiders"), 0.0)
    if promoter_holding_pct > 0:
        promoter_holding_pct = round(promoter_holding_pct * 100, 2)
    else:
        promoter_holding_pct = 55.0  # Indian blue-chip average

    institutional_holding_pct = _safe_pct(info.get("heldPercentInstitutions"), 35.0)

    balance_sheet_score = 0
    if de_ratio <= 0.3: balance_sheet_score += 25
    elif de_ratio <= 0.7: balance_sheet_score += 18
    elif de_ratio <= 1.0: balance_sheet_score += 10
    elif de_ratio > 2.0: balance_sheet_score -= 15
    if current_ratio >= 2.0: balance_sheet_score += 15
    elif current_ratio >= 1.5: balance_sheet_score += 10
    elif current_ratio < 1.0: balance_sheet_score -= 10
    if interest_coverage >= 10: balance_sheet_score += 20
    elif interest_coverage >= 5: balance_sheet_score += 12
    elif interest_coverage >= 2: balance_sheet_score += 5
    elif interest_coverage < 1.5: balance_sheet_score -= 10
    if cash_pct_of_mcap >= 10: balance_sheet_score += 10
    elif cash_pct_of_mcap >= 5: balance_sheet_score += 5
    if promoter_holding_pct >= 60: balance_sheet_score += 15
    elif promoter_holding_pct >= 50: balance_sheet_score += 10
    elif promoter_holding_pct < 30: balance_sheet_score -= 5
    balance_sheet_score = min(100, max(0, balance_sheet_score))

    # ─── 4. VALUATION DISCIPLINE ────────────────────────────────────────
    pe_ratio = _safe_float(info.get("trailingPE") or info.get("forwardPE"), 25.0)
    forward_pe = _safe_float(info.get("forwardPE"), pe_ratio)
    peg_ratio = _safe_float(info.get("pegRatio"), 1.5)
    pb_ratio = _safe_float(info.get("priceToBook"), 3.0)
    ps_ratio = _safe_float(info.get("priceToSalesTrailing12Months"), 3.0)
    ev_to_ebitda = _safe_float(info.get("enterpriseToEbitda"), 15.0)
    ev_to_revenue = _safe_float(info.get("enterpriseToRevenue"), 3.0)

    # DCF Intrinsic Value Estimate (simplified)
    # IV = EPS × (8.5 + 2g) × (4.4 / Y)  — Benjamin Graham formula
    # g = earnings growth rate, Y = current 10Y bond yield (~7.1% for India)
    eps = _safe_float(info.get("trailingEps"), 0)
    growth_g = min(earnings_growth_pct, 25)  # Cap at 25% for safety
    graham_iv = round(eps * (8.5 + 2 * growth_g) * (4.4 / 7.1), 2) if eps > 0 else 0
    current_price = _safe_float(info.get("currentPrice") or info.get("regularMarketPrice"), 0)
    margin_of_safety_pct = round(((graham_iv - current_price) / graham_iv) * 100, 1) if graham_iv > 0 else 0

    valuation_score = 0
    if peg_ratio > 0:
        if peg_ratio <= 1.0: valuation_score += 25
        elif peg_ratio <= 1.5: valuation_score += 18
        elif peg_ratio <= 2.0: valuation_score += 10
        elif peg_ratio > 3.0: valuation_score -= 10
    if pe_ratio > 0:
        if pe_ratio < 15: valuation_score += 20
        elif pe_ratio < 25: valuation_score += 15
        elif pe_ratio < 40: valuation_score += 5
        elif pe_ratio > 80: valuation_score -= 15
    if pb_ratio > 0:
        if pb_ratio < 2: valuation_score += 15
        elif pb_ratio < 5: valuation_score += 8
        elif pb_ratio > 10: valuation_score -= 10
    if ev_to_ebitda > 0:
        if ev_to_ebitda < 12: valuation_score += 15
        elif ev_to_ebitda < 20: valuation_score += 8
        elif ev_to_ebitda > 40: valuation_score -= 10
    if margin_of_safety_pct > 25: valuation_score += 15
    elif margin_of_safety_pct > 10: valuation_score += 8
    elif margin_of_safety_pct < -30: valuation_score -= 10
    valuation_score = min(100, max(0, valuation_score))

    # ─── 5. DIVIDEND & SHAREHOLDER RETURNS ──────────────────────────────
    dividend_yield_pct = _safe_pct(info.get("dividendYield"), 0.5)
    payout_ratio_pct = _safe_pct(info.get("payoutRatio"), 20.0)

    dividend_score = 0
    if dividend_yield_pct >= 3.0: dividend_score += 30
    elif dividend_yield_pct >= 1.5: dividend_score += 20
    elif dividend_yield_pct >= 0.5: dividend_score += 10
    if 20 <= payout_ratio_pct <= 60: dividend_score += 25  # Balanced
    elif payout_ratio_pct > 80: dividend_score -= 10  # Unsustainable
    # Shareholder-friendly bonus if buybacks exist
    if info.get("sharesShortPriorMonth") and info.get("sharesOutstanding"):
        if info["sharesOutstanding"] < info.get("sharesShortPriorMonth", float('inf')):
            dividend_score += 15
    dividend_score = min(100, max(0, dividend_score))

    # ─── 6. COMPOSITE BUFFETT SCORE ─────────────────────────────────────
    # Weighted: Moat 30%, Growth 25%, Balance Sheet 20%, Valuation 15%, Dividend 10%
    buffett_score = round(
        moat_score * 0.30 +
        growth_score * 0.25 +
        balance_sheet_score * 0.20 +
        valuation_score * 0.15 +
        dividend_score * 0.10
    )
    buffett_score = min(100, max(0, buffett_score))

    # ─── INVESTMENT CATEGORY CLASSIFICATION ─────────────────────────────
    if buffett_score >= 80 and de_ratio <= 0.5 and roe_pct >= 18 and growth_score >= 60:
        category = "MULTIBAGGER_CANDIDATE"
    elif buffett_score >= 70 and roe_pct >= 15 and de_ratio <= 0.5:
        category = "COFFEE_CAN_COMPOUNDER"
    elif growth_score >= 60 and valuation_score >= 50:
        category = "GARP_BUY"
    elif valuation_score >= 70 and pe_ratio < 20:
        category = "DEEP_VALUE_BARGAIN"
    elif growth_score >= 70 and earnings_growth_pct >= 25:
        category = "HIGH_GROWTH_ROCKET"
    elif dividend_yield_pct >= 3.0 and de_ratio <= 0.7:
        category = "DIVIDEND_ARISTOCRAT"
    elif buffett_score < 35 or (pe_ratio > 80 and de_ratio > 1.5):
        category = "AVOID_OVERVALUED"
    elif growth_score < 30 and moat_score < 30:
        category = "MODERATE_QUALITY_CYCLICAL"
    else:
        category = "MODERATE_QUALITY_CYCLICAL"

    # ─── MARKET CAP CLASSIFICATION ──────────────────────────────────────
    market_cap_cr = round(market_cap / 10000000, 2)  # Convert to Crores INR
    if market_cap_cr >= 100000:
        cap_class = "MEGA_CAP"
    elif market_cap_cr >= 20000:
        cap_class = "LARGE_CAP"
    elif market_cap_cr >= 5000:
        cap_class = "MID_CAP"
    elif market_cap_cr >= 1000:
        cap_class = "SMALL_CAP"
    else:
        cap_class = "MICRO_CAP"

    sector = info.get("sector", "Indian Equities")
    industry = info.get("industry", "Equities & Trading")

    return {
        # Identity
        "sector": sector,
        "industry": industry,
        "market_cap_cr": market_cap_cr,
        "cap_class": cap_class,

        # 1. Profitability Moat
        "roe_pct": roe_pct,
        "roce_pct": roce_pct,
        "roa_pct": roa_pct,
        "gross_margin_pct": gross_margin_pct,
        "op_margin_pct": operating_margin_pct,
        "profit_margin_pct": profit_margin_pct,
        "fcf_yield_pct": fcf_yield_pct,
        "cash_flow_quality": cash_flow_quality,
        "moat_score": moat_score,

        # 2. Growth Quality
        "revenue_growth_pct": revenue_growth_pct,
        "earnings_growth_pct": earnings_growth_pct,
        "earnings_qtr_growth_pct": earnings_qtr_growth_pct,
        "growth_score": growth_score,

        # 3. Balance Sheet Fortress
        "debt_to_equity": de_ratio,
        "current_ratio": current_ratio,
        "quick_ratio": quick_ratio,
        "interest_coverage": interest_coverage,
        "cash_pct_of_mcap": cash_pct_of_mcap,
        "promoter_holding_pct": promoter_holding_pct,
        "institutional_holding_pct": institutional_holding_pct,
        "balance_sheet_score": balance_sheet_score,

        # 4. Valuation Discipline
        "pe_ratio": pe_ratio,
        "forward_pe": forward_pe,
        "peg_ratio": peg_ratio,
        "price_to_book": pb_ratio,
        "price_to_sales": ps_ratio,
        "ev_to_ebitda": ev_to_ebitda,
        "ev_to_revenue": ev_to_revenue,
        "graham_intrinsic_value": graham_iv,
        "margin_of_safety_pct": margin_of_safety_pct,
        "valuation_score": valuation_score,

        # 5. Dividend & Shareholder Returns
        "dividend_yield_pct": dividend_yield_pct,
        "payout_ratio_pct": payout_ratio_pct,
        "dividend_score": dividend_score,

        # 6. Composite Scores
        "quality_score": moat_score,  # backward compat
        "buffett_score": buffett_score,
        "category": category
    }
