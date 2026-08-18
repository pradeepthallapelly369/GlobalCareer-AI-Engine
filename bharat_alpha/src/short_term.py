"""Short-term (technical) analysis layer.

Composes the existing `analyze_stock_technicals` from the BharatAlpha
engine and adds a 0-100 weighted composite score plus an entry /
target / stop-loss suggestion.
"""
from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd

from backend.engine.technicals import (
    analyze_stock_technicals,
    calculate_ema,
    calculate_macd,
    calculate_bollinger_bands,
    calculate_rsi,
)


# ── Per-component scorers (each returns 0-100) ────────────────────────
def _rsi_score(rsi: float) -> float:
    if pd.isna(rsi):
        return 50.0
    if rsi < 30:
        return 90.0           # oversold → mean-reversion buy
    if rsi > 70:
        return 20.0           # overbought → risky
    if 40 <= rsi <= 60:
        return 60.0           # neutral momentum
    if rsi < 40:
        return 70.0
    return 40.0               # 60-70 zone


def _macd_score(hist: float, prev_hist: float) -> float:
    if pd.isna(hist) or pd.isna(prev_hist):
        return 50.0
    if hist > 0 and hist > prev_hist:
        return 100.0          # bullish & accelerating
    if hist > 0:
        return 75.0
    if hist < 0 and hist < prev_hist:
        return 0.0            # bearish & accelerating
    return 30.0


def _ema_stack_score(close: float, ema20: float, ema50: float, ema200: float) -> float:
    if any(pd.isna(x) for x in (close, ema20, ema50, ema200)):
        return 50.0
    if close > ema20 > ema50 > ema200:
        return 100.0
    if close < ema20 < ema50 < ema200:
        return 0.0
    # Mixed
    bullish = sum(int(close > ema20), int(ema20 > ema50), int(ema50 > ema200))
    return 25.0 + bullish * 25.0


def _bollinger_score(close: float, upper: float, lower: float) -> float:
    if any(pd.isna(x) for x in (close, upper, lower)) or upper == lower:
        return 50.0
    pct = (close - lower) / (upper - lower)
    pct = max(0.0, min(1.0, pct))
    # Closer to lower band → higher score (buy zone); closer to upper → lower
    return round(100.0 * (1.0 - pct), 1)


def _volume_score(volume: float, avg_volume: float) -> float:
    if pd.isna(volume) or pd.isna(avg_volume) or avg_volume <= 0:
        return 40.0
    ratio = volume / avg_volume
    if ratio >= 2.0:
        return 100.0
    if ratio >= 1.5:
        return 85.0
    if ratio >= 1.0:
        return 60.0
    if ratio >= 0.5:
        return 40.0
    return 20.0


def _crossover_score(ema20: pd.Series, ema50: pd.Series, lookback: int = 5) -> float:
    """Return 100 if golden cross in last `lookback` bars, 0 for death cross, 50 otherwise."""
    if len(ema20) < lookback + 1 or len(ema50) < lookback + 1:
        return 50.0
    recent = ema20.iloc[-lookback:].values - ema50.iloc[-lookback:].values
    if not (recent[:-1] * recent[1:] < 0).any():
        return 50.0
    crossed = recent[-1] - recent[-2]
    return 100.0 if crossed > 0 else 0.0


# ── Public API ────────────────────────────────────────────────────────
def score_technicals(prices: pd.DataFrame, weights: dict) -> dict:
    """Compute the 0-100 weighted technical score and a rationale string.

    `prices` must contain 'Close' and 'Volume' columns.
    """
    if prices.empty or len(prices) < 60:
        return {"score": 0.0, "breakdown": {}, "rationale": "Insufficient history"}

    close = prices["Close"]
    ema20 = calculate_ema(close, 20)
    ema50 = calculate_ema(close, 50)
    ema200 = calculate_ema(close, 200) if len(prices) >= 200 else ema50
    macd_line, macd_sig, macd_hist = calculate_macd(close)
    rsi = calculate_rsi(close, 14)
    bb_upper, bb_mid, bb_lower = calculate_bollinger_bands(close, 20, 2)

    last_close = float(close.iloc[-1])
    avg_vol_20 = float(prices["Volume"].tail(20).mean())

    components = {
        "rsi": _rsi_score(float(rsi.iloc[-1])),
        "macd": _macd_score(float(macd_hist.iloc[-1]), float(macd_hist.iloc[-2])),
        "ema_stack": _ema_stack_score(
            last_close,
            float(ema20.iloc[-1]),
            float(ema50.iloc[-1]),
            float(ema200.iloc[-1]),
        ),
        "bollinger": _bollinger_score(
            last_close,
            float(bb_upper.iloc[-1]),
            float(bb_lower.iloc[-1]),
        ),
        "volume": _volume_score(float(prices["Volume"].iloc[-1]), avg_vol_20),
        "crossover": _crossover_score(ema20, ema50),
    }

    total = sum(components[k] * weights.get(k, 0.0) for k in components)
    rationale = _rationale(components, last_close, float(ema20.iloc[-1]), float(ema50.iloc[-1]))

    return {
        "score": round(total, 1),
        "breakdown": {k: round(v, 1) for k, v in components.items()},
        "rationale": rationale,
        "rsi": round(float(rsi.iloc[-1]), 1),
        "macd_hist": round(float(macd_hist.iloc[-1]), 3),
        "ema20": round(float(ema20.iloc[-1]), 2),
        "ema50": round(float(ema50.iloc[-1]), 2),
    }


def _rationale(components: dict, last_close: float, ema20: float, ema50: float) -> str:
    bits: list[str] = []
    if components["ema_stack"] >= 75:
        bits.append("bullish EMA stack")
    elif components["ema_stack"] <= 25:
        bits.append("bearish EMA stack")
    if components["macd"] >= 75:
        bits.append("MACD bullish & accelerating")
    elif components["macd"] <= 25:
        bits.append("MACD bearish")
    if components["rsi"] >= 75:
        bits.append("RSI oversold zone")
    elif components["rsi"] <= 25:
        bits.append("RSI overbought")
    if components["volume"] >= 75:
        bits.append("volume confirmation")
    if components["crossover"] >= 75:
        bits.append("recent golden cross")
    elif components["crossover"] <= 25:
        bits.append("recent death cross")
    if not bits:
        return "Mixed signals; neutral setup"
    return ", ".join(bits)


def entry_target_sl(prices: pd.DataFrame, score: float) -> dict:
    """Suggest an entry zone, target, and stop-loss using ATR + 20/50 EMA.

    Convention:
      - Entry: a tight band around the 20-EMA (or last close, whichever
        gives a better risk/reward).
      - Target: 2× risk above entry (2:1 R:R).
      - Stop-loss: 1.5× ATR below entry.
    """
    if prices.empty or len(prices) < 20:
        return {"entry": None, "target": None, "stop_loss": None, "risk_reward": None}

    from backend.engine.technicals import calculate_atr

    close = float(prices["Close"].iloc[-1])
    ema20 = float(calculate_ema(prices["Close"], 20).iloc[-1])
    ema50 = float(calculate_ema(prices["Close"], 50).iloc[-1])
    atr = float(calculate_atr(prices, 14).iloc[-1])

    entry = round(min(close, ema20) * 0.998, 2)
    stop_loss = round(entry - 1.5 * atr, 2)
    risk = entry - stop_loss
    if risk <= 0:
        risk = close * 0.03
        stop_loss = round(entry - risk, 2)
    target = round(entry + 2.0 * risk, 2)
    rr = round((target - entry) / risk, 2) if risk > 0 else None

    return {
        "entry": entry,
        "target": target,
        "stop_loss": stop_loss,
        "risk_reward": rr,
        "atr": round(atr, 2),
        "ema20": round(ema20, 2),
        "ema50": round(ema50, 2),
    }
