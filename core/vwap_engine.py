import numpy as np
import pandas as pd


class VWAPEngine:
    """
    Institutional VWAP + Volume Distribution Engine
    Phase‑10A compatible
    """

    def __init__(
        self,
        rolling_window=None,
        vol_ma_window=20,
        range_ma_window=20,
        atr_window=14,
    ):
        self.rolling_window = rolling_window
        self.vol_ma_window = vol_ma_window
        self.range_ma_window = range_ma_window
        self.atr_window = atr_window

    def compute(self, df: pd.DataFrame) -> pd.DataFrame:
        data = df.copy()

        data["tp"] = (data["high"] + data["low"] + data["close"]) / 3.0
        data["pv"] = data["tp"] * data["tick_volume"]

        if self.rolling_window:
            vol_sum = data["tick_volume"].rolling(self.rolling_window).sum()
            pv_sum = data["pv"].rolling(self.rolling_window).sum()
        else:
            vol_sum = data["tick_volume"].cumsum()
            pv_sum = data["pv"].cumsum()

        data["vwap"] = pv_sum / vol_sum
        data["vwap_dev"] = (data["close"] - data["vwap"]) / data["vwap"]

        vol_ma = data["tick_volume"].rolling(self.vol_ma_window).mean()
        data["vol_weight"] = data["tick_volume"] / vol_ma

        data["bar_range"] = data["high"] - data["low"]
        data["avg_range"] = data["bar_range"].rolling(self.range_ma_window).mean()

        high_low = data["high"] - data["low"]
        high_close = np.abs(data["high"] - data["close"].shift())
        low_close = np.abs(data["low"] - data["close"].shift())

        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        data["atr"] = tr.rolling(window=self.atr_window).mean()

        data.replace([np.inf, -np.inf], np.nan, inplace=True)
        return data
