"""
BharatAlpha Trade ⚡ — Options & Futures Trading Terminal API
FastAPI backend on port 8001
Features: MiroFish Swarm Sandbox, Live Market Ticks, Fyers Broker Integration
"""
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os, math
import numpy as np

from dotenv import load_dotenv
load_dotenv()

from backend.broker.fyers_connector import fyers_broker
from backend.broker.zerodha_connector import zerodha_broker
from backend.broker.market_feed import market_feed
from backend.engine.swarm_simulator import swarm_engine
from backend.engine.options_greeks import (
    enrich_option_chain_with_greeks, calculate_all_greeks,
    solve_implied_volatility, days_to_expiry_fraction, RISK_FREE_RATE
)
from backend.engine.options_strategies import (
    STRATEGY_CATALOG, analyze_strategy, build_strategy_legs, calculate_payoff_at_expiry
)
from backend.engine.agent_hub import TradeAgentEngine

app = FastAPI(title="BharatAlpha Trade ⚡ — Options & Futures Terminal", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

trade_agent = TradeAgentEngine()

def sanitize(obj):
    """Recursively sanitize numpy/nan values for JSON serialization."""
    if isinstance(obj, dict):
        return {k: sanitize(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize(x) for x in obj]
    elif isinstance(obj, (float, np.floating)):
        if math.isnan(obj) or math.isinf(obj):
            return 0.0
        return float(obj)
    elif isinstance(obj, (int, np.integer)):
        return int(obj)
    elif isinstance(obj, (bool, np.bool_)):
        return bool(obj)
    return obj

# ─── Data Models ───────────────────────────────────
class FyersCredsRequest(BaseModel):
    app_id: str
    secret_key: str
    access_token: Optional[str] = None

class StrategyRequest(BaseModel):
    strategy_key: str
    spot_price: float
    lot_size: int = 25
    strike_step: int = 50

class OrderLeg(BaseModel):
    action: str  # BUY or SELL
    type: str    # CE or PE
    strike: int
    qty: int
    premium: float

class ExecuteRequest(BaseModel):
    legs: List[OrderLeg]
    lot_size: int = 25
    mode: str = "paper"  # paper | live
    broker: str = "fyers"

class AgentChatReq(BaseModel):
    query: str
    agent: str = "arya"

class AgentExecReq(BaseModel):
    symbol: str = "NIFTY"
    action: str = "BUY"
    mode: str = "paper"
    broker: str = "fyers"
    strategy: str = "SHORT_STRADDLE"
    qty: int = 25
    strike: int = 24600
    type: str = "CE"

class SwarmSimReq(BaseModel):
    symbol: str = "NIFTY"
    spot_price: float = 24600.0

# ─── Live Market Feed Endpoint ───────────────────────────
@app.get("/api/market/ticks")
def get_market_ticks():
    """Get live ticker stream for NIFTY, BANKNIFTY, FINNIFTY, SENSEX."""
    return sanitize(market_feed.get_live_ticks())

# ─── MiroFish Swarm Simulation Endpoint ───────────────────
@app.post("/api/agent/swarm/simulate")
def run_swarm_simulation(req: SwarmSimReq):
    """Run a 3-round MiroFish Swarm Sandbox Simulation for market consensus and trade generation."""
    return sanitize(swarm_engine.run_simulation(symbol=req.symbol, spot_price=req.spot_price))

# ─── Broker Auth & Setup Endpoints ────────────────────────
@app.post("/api/broker/fyers/credentials")
def save_fyers_credentials(req: FyersCredsRequest):
    """Configure and save Fyers API credentials."""
    res = fyers_broker.save_credentials(req.app_id, req.secret_key, req.access_token)
    return sanitize(res)

@app.get("/api/broker/fyers/profile")
def get_fyers_profile():
    """Get connected Fyers profile information."""
    return sanitize(fyers_broker.get_profile())

@app.get("/api/broker/funds")
def get_broker_funds():
    """Get account margin and funds."""
    return sanitize(fyers_broker.get_funds())

@app.get("/api/broker/login/{broker}")
def broker_login(broker: str):
    """Get OAuth login URL for Fyers or Zerodha."""
    if broker == "fyers":
        return sanitize(fyers_broker.get_login_url())
    elif broker == "zerodha":
        return sanitize(zerodha_broker.get_login_url())
    raise HTTPException(status_code=400, detail="Supported brokers: fyers, zerodha")

@app.get("/api/broker/callback")
def broker_callback(auth_code: str = Query(None), s: str = Query(None), code: str = Query(None)):
    """Handle OAuth redirect callback."""
    token = auth_code or code
    if not token:
        raise HTTPException(status_code=400, detail="No auth_code received")
    state = s or "fyers"
    if "zerodha" in state.lower():
        return sanitize(zerodha_broker.generate_token(token))
    return sanitize(fyers_broker.generate_token(token))

@app.get("/api/broker/status")
def broker_status():
    """Check broker connection status."""
    return {
        "fyers": {
            "connected": fyers_broker.is_connected(),
            "has_credentials": bool(fyers_broker.client_id),
            "client_id": fyers_broker.client_id[:6] + "..." if fyers_broker.client_id else ""
        },
        "zerodha": {
            "connected": zerodha_broker.is_connected(),
            "has_credentials": bool(zerodha_broker.api_key),
        },
        "trading_mode": os.getenv("TRADING_MODE", "paper"),
    }

# ─── Option Chain Endpoint ──────────────────────────────────
@app.get("/api/options/chain/{symbol}")
def get_option_chain(symbol: str = "NIFTY"):
    """Get live option chain with Black-Scholes Greeks."""
    sym_map = {
        "NIFTY": "NSE:NIFTY50-INDEX",
        "BANKNIFTY": "NSE:NIFTYBANK-INDEX",
    }
    fyers_symbol = sym_map.get(symbol.upper(), f"NSE:{symbol.upper()}-INDEX")

    raw = fyers_broker.get_option_chain(fyers_symbol)
    chain = raw.get("chain", [])
    spot = raw.get("spot_price", 24628.5)
    dte = raw.get("days_to_expiry", 7)
    lot_size = raw.get("lot_size", 25)
    strike_step = raw.get("strike_step", 50)

    enriched = enrich_option_chain_with_greeks(chain, spot, dte)

    return sanitize({
        "status": "success",
        "symbol": symbol.upper(),
        "spot_price": spot,
        "lot_size": lot_size,
        "strike_step": strike_step,
        "expiry": raw.get("expiry", "N/A"),
        "days_to_expiry": dte,
        "source": raw.get("source", "live"),
        "chain": enriched
    })

# ─── Strategy Builder Endpoint ───────────────────────────────
@app.get("/api/options/strategies")
def list_strategies():
    """List preset strategy templates."""
    return sanitize({
        "status": "success",
        "strategies": [
            {"key": k, **v} for k, v in STRATEGY_CATALOG.items()
        ]
    })

@app.post("/api/options/strategy")
def build_strategy(req: StrategyRequest):
    """Build strategy payoff analysis."""
    result = analyze_strategy(
        req.strategy_key, req.spot_price, req.lot_size, req.strike_step
    )
    return sanitize({"status": "success", "data": result})

# ─── Order Execution Endpoint ────────────────────────────────
@app.post("/api/options/execute")
def execute_order(req: ExecuteRequest):
    """Execute order via paper mode or live Fyers broker."""
    if req.mode == "paper":
        return sanitize(trade_agent.execute_trade({
            "symbol": "NIFTY",
            "action": "BUY",
            "mode": "paper",
            "broker": "fyers",
            "strategy": "MULTI_LEG",
            "qty": req.lot_size,
        }))
    else:
        if not fyers_broker.is_connected():
            raise HTTPException(status_code=401, detail="Fyers broker not connected. Please enter credentials.")
        results = []
        for leg in req.legs:
            sym = f"NSE:NIFTY{leg.strike}{leg.type}"
            side = 1 if leg.action == "BUY" else -1
            resp = fyers_broker.place_order(sym, leg.qty * req.lot_size, side)
            results.append(resp)
        return sanitize({"status": "success", "mode": "live", "orders": results})

# ─── Positions & P&L Endpoint ────────────────────────────────
@app.get("/api/broker/positions")
def get_positions():
    """Get current positions."""
    if fyers_broker.is_connected():
        return sanitize(fyers_broker.get_positions())
    return sanitize({
        "status": "success",
        "mode": "paper",
        "positions": trade_agent.get_positions(),
        "total_positions": len(trade_agent.get_positions()),
    })

# ─── Agent AI Chat & Execution ──────────────────────────────
@app.post("/api/agent/chat")
def trade_agent_chat(req: AgentChatReq):
    """Chat with Options AI Agent (Arya)."""
    return sanitize(trade_agent.process_chat(req.query, req.agent))

@app.post("/api/agent/execute")
def trade_agent_execute(req: AgentExecReq):
    """Execute trade directly triggered by AI Agent."""
    return sanitize(trade_agent.execute_trade(req.dict()))
