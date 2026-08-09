import os

def generate_veteran_ai_memo(tech: dict, fund: dict, plan: dict, symbol: str) -> dict:
    """
    Generates a 50-Year Veteran Stock Market Analyst Report & Investment Memo.
    """
    symbol_clean = symbol.replace(".NS", "").replace(".BO", "").upper()
    curr_p = tech.get("current_price", 0)
    change_pct = tech.get("change_pct", 0)
    conviction = plan.get("conviction_stars", 3)
    stars_str = "★" * conviction + "☆" * (5 - conviction)
    
    action = plan.get("action", "HOLD").replace("_", " ")
    horizon = plan.get("horizon", "N/A")
    category = fund.get("category", "EQUITY").replace("_", " ")
    
    # Fundamental Highlights
    roe = fund.get("roe_pct", "N/A")
    pe = fund.get("pe_ratio", "N/A")
    de = fund.get("debt_to_equity", "N/A")
    quality_score = fund.get("quality_score", 50)
    
    # Technical Highlights
    rsi = tech.get("rsi", 50)
    supertrend = tech.get("supertrend_direction", "NEUTRAL")
    trend_status = tech.get("trend_status", "NEUTRAL").replace("_", " ")
    vol_ratio = tech.get("volume_ratio", 1.0)
    vcp_active = tech.get("vcp", {}).get("is_vcp", False)
    
    # Trade Setup
    entry = plan.get("entry_zone", "N/A")
    sl = plan.get("stop_loss", "N/A")
    sl_pct = plan.get("stop_loss_pct", "N/A")
    t1 = plan.get("target_1", "N/A")
    t1_pct = plan.get("target_1_pct", "N/A")
    t2 = plan.get("target_2", "N/A")
    t2_pct = plan.get("target_2_pct", "N/A")
    t3 = plan.get("target_3", "N/A")
    t3_pct = plan.get("target_3_pct", "N/A")
    rr = plan.get("risk_reward_ratio", "1:3")

    # Construct the Veteran Memo Sections
    thesis_bullets = []
    if quality_score >= 70:
        thesis_bullets.append(f"High Financial Quality: Strong Return on Equity (ROE: {roe}%) with disciplined balance sheet leverage (D/E: {de}).")
    if vcp_active:
        thesis_bullets.append("Mark Minervini Volatility Contraction Pattern (VCP) detected: Supply drying up near key breakout pivot.")
    if vol_ratio > 1.5:
        thesis_bullets.append(f"Institutional Footprint: Volume expansion of {vol_ratio}x over 20-day moving average indicates active smart-money accumulation.")
    if rsi >= 50 and rsi <= 68:
        thesis_bullets.append(f"Healthy Momentum: RSI at {rsi} sits in the prime bullish acceleration zone without being overextended.")

    if not thesis_bullets:
        thesis_bullets.append("Consolidation setup: Stock is forming a structural base while awaiting fundamental or earnings catalyst.")

    risks = [
        f"Broader Indian market volatility or sharp FII net outflow in {fund.get('sector', 'this sector')}.",
        f"Breach of key ATR stop loss level at ₹{sl} ({sl_pct}) invalidates the bullish thesis.",
        f"P/E ratio of {pe} requires sustained top-line growth to maintain current valuation multiples."
    ]

    verdict_summary = (
        f"{symbol_clean} exhibits a {stars_str} ({plan.get('veteran_score')}/100) conviction setup. "
        f"The 50-year veteran consensus recommends {action} with a horizon of {horizon}. "
        f"Risk-to-Reward ratio is highly favorable at {rr} with initial Target 1 at ₹{t1} ({t1_pct}) "
        f"and Target 2 at ₹{t2} ({t2_pct}). Dynamic stop loss is anchored at ₹{sl} ({sl_pct})."
    )

    return {
        "ticker": symbol_clean,
        "action": action,
        "conviction_stars": stars_str,
        "conviction_score": plan.get("veteran_score"),
        "category": category,
        "verdict_summary": verdict_summary,
        "investment_thesis": thesis_bullets,
        "key_risks": risks,
        "trade_blueprint": {
            "entry_zone": entry,
            "stop_loss": f"₹{sl} ({sl_pct})",
            "target_1": f"₹{t1} ({t1_pct})",
            "target_2": f"₹{t2} ({t2_pct})",
            "target_3": f"₹{t3} ({t3_pct})",
            "risk_reward": rr,
            "horizon": horizon
        }
    }
