"""
Zerodha Kite Connect Broker Connector — OAuth authentication and order placement.
Backup/secondary broker for BharatAlpha Trade.
"""
import os
import json
from datetime import date

TOKEN_FILE = os.path.join(os.path.dirname(__file__), ".zerodha_token")

class ZerodhaConnector:
    def __init__(self):
        self.api_key = os.getenv("ZERODHA_API_KEY", "")
        self.api_secret = os.getenv("ZERODHA_API_SECRET", "")
        self.access_token = None
        self._load_cached_token()

    def _load_cached_token(self):
        if os.path.exists(TOKEN_FILE):
            try:
                with open(TOKEN_FILE, "r") as f:
                    data = json.load(f)
                if data.get("date") == str(date.today()) and data.get("token"):
                    self.access_token = data["token"]
            except Exception:
                pass

    def _save_token(self, token):
        with open(TOKEN_FILE, "w") as f:
            json.dump({"date": str(date.today()), "token": token}, f)
        self.access_token = token

    def is_connected(self):
        return bool(self.access_token)

    def get_login_url(self):
        if not self.api_key:
            return {"error": "ZERODHA_API_KEY must be set in .env"}
        try:
            from kiteconnect import KiteConnect
            kite = KiteConnect(api_key=self.api_key)
            return {"url": kite.login_url(), "status": "success"}
        except Exception as e:
            return {"error": str(e)}

    def generate_token(self, request_token):
        try:
            from kiteconnect import KiteConnect
            kite = KiteConnect(api_key=self.api_key)
            data = kite.generate_session(request_token, api_secret=self.api_secret)
            if data.get("access_token"):
                self._save_token(data["access_token"])
                return {"status": "success", "message": "Zerodha connected successfully"}
            return {"error": "Token generation failed"}
        except Exception as e:
            return {"error": str(e)}

    def get_positions(self):
        if not self.is_connected():
            return {"error": "Not connected"}
        try:
            from kiteconnect import KiteConnect
            kite = KiteConnect(api_key=self.api_key)
            kite.set_access_token(self.access_token)
            return kite.positions()
        except Exception as e:
            return {"error": str(e)}

    def place_order(self, symbol, qty, transaction_type, order_type="LIMIT", product="MIS", price=0):
        if not self.is_connected():
            return {"error": "Not connected"}
        try:
            from kiteconnect import KiteConnect
            kite = KiteConnect(api_key=self.api_key)
            kite.set_access_token(self.access_token)
            order_id = kite.place_order(
                variety=kite.VARIETY_REGULAR,
                exchange=kite.EXCHANGE_NFO,
                tradingsymbol=symbol,
                transaction_type=transaction_type,
                quantity=qty,
                product=product,
                order_type=order_type,
                price=price,
                validity=kite.VALIDITY_DAY
            )
            return {"status": "success", "order_id": order_id}
        except Exception as e:
            return {"error": str(e)}

zerodha_broker = ZerodhaConnector()
