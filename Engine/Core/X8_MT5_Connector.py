import MetaTrader5 as mt5
import json
import os
import time


class MT5Connector:

    def __init__(self):

        # Load config from project root/config/
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        config_path = os.path.join(base_path, "config", "mt5_config.json")

        if not os.path.exists(config_path):
            raise FileNotFoundError(f"❌ Config file not found: {config_path}")

        with open(config_path, "r") as f:
            cfg = json.load(f)

        # ✅ MATCHED EXACTLY TO YOUR FILE
        self.login = cfg["login"]
        self.password = cfg["password"]
        self.server = cfg["server"]
        self.default_symbol = cfg.get("symbol", None)
        self.default_lot = cfg.get("lot", 0.01)
        self.auto_trade_enabled = cfg.get("auto_trade_enabled", True)

        self.connect()

        # Auto-select default symbol if provided
        if self.default_symbol:
            self.select_symbol(self.default_symbol)


    # ------------------------------------------------------
    # ✅ CONNECT TO MT5
    # ------------------------------------------------------
    def connect(self):

        mt5.initialize()

        authorized = mt5.login(
            login=self.login,
            password=self.password,
            server=self.server
        )

        if authorized:
            print(f"✅ MT5 Login successful | ID: {self.login}")
        else:
            raise RuntimeError(f"❌ MT5 Login failed: {mt5.last_error()}")


    # ------------------------------------------------------
    # ✅ SELECT SYMBOL
    # ------------------------------------------------------
    def select_symbol(self, symbol):

        info = mt5.symbol_info(symbol)

        if info is None:
            print(f"❌ Symbol not found: {symbol}")
            return False

        if not info.visible:
            if not mt5.symbol_select(symbol, True):
                print(f"❌ Failed to activate symbol: {symbol}")
                return False

        print(f"✅ Symbol selected: {symbol}")
        return True


    # ------------------------------------------------------
    # ✅ FETCH LAST M1 CANDLE
    # ------------------------------------------------------
    def get_latest_candle(self, symbol):

        try:
            rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 1)

            if rates is None or len(rates) == 0:
                print(f"⚠️ No rates received for {symbol}")
                return None

            r = rates[0]

            candle = {
                "time": int(r["time"]),
                "open": float(r["open"]),
                "high": float(r["high"]),
                "low": float(r["low"]),
                "close": float(r["close"]),
                "volume": float(r["tick_volume"]),
                "spread": float(r["spread"]),
            }

            return candle

        except Exception as e:
            print(f"❌ get_latest_candle error: {e}")
            return None


    # ------------------------------------------------------
    # ✅ SEND ORDER
    # ------------------------------------------------------
    def send_order(self, symbol, order_type, lot=None):

        if not self.auto_trade_enabled:
            print("⚠️ Auto trading disabled. Ignoring trade request.")
            return None

        if lot is None:
            lot = self.default_lot

        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            print(f"❌ Could not get tick for {symbol}")
            return None

        price = tick.ask if order_type == "BUY" else tick.bid

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "type": mt5.ORDER_TYPE_BUY if order_type == "BUY" else mt5.ORDER_TYPE_SELL,
            "volume": float(lot),
            "price": float(price),
            "deviation": 30,
            "magic": 20241101,
            "comment": "AutoEngine_M1",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }

        result = mt5.order_send(request)

        if result is None:
            print("❌ order_send returned None")
            return None

        if result.retcode == mt5.TRADE_RETCODE_DONE:
            print(f"✅ ORDER EXECUTED: {order_type} {lot} {symbol} @ {price}")
        else:
            print(f"⚠️ ORDER FAILED | Retcode: {result.retcode} | Details: {result}")

        return result
