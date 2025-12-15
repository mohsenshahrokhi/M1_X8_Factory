# =====================================================
# execution/stop_engine.py
# FINAL – TRUE O(1) / NO QUANTILE
# =====================================================

import numpy as np


class StopEngine:
    """
    Institutional Stop Engine – FINAL
    ---------------------------------
    ✅ NO percentile / quantile
    ✅ True O(1)
    ✅ Numerically stable
    """

    def __init__(
        self,
        alpha: float = 0.05,        # EWMA tail speed
        min_samples: int = 50,
    ):
        self.alpha = alpha
        self.min_samples = min_samples

        self._ewma_tail = None
        self._samples = 0

    # ==================================================
    # MAIN API
    # ==================================================
    def compute(
        self,
        direction: str,
        entry_price: float,
        atr: float,
        stress_score: float,
        nds_slope: float,
        returns: np.ndarray,
    ):
        # ---------- SAFETY ----------
        if returns is None or len(returns) < self.min_samples:
            return entry_price - atr, "ATR_FALLBACK"

        # ---------- UPDATE EWMA CVAR ----------
        self._update_tail(returns[-1])

        # ---------- CVAR STOP ----------
        if self._ewma_tail is not None:
            cvar_stop = entry_price * (1.0 + self._ewma_tail)
        else:
            cvar_stop = entry_price - atr

        # ---------- FINAL STOP ----------
        if direction == "LONG":
            stop_price = min(entry_price - atr, cvar_stop)
        else:
            stop_price = max(entry_price + atr, cvar_stop)

        return stop_price, "EWMA_CVAR"

    # ==================================================
    # O(1) TAIL ESTIMATOR
    # ==================================================
    def _update_tail(self, r: float):
        """
        Approximate left tail (losses only)
        """
        if r >= 0.0:
            return

        self._samples += 1

        if self._ewma_tail is None:
            self._ewma_tail = r
        else:
            self._ewma_tail = (
                (1.0 - self.alpha) * self._ewma_tail
                + self.alpha * r
            )
