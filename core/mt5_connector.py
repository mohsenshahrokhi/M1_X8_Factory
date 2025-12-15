# X6/core/mt5_connector.py

import MetaTrader5 as mt5
import datetime


class MT5Connector:
    def __init__(self):
        self.connected = False

    def connect(self):
        if not mt5.initialize():
            raise RuntimeError("❌ MT5 initialize() failed")

        acc = mt5.account_info()
        if acc is None:
            raise RuntimeError("❌ MT5 connected but account_info() is None")

        self.connected = True

        print("✅ MT5 Connected")
        print(f"Account: {acc.login}")
        print(f"Broker : {acc.company}")
        print(f"Balance: {acc.balance}")

    def shutdown(self):
        if self.connected:
            mt5.shutdown()
            self.connected = False
            print(f"🔌 MT5 Disconnected {datetime.datetime.now()}")
