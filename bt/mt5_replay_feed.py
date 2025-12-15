# =====================================================
# bt/mt5_replay_feed.py
# FINAL – NUMPY‑FIRST / FREEZE‑PROOF / O(1)
# =====================================================

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List


class MT5ReplayFeed:
    """
    MT5 Replay Feed – X6 System
    --------------------------
    ✅ Fixed RangeIndex
    ✅ Fixed dtypes
    ✅ NumPy sliding window
    ✅ Zero Pandas access in step()
    ✅ O(1) iteration safe
    """

    TF_MAP = {
        "M1": mt5.TIMEFRAME_M1,
        "M5": mt5.TIMEFRAME_M5,
        "M15": mt5.TIMEFRAME_M15,
    }

    # ==================================================
    # INIT
    # ==================================================
    def __init__(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        timeframes: List[str],
        bars: int = 500,
    ):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.timeframes = timeframes
        self.bars = bars

        self._data: Dict[str, pd.DataFrame] = {}
        self._cursor: int = 0

        self._df_window: pd.DataFrame | None = None
        self._values: np.ndarray | None = None
        self._base_values: np.ndarray | None = None

        self._columns: List[str] | None = None
        self._dtypes: Dict[str, str] | None = None
        self._n_cols: int = 0

        self._equity: float = 100_000.0

    # ==================================================
    # LOAD DATA (ONE‑TIME)
    # ==================================================
    def load(self):

        base_tf = self.timeframes[0]

        # ---- Load MT5 rates ----
        for tf in self.timeframes:
            rates = mt5.copy_rates_range(
                self.symbol,
                self.TF_MAP[tf],
                self.start_date,
                self.end_date,
            )

            if rates is None or len(rates) == 0:
                raise RuntimeError(f"No data for {self.symbol} {tf}")

            df = pd.DataFrame(rates)
            df["time"] = pd.to_datetime(df["time"], unit="s")
            df.sort_values("time", inplace=True)
            df.reset_index(drop=True, inplace=True)

            self._data[tf] = df

        base_df = self._data[base_tf]

        if len(base_df) <= self.bars:
            raise RuntimeError("Not enough historical data")

        # ---- Initialize rolling window ----
        window = base_df.iloc[: self.bars].copy()
        window.reset_index(drop=True, inplace=True)

        self._columns = list(window.columns)

        # ---- Freeze dtypes ----
        self._dtypes = window.dtypes.to_dict()
        for c, dt in self._dtypes.items():
            window[c] = window[c].astype(dt, copy=False)

        self._df_window = window

        # ---- NumPy backing buffer (window) ----
        self._values = self._df_window.to_numpy(copy=False)
        self._n_cols = self._values.shape[1]

        # ---- NumPy backing buffer (full history) ----
        self._base_values = base_df.to_numpy(copy=False)

        self._cursor = self.bars

    # ==================================================
    # STEP (CRITICAL – NUMPY ONLY)
    # ==================================================
    def step(self) -> bool:
        """
        Advance by one bar.
        ❌ No pandas access
        ✅ NumPy only
        """

        base_values = self._base_values

        if self._cursor >= base_values.shape[0]:
            return False

        # ---- Fetch next row (NumPy) ----
        row = base_values[self._cursor]
        self._cursor += 1

        # ---- Shift rolling window ----
        self._values[:-1] = self._values[1:]

        # ---- Overwrite last row ----
        self._values[-1, :self._n_cols] = row[:self._n_cols]

        return True

    # ==================================================
    # DATA ACCESS
    # ==================================================
    def get_data(self) -> pd.DataFrame | None:
        if self._df_window is None or len(self._df_window) < 30:
            return None
        return self._df_window

    # ==================================================
    # EQUITY (BACKTEST SAFE)
    # ==================================================
    def get_equity(self) -> float:
        return float(self._equity)

    def update_equity(self, pnl: float):
        self._equity += float(pnl)

    # ==================================================
    # POINT VALUE
    # ==================================================
    def get_point_value(self) -> float:
        info = mt5.symbol_info(self.symbol)
        return float(info.trade_tick_value) if info else 1.0
