def generate_trade_plan(tech: dict, fund: dict, symbol: str) -> dict:
    """
    Formulates a complete 50-year veteran trade execution plan with exact entries,
    targets, ATR stop losses, and conviction ratings.
    """
    curr_price = tech.get("current_price", 100.0)
    atr = tech.get("atr", curr_price * 0.02)
    tech_score = tech.get("technical_score", 50)
    quality_score = fund.get("quality_score", 50)
    valuation_score = fund.get("valuation_score", 50)
    
    # Combined Veteran Score (0 - 100)
    veteran_score = round((tech_score * 0.45) + (quality_score * 0.35) + (valuation_score * 0.20))
    
    # Conviction Rating (1 to 5 Stars)
    if veteran_score >= 85: conviction = 5
    elif veteran_score >= 72: conviction = 4
    elif veteran_score >= 58: conviction = 3
    elif veteran_score >= 45: conviction = 2
    else: conviction = 1
    
    # Determine Horizon & Action
    vcp_active = tech.get("vcp", {}).get("is_vcp", False)
    trend_status = tech.get("trend_status", "BULLISH_UPTREND")
    
    if trend_status == "BULLISH_UPTREND" or vcp_active:
        action = "STRONG_BUY" if conviction >= 4 else "ACCUMULATE_ON_DIPS"
    elif trend_status == "CONSOLIDATION_SIDEWAYS" and quality_score >= 70:
        action = "ACCUMULATE_FOR_LONG_TERM"
    else:
        action = "HOLD_OR_AVOID"

    # Precise Price Levels
    ema20 = tech.get("ema20", curr_price)
    
    # Entry zone: around current price to EMA20 support
    entry_low = round(min(curr_price * 0.985, ema20), 2)
    entry_high = round(curr_price * 1.005, 2)
    
    # Stop Loss calculation (ATR risk buffer)
    stop_loss = round(entry_low - (1.8 * atr), 2)
    risk_per_share = round(entry_high - stop_loss, 2)
    if risk_per_share <= 0:
        risk_per_share = round(curr_price * 0.05, 2)
        stop_loss = round(curr_price - risk_per_share, 2)
        
    # Targets based on Risk:Reward Multipliers
    target_1 = round(entry_high + (1.5 * risk_per_share), 2)
    target_2 = round(entry_high + (3.0 * risk_per_share), 2)
    target_3 = round(entry_high + (5.5 * risk_per_share), 2)
    
    rr_ratio = round((target_2 - entry_high) / (risk_per_share if risk_per_share > 0 else 1), 2)
    
    # Target percent gains
    t1_pct = round(((target_1 - entry_high) / entry_high) * 100, 1)
    t2_pct = round(((target_2 - entry_high) / entry_high) * 100, 1)
    t3_pct = round(((target_3 - entry_high) / entry_high) * 100, 1)
    sl_pct = round(((entry_high - stop_loss) / entry_high) * 100, 1)
    
    # Suggested Investment Horizon
    if action in ["STRONG_BUY", "ACCUMULATE_ON_DIPS"] and vcp_active:
        horizon = "SWING_TRADING (2 to 6 Weeks)"
    elif fund.get("category") == "COFFEE_CAN_COMPOUNDER":
        horizon = "LONG_TERM_INVESTING (1 to 3+ Years)"
    elif fund.get("category") == "GARP_BUY":
        horizon = "POSITIONAL_TRADING (1 to 6 Months)"
    else:
        horizon = "SHORT_TERM_SWING (1 to 4 Weeks)"
        
    return {
        "action": action,
        "conviction_stars": conviction,
        "veteran_score": veteran_score,
        "horizon": horizon,
        "entry_zone": f"₹{entry_low} - ₹{entry_high}",
        "entry_high": entry_high,
        "entry_low": entry_low,
        "stop_loss": stop_loss,
        "stop_loss_pct": f"-{sl_pct}%",
        "target_1": target_1,
        "target_1_pct": f"+{t1_pct}%",
        "target_2": target_2,
        "target_2_pct": f"+{t2_pct}%",
        "target_3": target_3,
        "target_3_pct": f"+{t3_pct}%",
        "risk_reward_ratio": f"1:{rr_ratio}",
        "max_risk_per_share": risk_per_share
    }
