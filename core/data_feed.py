# core/data_feed.py

import MetaTrader5 as mt5
import pandas as pd

class MarketDataFeed:
    def __init__(self, base_symbol, timeframe, bars=500):
        self.base_symbol = base_symbol
        self.timeframe = timeframe
        self.bars = bars
        self.symbol = self._resolve_symbol()
    def get_point_value(self) -> float:
            return 1.0
    def _resolve_symbol(self):
        symbols = mt5.symbols_get()
        for s in symbols:
            if s.name.startswith(self.base_symbol):
                mt5.symbol_select(s.name, True)
                return s.name
        raise RuntimeError(f"Symbol {self.base_symbol} not found in broker")

    def get_data(self):
        rates = mt5.copy_rates_from_pos(
            self.symbol,
            self.timeframe,
            0,
            self.bars
        )

        if rates is None or len(rates) == 0:
            raise RuntimeError(f"No data for {self.symbol}")

        df = pd.DataFrame(rates)
        df["time"] = pd.to_datetime(df["time"], unit="s")

        return df
    def get_point_value(self) -> float:
        """
        USD value per 1.0 price move
        """
        return 1.0

    def get_point_value(self) -> float:
        """
        USD value per 1.0 price move.
        For XAUUSD spot CFD:
        1 lot ≈ 1 USD per 0.01 move
        Adjust if broker differs.
        """
        return 1.0
