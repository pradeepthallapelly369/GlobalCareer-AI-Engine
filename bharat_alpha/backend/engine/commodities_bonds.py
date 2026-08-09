"""
BharatAlpha Invest — Commodities & Fixed Income Analytics Engine
Tracks Gold (MCX/SGB), Silver, RBI G-Secs, Corporate Bonds, and Bank FDs.
"""

def get_commodities_data():
    """
    Returns live rates, historical returns, and Sovereign Gold Bonds (SGB) data.
    """
    return {
        "gold_24k_10g": {
            "price_rs": 72450.00,
            "change_rs": 320.00,
            "change_pct": 0.44,
            "return_1y_pct": 21.5,
            "return_3y_pct": 14.8,
            "return_5y_pct": 13.9,
            "unit": "per 10g (24K 999 Purity)"
        },
        "gold_22k_10g": {
            "price_rs": 66410.00,
            "change_rs": 290.00,
            "change_pct": 0.44,
            "unit": "per 10g (22K Standard Gold)"
        },
        "silver_1kg": {
            "price_rs": 84200.00,
            "change_rs": -450.00,
            "change_pct": -0.53,
            "return_1y_pct": 18.9,
            "return_3y_pct": 16.2,
            "return_5y_pct": 15.1,
            "unit": "per 1kg (999 Purity Fine Silver)"
        },
        "sgb_tranches": [
            {
                "series": "SGB 2023-24 Series IV",
                "issue_price_rs": 6263,
                "current_market_price_rs": 7180,
                "coupon_rate_pct": 2.50,
                "maturity_date": "2032-02-21",
                "cagr_projected_pct": 14.2,
                "tax_status": "Exempt from Capital Gains Tax at maturity"
            },
            {
                "series": "SGB 2022-23 Series III",
                "issue_price_rs": 5409,
                "current_market_price_rs": 7210,
                "coupon_rate_pct": 2.50,
                "maturity_date": "2030-12-27",
                "cagr_projected_pct": 15.8,
                "tax_status": "Exempt from Capital Gains Tax at maturity"
            },
            {
                "series": "SGB 2021-22 Series IX",
                "issue_price_rs": 4786,
                "current_market_price_rs": 7195,
                "coupon_rate_pct": 2.50,
                "maturity_date": "2030-03-08",
                "cagr_projected_pct": 16.9,
                "tax_status": "Exempt from Capital Gains Tax at maturity"
            }
        ]
    }

def get_bonds_and_fixed_income():
    """
    Returns yield metrics for RBI Government Securities, Corporate AAA Bonds, and Bank FDs.
    """
    return {
        "g_sec_10y_yield_pct": 6.94,
        "rbi_repo_rate_pct": 6.50,
        "inflation_rate_cpi_pct": 4.85,
        "real_yield_pct": 2.09,
        "g_secs": [
            {"name": "7.18% GS 2033 (10-Year Benchmark)", "yield_pct": 6.94, "rating": "SOV", "duration_yrs": 10},
            {"name": "7.06% GS 2028 (5-Year Sovereign)", "yield_pct": 6.88, "rating": "SOV", "duration_yrs": 5},
            {"name": "91-Day Treasury Bill (T-Bill)", "yield_pct": 6.68, "rating": "SOV", "duration_yrs": 0.25},
            {"name": "364-Day Treasury Bill (T-Bill)", "yield_pct": 6.75, "rating": "SOV", "duration_yrs": 1.0}
        ],
        "corporate_bonds": [
            {"issuer": "L&T Finance Ltd (AAA)", "coupon_pct": 8.15, "yield_to_maturity_pct": 8.05, "tenure": "3 Years", "rating": "CRISIL AAA"},
            {"issuer": "HDFC Bank Ltd Bonds (AAA)", "coupon_pct": 7.75, "yield_to_maturity_pct": 7.68, "tenure": "5 Years", "rating": "CARE AAA"},
            {"issuer": "REC Ltd (PSU Bond)", "coupon_pct": 7.60, "yield_to_maturity_pct": 7.52, "tenure": "5 Years", "rating": "CRISIL AAA"},
            {"issuer": "PFC Ltd (PSU Bond)", "coupon_pct": 7.62, "yield_to_maturity_pct": 7.55, "tenure": "5 Years", "rating": "ICRA AAA"}
        ],
        "bank_fds": [
            {"bank": "SBI (State Bank of India)", "regular_rate_pct": 6.80, "senior_rate_pct": 7.30, "best_tenure": "400 Days (Amrit Kalash)"},
            {"bank": "HDFC Bank", "regular_rate_pct": 7.25, "senior_rate_pct": 7.75, "best_tenure": "35 Months"},
            {"bank": "ICICI Bank", "regular_rate_pct": 7.20, "senior_rate_pct": 7.75, "best_tenure": "15 Months to 2 Years"},
            {"bank": "Suryoday Small Finance Bank", "regular_rate_pct": 8.65, "senior_rate_pct": 9.15, "best_tenure": "2 Years 2 Months"}
        ]
    }
