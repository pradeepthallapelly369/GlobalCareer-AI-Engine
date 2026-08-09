"""
BharatAlpha Invest — Wealth Advisor Engine
Calculates SIP projections and institutional asset allocation profiles.
"""

def calculate_sip_growth(monthly_sip: float, tenure_years: int, expected_return_pct: float, stepup_pct: float = 0.0):
    """
    Computes SIP wealth growth with optional annual step-up %.
    """
    months = tenure_years * 12
    monthly_rate = (expected_return_pct / 100.0) / 12.0
    
    current_sip = monthly_sip
    total_invested = 0.0
    corpus = 0.0
    
    yearly_breakdown = []
    
    for m in range(1, months + 1):
        corpus = (corpus + current_sip) * (1 + monthly_rate)
        total_invested += current_sip
        
        # Apply step up every 12 months
        if m % 12 == 0:
            year_num = m // 12
            wealth_gain = corpus - total_invested
            yearly_breakdown.append({
                "year": year_num,
                "monthly_sip": round(current_sip, 2),
                "total_invested": round(total_invested, 2),
                "wealth_gain": round(wealth_gain, 2),
                "future_value": round(corpus, 2)
            })
            if stepup_pct > 0:
                current_sip = current_sip * (1 + (stepup_pct / 100.0))
                
    wealth_gain = corpus - total_invested
    
    return {
        "monthly_sip_start": monthly_sip,
        "tenure_years": tenure_years,
        "expected_cagr_pct": expected_return_pct,
        "annual_stepup_pct": stepup_pct,
        "total_invested_rs": round(total_invested, 2),
        "wealth_gained_rs": round(wealth_gain, 2),
        "final_corpus_rs": round(corpus, 2),
        "wealth_multiplier": round(corpus / total_invested, 2) if total_invested > 0 else 1.0,
        "yearly_schedule": yearly_breakdown
    }


def generate_asset_allocation(age: int, risk_profile: str = "MODERATE"):
    """
    Generates recommended asset allocation profile based on age & risk tolerance.
    """
    profile = risk_profile.upper().strip()
    
    # Rule of thumb base: Equity % = 100 - Age (adjusted by risk profile)
    base_equity = max(20, min(85, 100 - age))
    
    if profile == "CONSERVATIVE":
        equity_pct = max(15, base_equity - 20)
        debt_pct = 60
        gold_pct = 15
        cash_pct = 100 - equity_pct - debt_pct - gold_pct
    elif profile == "AGGRESSIVE":
        equity_pct = min(85, base_equity + 15)
        debt_pct = 15
        gold_pct = 10
        cash_pct = 100 - equity_pct - debt_pct - gold_pct
    elif profile == "VERY_AGGRESSIVE":
        equity_pct = min(90, base_equity + 25)
        debt_pct = 5
        gold_pct = 5
        cash_pct = 0
    else: # MODERATE
        equity_pct = base_equity
        debt_pct = max(15, 80 - equity_pct)
        gold_pct = 10
        cash_pct = 100 - equity_pct - debt_pct - gold_pct
        
    return {
        "user_age": age,
        "risk_profile": profile,
        "allocation_percentages": {
            "equity_pct": equity_pct,
            "debt_bonds_pct": debt_pct,
            "gold_commodities_pct": gold_pct,
            "liquid_cash_pct": cash_pct
        },
        "recommended_instruments": [
            {
                "asset_class": "Equities & Stock Funds",
                "allocation_pct": equity_pct,
                "sub_split": "Large Cap (40%) | Mid Cap (30%) | Small/Flexi Cap (30%)",
                "action": "Invest via monthly SIPs in top-rated Flexi-cap & Nifty Index funds."
            },
            {
                "asset_class": "Debt Securities & Fixed Income",
                "allocation_pct": debt_pct,
                "sub_split": "G-Sec Bonds (50%) | Corporate AAA NCDs (30%) | Bank FDs (20%)",
                "action": "Lock in high 10Y G-Sec yields & AAA bonds for downside capital protection."
            },
            {
                "asset_class": "Gold & Commodities",
                "allocation_pct": gold_pct,
                "sub_split": "Sovereign Gold Bonds / Gold ETFs (100%)",
                "action": "Accumulate SGBs for 2.5% tax-free annual coupon + gold appreciation."
            },
            {
                "asset_class": "Liquid Emergency Cash",
                "allocation_pct": cash_pct,
                "sub_split": "Liquid Mutual Funds / High Yield Savings (100%)",
                "action": "Keep 6 months of living expenses in instant-redemption liquid funds."
            }
        ]
    }
