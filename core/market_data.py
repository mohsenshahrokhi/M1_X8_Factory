# core/market_data.py

import pandas as pd
import MetaTrader5 as MetaTrader5
import os
print("✅ LOADING MARKET_DATA FROM:", os.path.abspath(__file__))


class MarketDataFeed:
    """
    Canonical Market Data Feed – X6 System
    (Hard-decoupled from MT5Connector)
    """

    def __init__(
        self,
        mt5,
        base_symbol: str = "BTCUSD",
        timeframe: int = None,
        bars: int = 500
    ):
        if hasattr(mt5, 'mt5'):  # اگر MT5Connector است
            self.connector = mt5
            self.mt5 = mt5.mt5  # ماژول اصلی MT5
        else:  # اگر ماژول مستقیم MT5 است
            self.connector = None
            self.mt5 = mt5

        self.symbol = base_symbol
        self.timeframe = timeframe if timeframe is not None else self.mt5.TIMEFRAME_M5
        self.bars = bars

        # ---- MT5 INIT ----
        if not self.mt5.initialize():
            raise RuntimeError("❌ MT5 initialization failed")

        print("✅ MT5 Connected")

        info = self.mt5.account_info()
        if info:
            print(f"Account: {info.login}")
            print(f"Broker : {info.company}")
            print(f"Balance: {info.balance}")

    # ==================================================
    # Market Data
    # ==================================================
    def get_data(self) -> pd.DataFrame:
        rates = self.mt5.copy_rates_from_pos(
            self.symbol,
            self.timeframe,
            0,
            self.bars,
        )

        if rates is None or len(rates) == 0:
            return None

        df = pd.DataFrame(rates)
        df["time"] = pd.to_datetime(df["time"], unit="s")
        df.set_index("time", inplace=True)
        return df

    # ==================================================
    # Account Equity ✅ STABLE
    # ==================================================
    def get_equity(self) -> float:
        try:
            info = self.mt5.account_info()
            if info is None:
                return 0.0
            return float(info.equity) if info.equity is not None else float(info.balance)
        except Exception:
            return 0.0

    # ==================================================
    # Point Value ✅ STABLE
    # ==================================================
    def get_point_value(self) -> float:
        try:
            info = self.mt5.symbol_info(self.symbol)
            if info is None:
                return 1.0
            return float(info.trade_tick_value)
        except Exception:
            return 1.0
