"""Data-source router for the notebook pipeline.

Two sources:

1. **yfinance** (always) — daily OHLCV for technical analysis, plus
   `.info` for fundamentals of NSE-only tickers.

2. **Alpha Vantage** (when a key is configured AND the symbol maps to a
   US-listed ADR) — `OVERVIEW` and `INCOME_STATEMENT` are used to
   *enrich* the long-term row with extra fields like dividend yield,
   EV/EBITDA, and 5-year growth where the yfinance payload is missing.

All network calls go through the on-disk cache and the token-bucket
rate limiter so the Alpha Vantage free-tier (5 req/min, 500 req/day)
isn't tripped.
"""
from __future__ import annotations

import logging
import time
from typing import Any, Optional

import pandas as pd
import requests

from . import cache, universe
from .config import Config
from .rate_limiter import TokenBucket


log = logging.getLogger("stock_analysis.data")


# ── Stats counters used by the notebook's summary cell ─────────────────
class FetchStats:
    def __init__(self) -> None:
        self.cache_hits = 0
        self.fresh_calls = 0
        self.failed = 0
        self.av_calls = 0
        self.yf_calls = 0
        self.start_time = time.time()

    def as_dict(self) -> dict:
        elapsed = round(time.time() - self.start_time, 1)
        return {
            "cache_hits": self.cache_hits,
            "fresh_calls": self.fresh_calls,
            "av_calls": self.av_calls,
            "yf_calls": self.yf_calls,
            "failed": self.failed,
            "elapsed_seconds": elapsed,
        }


# ── yfinance helpers (prices) ──────────────────────────────────────────
def fetch_yf_history(symbol: str, period: str = "2y") -> pd.DataFrame:
    """Return a daily OHLCV DataFrame for a yfinance symbol."""
    import yfinance as yf  # imported lazily to keep startup fast

    ticker = yf.Ticker(symbol)
    df = ticker.history(period=period, auto_adjust=False)
    if df is None or df.empty:
        return pd.DataFrame()
    # Normalize column names and drop tz
    df = df.rename_axis("Date").reset_index()
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"]).dt.tz_localize(None)
    return df


def get_prices(
    symbol: str,
    cfg: Config,
    stats: FetchStats,
    period: str = "2y",
) -> pd.DataFrame:
    """Cached daily-price fetch (yfinance-backed)."""
    key = cache.cache_key("yf_history", {"symbol": symbol, "period": period})
    cached = cache.read(key, cfg.cache_dir, cfg.cache_max_age_hours)
    if cached is not None:
        stats.cache_hits += 1
        df = pd.DataFrame(cached.get("rows", []))
        if not df.empty and "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"])
        return df

    try:
        df = fetch_yf_history(symbol, period=period)
    except Exception as exc:  # pragma: no cover - network errors
        log.warning("yfinance history failed for %s: %s", symbol, exc)
        stats.failed += 1
        return pd.DataFrame()

    if df.empty:
        stats.failed += 1
        return df

    stats.fresh_calls += 1
    stats.yf_calls += 1
    cache.write(key, {"rows": df.to_dict(orient="records")}, cfg.cache_dir)
    return df


# ── Alpha Vantage: OVERVIEW & INCOME_STATEMENT ────────────────────────
_AV_BASE = "https://www.alphavantage.co/query"


def _av_get(params: dict, bucket: TokenBucket, cfg: Config, stats: FetchStats, label: str) -> Optional[dict]:
    """Wrapper around requests.get with cache + rate limit + error handling."""
    if not cfg.has_av_key():
        return None
    key = cache.cache_key("av_" + label, params)
    cached = cache.read(key, cfg.cache_dir, cfg.cache_max_age_hours)
    if cached is not None:
        stats.cache_hits += 1
        return cached

    bucket.wait()
    try:
        resp = requests.get(_AV_BASE, params=params, timeout=20)
        resp.raise_for_status()
        payload = resp.json()
    except Exception as exc:  # pragma: no cover - network errors
        log.warning("Alpha Vantage call %s failed: %s", label, exc)
        stats.failed += 1
        return None
    bucket.record()
    stats.fresh_calls += 1
    stats.av_calls += 1

    # AV embeds error messages under "Note" or "Information" for rate limits
    if "Note" in payload or "Information" in payload:
        log.warning("Alpha Vantage rate-limit signal: %s", payload.get("Note") or payload.get("Information"))
        return None

    cache.write(key, payload, cfg.cache_dir)
    return payload


def fetch_av_overview(av_symbol: str, bucket: TokenBucket, cfg: Config, stats: FetchStats) -> Optional[dict]:
    """Return the Alpha Vantage `OVERVIEW` payload, or None if not available."""
    params = {"function": "OVERVIEW", "symbol": av_symbol, "apikey": cfg.alpha_vantage_key}
    return _av_get(params, bucket, cfg, stats, label=f"overview:{av_symbol}")


def fetch_av_income_statement(av_symbol: str, bucket: TokenBucket, cfg: Config, stats: FetchStats) -> Optional[dict]:
    """Return the Alpha Vantage `INCOME_STATEMENT` payload (annual reports)."""
    params = {"function": "INCOME_STATEMENT", "symbol": av_symbol, "apikey": cfg.alpha_vantage_key}
    return _av_get(params, bucket, cfg, stats, label=f"income:{av_symbol}")


# ── Pluggable router ──────────────────────────────────────────────────
def get_fundamentals(
    symbol: str,
    cfg: Config,
    stats: FetchStats,
    bucket: Optional[TokenBucket] = None,
) -> dict:
    """Return a fundamentals dict for an NSE symbol.

    Always includes the yfinance-derived fundamentals via
    `analyze_stock_fundamentals` (the existing BharatAlpha engine). If
    the symbol maps to a US ADR AND an Alpha Vantage key is configured,
    additional fields (e.g. EV/EBITDA, dividend yield) are merged in
    from the AV OVERVIEW payload.
    """
    from backend.engine.fundamentals import analyze_stock_fundamentals

    base: dict = {}
    try:
        base = analyze_stock_fundamentals(symbol) or {}
    except Exception as exc:  # pragma: no cover
        log.warning("yfinance fundamentals failed for %s: %s", symbol, exc)
        stats.failed += 1

    av_symbol = universe.to_alphavantage_symbol(symbol)
    if av_symbol and cfg.has_av_key() and bucket is not None:
        overview = fetch_av_overview(av_symbol, bucket, cfg, stats)
        if overview:
            base = _merge_av_overview(base, overview)

    return base


def _to_float(value: Any) -> Optional[float]:
    try:
        f = float(value)
    except (TypeError, ValueError):
        return None
    return f


def _merge_av_overview(base: dict, overview: dict) -> dict:
    """Enrich a fundamentals dict with select Alpha Vantage OVERVIEW fields."""
    enriched = dict(base)

    # Map a few AV fields onto our canonical names. Only overwrite when
    # the AV value is numeric and the base value is missing or zero.
    def maybe_set(key: str, av_value: Any) -> None:
        f = _to_float(av_value)
        if f is None or f <= 0:
            return
        if not enriched.get(key):
            enriched[key] = round(f, 4)

    maybe_set("pe_ratio", overview.get("PERatio"))
    maybe_set("peg_ratio", overview.get("PEGRatio"))
    maybe_set("pb_ratio", overview.get("PriceToBookRatio"))
    maybe_set("ev_to_ebitda", overview.get("EVToEBITDA"))
    maybe_set("roe", overview.get("ReturnOnEquityTTM"))  # decimal in AV
    maybe_set("dividend_yield", overview.get("DividendYield"))
    maybe_set("eps", overview.get("EPS"))
    maybe_set("revenue_ttm", overview.get("RevenueTTM"))
    maybe_set("gross_profit_ttm", overview.get("GrossProfitTTM"))
    enriched["av_overview_raw"] = {k: overview.get(k) for k in (
        "Symbol", "Name", "Sector", "Industry", "MarketCapitalization",
        "PERatio", "PEGRatio", "PriceToBookRatio", "EVToEBITDA",
        "ReturnOnEquityTTM", "DividendYield", "EPS", "RevenueTTM",
    )}
    return enriched
