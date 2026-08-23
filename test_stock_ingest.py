import sys
import os
sys.path.append("/home/upc/every_thing_claude/indian-stock-market-lakehouse-pipeline/indian-stock-market-lakehouse-pipeline/scripts")

try:
    from stock_market_ingest import fetch_live_market_data, normalize_ohlcv
    print("[PASS] Successfully imported modules from stock_market_ingest.py")
except Exception as e:
    print(f"[FAIL] Error importing: {e}")
    sys.exit(1)

try:
    df = fetch_live_market_data(["RELIANCE.NS"])
    if not df.empty and "close_price" in df.columns:
        print(f"[PASS] Data fetching works! Retrieved {len(df)} rows for RELIANCE.NS")
    else:
        print("[FAIL] Data fetching returned empty or malformed dataframe.")
except Exception as e:
    print(f"[FAIL] Data fetching crashed: {e}")
