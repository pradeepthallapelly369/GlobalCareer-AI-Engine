"""Central configuration for the stock-analysis notebook.

Loads the Alpha Vantage API key from the environment (or a .env file) and
defines the default scoring weights used by the short-term (technical)
and long-term (fundamental) ranking pipelines.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

try:
    from dotenv import load_dotenv  # type: ignore
    _DOTENV_LOADED = True
except Exception:  # pragma: no cover - python-dotenv is optional at import time
    _DOTENV_LOADED = False


# Resolve project root (this file lives in <project>/src/config.py)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
CACHE_DIR = DATA_DIR / "cache"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
CHARTS_DIR = OUTPUTS_DIR / "charts"


@dataclass
class Config:
    """Runtime configuration for the notebook pipeline."""

    alpha_vantage_key: str = ""
    cache_dir: Path = field(default_factory=lambda: CACHE_DIR)
    outputs_dir: Path = field(default_factory=lambda: OUTPUTS_DIR)
    charts_dir: Path = field(default_factory=lambda: CHARTS_DIR)

    # Horizons / output sizing
    short_horizon_days: int = 21        # ~1 trading month
    long_horizon_years: int = 1
    top_n: int = 10

    # Liquidity filter — drop names with 20-day average volume below this
    min_avg_volume_20d: int = 100_000

    # Technical scoring weights (must sum to 1.0)
    technical_weights: dict = field(default_factory=lambda: {
        "rsi": 0.15,
        "macd": 0.20,
        "ema_stack": 0.20,
        "bollinger": 0.15,
        "volume": 0.15,
        "crossover": 0.15,
    })

    # Fundamental scoring weights (must sum to 1.0)
    fundamental_weights: dict = field(default_factory=lambda: {
        "value": 0.30,
        "quality": 0.30,
        "growth": 0.25,
        "safety": 0.15,
    })

    # Alpha Vantage free tier: 5 requests/minute, 500 requests/day
    rate_limit_per_min: int = 5
    cache_max_age_hours: int = 24

    @classmethod
    def from_env(cls, project_root: Path | None = None) -> "Config":
        """Build a Config from environment variables / .env file."""
        root = project_root or PROJECT_ROOT
        env_path = root / ".env"
        if env_path.exists() and _DOTENV_LOADED:
            load_dotenv(env_path)

        return cls(
            alpha_vantage_key=os.getenv("ALPHA_VANTAGE_API_KEY", "").strip(),
        )

    def ensure_dirs(self) -> None:
        for d in (self.cache_dir, self.outputs_dir, self.charts_dir):
            d.mkdir(parents=True, exist_ok=True)

    def has_av_key(self) -> bool:
        return bool(self.alpha_vantage_key)
