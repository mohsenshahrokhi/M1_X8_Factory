import numpy as np


class VWAPEngine:
    """
    Freeze‑Proof, O(1), NumPy‑Only VWAP Engine
    Compatible with Orchestrator Phase‑9C
    """

    def __init__(
        self,
        vol_ma_window=20,
        range_ma_window=20,
        atr_window=14,
    ):
        self.vol_ma_window = vol_ma_window
        self.range_ma_window = range_ma_window
        self.atr_window = atr_window

        self._init = False

    # ==================================================
    # One‑time initialization
    # ==================================================
    def warmup(self, df):
        self._close = df["close"].to_numpy(dtype=np.float64, copy=False)
        self._high  = df["high"].to_numpy(dtype=np.float64, copy=False)
        self._low   = df["low"].to_numpy(dtype=np.float64, copy=False)
        self._vol   = df["tick_volume"].to_numpy(dtype=np.float64, copy=False)

        n = len(self._close)

        # ---- VWAP ----
        tp = (self._high + self._low + self._close) / 3.0
        pv = tp * self._vol
        self._vwap = np.cumsum(pv) / np.cumsum(self._vol)

        # ---- Ranges ----
        self._bar_range = self._high - self._low

        # ---- Rolling buffers ----
        self._vol_ma     = np.full(n, np.nan)
        self._avg_range  = np.full(n, np.nan)
        self._atr        = np.full(n, np.nan)

        self._init = True

    # ==================================================
    # O(1) step
    # ==================================================
    def step(self, i: int):
        if not self._init:
            raise RuntimeError("VWAPEngine not initialized")

        n = len(self._close)
        if i >= n:
            i = n - 1

        # -------- Volume MA --------
        w = self.vol_ma_window
        start = max(0, i - w + 1)
        self._vol_ma[i] = np.mean(self._vol[start : i + 1])

        # -------- Avg Range --------
        w = self.range_ma_window
        start = max(0, i - w + 1)
        self._avg_range[i] = np.mean(self._bar_range[start : i + 1])

        # -------- ATR proxy --------
        w = self.atr_window
        start = max(0, i - w + 1)
        self._atr[i] = np.mean(self._bar_range[start : i + 1])

    # ==================================================
    # Snapshot (pure read)
    # ==================================================
    def snapshot(self, i: int):
        n = len(self._close)
        if i >= n:
            i = n - 1  # ✅ clamp index (CRITICAL)

        vwap = self._vwap[i]
        close = self._close[i]

        return {
            "vwap_dev": (close - vwap) / vwap,
            "vol_weight": (
                self._vol[i] / self._vol_ma[i]
                if not np.isnan(self._vol_ma[i]) and self._vol_ma[i] > 0
                else 1.0
            ),
            "bar_range": self._bar_range[i],
            "avg_range": self._avg_range[i],
            "atr": self._atr[i],
        }
