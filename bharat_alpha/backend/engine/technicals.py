import numpy as np
import pandas as pd

def calculate_sma(series: pd.Series, period: int) -> pd.Series:
    return series.rolling(window=period).mean()

def calculate_ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()

def calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / (loss.replace(0, 1e-9))
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50)

def calculate_macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    fast_ema = calculate_ema(series, fast)
    slow_ema = calculate_ema(series, slow)
    macd_line = fast_ema - slow_ema
    signal_line = calculate_ema(macd_line, signal)
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram

def calculate_bollinger_bands(series: pd.Series, period: int = 20, std_dev: int = 2):
    sma = calculate_sma(series, period)
    rolling_std = series.rolling(window=period).std()
    upper_band = sma + (rolling_std * std_dev)
    lower_band = sma - (rolling_std * std_dev)
    return upper_band, sma, lower_band

def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high = df['High']
    low = df['Low']
    close = df['Close']
    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    return atr.bfill() if hasattr(atr, 'bfill') else atr

def calculate_supertrend(df: pd.DataFrame, period: int = 10, multiplier: float = 3.0):
    atr = calculate_atr(df, period)
    hl2 = (df['High'] + df['Low']) / 2
    basic_ub = hl2 + (multiplier * atr)
    basic_lb = hl2 - (multiplier * atr)
    
    final_ub = pd.Series(index=df.index, dtype=float)
    final_lb = pd.Series(index=df.index, dtype=float)
    supertrend = pd.Series(index=df.index, dtype=float)
    direction = pd.Series(index=df.index, dtype=int)
    
    for i in range(len(df)):
        if i == 0:
            final_ub.iloc[i] = basic_ub.iloc[i]
            final_lb.iloc[i] = basic_lb.iloc[i]
            supertrend.iloc[i] = final_ub.iloc[i]
            direction.iloc[i] = -1
            continue
            
        # Upperband
        if basic_ub.iloc[i] < final_ub.iloc[i-1] or df['Close'].iloc[i-1] > final_ub.iloc[i-1]:
            final_ub.iloc[i] = basic_ub.iloc[i]
        else:
            final_ub.iloc[i] = final_ub.iloc[i-1]
            
        # Lowerband
        if basic_lb.iloc[i] > final_lb.iloc[i-1] or df['Close'].iloc[i-1] < final_lb.iloc[i-1]:
            final_lb.iloc[i] = basic_lb.iloc[i]
        else:
            final_lb.iloc[i] = final_lb.iloc[i-1]
            
        # Direction
        if supertrend.iloc[i-1] == final_ub.iloc[i-1]:
            if df['Close'].iloc[i] > final_ub.iloc[i]:
                supertrend.iloc[i] = final_lb.iloc[i]
                direction.iloc[i] = 1
            else:
                supertrend.iloc[i] = final_ub.iloc[i]
                direction.iloc[i] = -1
        else:
            if df['Close'].iloc[i] < final_lb.iloc[i]:
                supertrend.iloc[i] = final_ub.iloc[i]
                direction.iloc[i] = -1
            else:
                supertrend.iloc[i] = final_lb.iloc[i]
                direction.iloc[i] = 1
                
    return supertrend, direction

def detect_vcp_pattern(df: pd.DataFrame) -> dict:
    """
    Mark Minervini Volatility Contraction Pattern (VCP) Screener.
    Looks for price consolidation with narrowing high-low contractions and volume drying up.
    """
    if len(df) < 50:
        return {"is_vcp": False, "score": 0, "reason": "Insufficient historical data"}
        
    recent = df.tail(50)
    high_max = recent['High'].max()
    low_min = recent['Low'].min()
    current_close = recent['Close'].iloc[-1]
    
    # Contraction depth check (< 25-30% drop from peak)
    max_drawdown = (high_max - low_min) / high_max
    
    # 20-day vs 50-day volume check
    vol_20_sma = recent['Volume'].tail(20).mean()
    vol_50_sma = recent['Volume'].mean()
    volume_dry_up = (vol_20_sma < vol_50_sma * 0.85)
    
    # Price proximity to 52-week or 50-day high (within 15%)
    near_high = (current_close >= high_max * 0.85)
    
    # Moving Average Alignment (Close > 20 EMA > 50 EMA > 200 EMA)
    ema20 = calculate_ema(df['Close'], 20).iloc[-1]
    ema50 = calculate_ema(df['Close'], 50).iloc[-1]
    ema200 = calculate_ema(df['Close'], 200).iloc[-1] if len(df) >= 200 else ema50
    
    ma_aligned = (current_close > ema20 > ema50 > ema200)
    
    vcp_score = 0
    reasons = []
    if ma_aligned:
        vcp_score += 35
        reasons.append("Moving Averages in Perfect Stage 2 Uptrend (20>50>200 EMA)")
    if max_drawdown <= 0.25:
        vcp_score += 25
        reasons.append("Tight Contraction (<25% base depth)")
    if near_high:
        vcp_score += 20
        reasons.append("Trading within 15% of recent swing highs")
    if volume_dry_up:
        vcp_score += 20
        reasons.append("Volume drying up before breakout")

    is_vcp = bool(vcp_score >= 60)
    return {
        "is_vcp": is_vcp,
        "score": int(vcp_score),
        "reasons": reasons,
        "ma_aligned": bool(ma_aligned),
        "volume_dry_up": bool(volume_dry_up),
        "near_high": bool(near_high)
    }

def analyze_stock_technicals(df: pd.DataFrame) -> dict:
    """
    Computes a full 360-degree technical analysis payload for a stock dataframe.
    """
    if df.empty or len(df) < 20:
        return {}

    close = df['Close']
    curr_price = float(close.iloc[-1])
    prev_close = float(close.iloc[-2]) if len(close) > 1 else curr_price
    change_pct = round(((curr_price - prev_close) / prev_close) * 100, 2)
    
    ema20 = calculate_ema(close, 20)
    ema50 = calculate_ema(close, 50)
    ema200 = calculate_ema(close, 200) if len(df) >= 200 else calculate_ema(close, len(df))
    
    rsi = calculate_rsi(close, 14)
    curr_rsi = float(rsi.iloc[-1])
    
    macd, macd_sig, macd_hist = calculate_macd(close)
    curr_macd_hist = float(macd_hist.iloc[-1])
    
    bb_upper, bb_mid, bb_lower = calculate_bollinger_bands(close, 20, 2)
    atr = calculate_atr(df, 14)
    curr_atr = float(atr.iloc[-1])
    
    supertrend, st_dir = calculate_supertrend(df)
    curr_st_dir = int(st_dir.iloc[-1])
    
    # Volume dynamics
    vol_curr = float(df['Volume'].iloc[-1])
    vol_sma20 = float(df['Volume'].tail(20).mean())
    vol_ratio = round(vol_curr / (vol_sma20 if vol_sma20 > 0 else 1), 2)
    
    vcp_analysis = detect_vcp_pattern(df)
    
    # Quantitative Technical Score (0 - 100)
    tech_score = 50
    # Trend score
    if curr_price > ema20.iloc[-1]: tech_score += 10
    if curr_price > ema50.iloc[-1]: tech_score += 10
    if curr_price > ema200.iloc[-1]: tech_score += 10
    if ema20.iloc[-1] > ema50.iloc[-1]: tech_score += 5
    
    # Momentum score
    if 45 <= curr_rsi <= 68: tech_score += 10 # Ideal bullish momentum zone
    elif curr_rsi > 70: tech_score += 2 # Overbought caution
    elif curr_rsi < 30: tech_score += 5 # Oversold potential bounce
    
    if curr_macd_hist > 0: tech_score += 5
    if curr_st_dir == 1: tech_score += 10 # Supertrend Bullish
    if vol_ratio > 1.5: tech_score += 5 # Volume breakout
    
    tech_score = min(100, max(0, tech_score))
    
    # Trend status text
    if curr_price > ema50.iloc[-1] and curr_st_dir == 1:
        trend_status = "BULLISH_UPTREND"
    elif curr_price < ema50.iloc[-1] and curr_st_dir == -1:
        trend_status = "BEARISH_DOWNTREND"
    else:
        trend_status = "CONSOLIDATION_SIDEWAYS"
        
    return {
        "current_price": round(curr_price, 2),
        "change_pct": change_pct,
        "ema20": round(float(ema20.iloc[-1]), 2),
        "ema50": round(float(ema50.iloc[-1]), 2),
        "ema200": round(float(ema200.iloc[-1]), 2),
        "rsi": round(curr_rsi, 1),
        "macd_hist": round(curr_macd_hist, 2),
        "bb_upper": round(float(bb_upper.iloc[-1]), 2),
        "bb_lower": round(float(bb_lower.iloc[-1]), 2),
        "atr": round(curr_atr, 2),
        "supertrend_direction": "BULLISH" if curr_st_dir == 1 else "BEARISH",
        "volume_ratio": vol_ratio,
        "vcp": vcp_analysis,
        "technical_score": tech_score,
        "trend_status": trend_status
    }
