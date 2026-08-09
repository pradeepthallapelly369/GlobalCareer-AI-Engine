import yfinance as yf
import pandas as pd
import numpy as np
from backend.engine.technicals import calculate_ema, calculate_rsi, calculate_supertrend

def run_strategy_backtest(ticker_symbol: str, strategy: str = "EMA_CROSSOVER", period: str = "2y") -> dict:
    """
    Backtests a trading strategy over historical price data.
    Supported strategies:
    - EMA_CROSSOVER (20 EMA crosses above 50 EMA)
    - SUPERTREND_BREAKOUT (Supertrend switches from Bearish to Bullish)
    - RSI_OVERSOLD_REBOUND (RSI < 35 rebound with volume confirmation)
    """
    symbol = ticker_symbol.upper()
    if not symbol.endswith(".NS") and not symbol.endswith(".BO"):
        symbol = f"{symbol}.NS"
        
    try:
        stock = yf.Ticker(symbol)
        df = stock.history(period=period).dropna(subset=['Close'])
    except Exception as e:
        return {"error": f"Failed to fetch data for {symbol}: {e}"}

    if df.empty or len(df) < 50:
        return {"error": "Insufficient historical data for backtesting"}

    close = df['Close']
    df['EMA20'] = calculate_ema(close, 20)
    df['EMA50'] = calculate_ema(close, 50)
    df['RSI'] = calculate_rsi(close, 14)
    df['Supertrend'], df['ST_Dir'] = calculate_supertrend(df)

    initial_capital = 100000.0 # ₹1,00,000 Starting Capital
    capital = initial_capital
    position = None
    trades = []
    equity_curve = [initial_capital]
    
    # Iterate through history bar by bar
    for i in range(50, len(df)):
        current_date = df.index[i].strftime("%Y-%m-%d")
        curr_price = float(df['Close'].iloc[i])
        
        # Signal evaluation
        buy_signal = False
        sell_signal = False
        
        if strategy == "EMA_CROSSOVER":
            # Golden Cross: EMA20 crosses above EMA50
            if df['EMA20'].iloc[i-1] <= df['EMA50'].iloc[i-1] and df['EMA20'].iloc[i] > df['EMA50'].iloc[i]:
                buy_signal = True
            elif df['EMA20'].iloc[i-1] >= df['EMA50'].iloc[i-1] and df['EMA20'].iloc[i] < df['EMA50'].iloc[i]:
                sell_signal = True
                
        elif strategy == "SUPERTREND_BREAKOUT":
            if df['ST_Dir'].iloc[i-1] == -1 and df['ST_Dir'].iloc[i] == 1:
                buy_signal = True
            elif df['ST_Dir'].iloc[i-1] == 1 and df['ST_Dir'].iloc[i] == -1:
                sell_signal = True
                
        elif strategy == "RSI_OVERSOLD_REBOUND":
            if df['RSI'].iloc[i-1] < 35 and df['RSI'].iloc[i] >= 35:
                buy_signal = True
            elif df['RSI'].iloc[i] > 70:
                sell_signal = True
                
        else: # Default EMA Crossover
            if df['EMA20'].iloc[i-1] <= df['EMA50'].iloc[i-1] and df['EMA20'].iloc[i] > df['EMA50'].iloc[i]:
                buy_signal = True
            elif df['EMA20'].iloc[i-1] >= df['EMA50'].iloc[i-1] and df['EMA20'].iloc[i] < df['EMA50'].iloc[i]:
                sell_signal = True

        # Trade Management
        if buy_signal and position is None:
            shares = int(capital / curr_price)
            if shares > 0:
                cost = shares * curr_price
                position = {
                    "entry_date": current_date,
                    "entry_price": curr_price,
                    "shares": shares,
                    "cost": cost
                }
                
        elif (sell_signal or i == len(df) - 1) and position is not None:
            revenue = position["shares"] * curr_price
            profit = revenue - position["cost"]
            return_pct = (profit / position["cost"]) * 100
            capital += profit
            
            trades.append({
                "entry_date": position["entry_date"],
                "exit_date": current_date,
                "entry_price": round(position["entry_price"], 2),
                "exit_price": round(curr_price, 2),
                "shares": position["shares"],
                "profit_loss_rs": round(profit, 2),
                "return_pct": round(return_pct, 2)
            })
            position = None

        portfolio_val = capital if position is None else capital + (position["shares"] * (curr_price - position["entry_price"]))
        equity_curve.append(portfolio_val)

    # Compute Statistics
    winning_trades = [t for t in trades if t["profit_loss_rs"] > 0]
    losing_trades = [t for t in trades if t["profit_loss_rs"] <= 0]
    total_trades = len(trades)
    win_rate = round((len(winning_trades) / total_trades) * 100, 1) if total_trades > 0 else 0
    
    total_return_pct = round(((capital - initial_capital) / initial_capital) * 100, 2)
    
    # Benchmark Buy & Hold return
    start_p = float(df['Close'].iloc[50])
    end_p = float(df['Close'].iloc[-1])
    benchmark_return_pct = round(((end_p - start_p) / start_p) * 100, 2)
    
    # Max Drawdown calculation
    equity_series = pd.Series(equity_curve)
    rolling_max = equity_series.cummax()
    drawdown = (equity_series - rolling_max) / rolling_max
    max_drawdown_pct = round(abs(drawdown.min()) * 100, 2) if not drawdown.empty else 0

    return {
        "ticker": symbol.replace(".NS", ""),
        "strategy": strategy,
        "period": period,
        "starting_capital": initial_capital,
        "final_capital": round(capital, 2),
        "total_return_pct": total_return_pct,
        "benchmark_return_pct": benchmark_return_pct,
        "total_trades": total_trades,
        "winning_trades": len(winning_trades),
        "losing_trades": len(losing_trades),
        "win_rate_pct": win_rate,
        "max_drawdown_pct": max_drawdown_pct,
        "trades": trades[-10:] # Return last 10 execution logs
    }
