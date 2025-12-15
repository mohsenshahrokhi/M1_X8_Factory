# nds/market_state.py

import numpy as np


class MarketStateEngine:
    """
    Phase‑8.2 — Market State Engine
    --------------------------------
    Determines structural state of the market.
    NO trading decisions here.
    """

    def __init__(
        self,
        compression_cap: float = 2.5,
        expansion_cap: float = 2.5,
        vwap_pressure_threshold: float = 1.5,
    ):
        self.compression_cap = compression_cap
        self.expansion_cap = expansion_cap
        self.vwap_pressure_threshold = vwap_pressure_threshold

    def evaluate(
        self,
        *,
        vwap_dev: float,
        bar_range: float,
        avg_range: float,
        atr: float,
        vol_weight: float,
        stress_score: float,
        regime: str,
    ) -> dict:

        # -----------------------
        # Safety
        # -----------------------
        if avg_range <= 0 or bar_range <= 0:
            return self._warmup_state()

        # -----------------------
        # Compression / Expansion
        # -----------------------
        compression = np.clip(
            avg_range / bar_range,
            0.0,
            self.compression_cap
        )

        expansion = np.clip(
            bar_range / avg_range,
            0.0,
            self.expansion_cap
        )

        # -----------------------
        # Pressure
        # -----------------------
        if vwap_dev > self.vwap_pressure_threshold:
            pressure = "BUY"
        elif vwap_dev < -self.vwap_pressure_threshold:
            pressure = "SELL"
        else:
            pressure = "NEUTRAL"

        # -----------------------
        # Stability
        # -----------------------
        norm_dev = min(abs(vwap_dev) / self.vwap_pressure_threshold, 1.0)

        regime_factor = {
            "TREND": 0.9,
            "RANGE": 1.0,
            "NEUTRAL": 0.8
        }.get(regime, 0.7)

        stability = (
            (1.0 - stress_score) *
            (1.0 - norm_dev) *
            regime_factor
        )

        stability = float(np.clip(stability, 0.0, 1.0))

        # -----------------------
        # Final State Label
        # -----------------------
        if regime == "RANGE" and compression > 1.2:
            state = "RANGE_COMPRESSION"
        elif regime == "RANGE" and expansion > 1.2:
            state = "RANGE_EXPANSION"
        elif regime == "TREND":
            state = "TREND_ACTIVE"
        else:
            state = "UNSTABLE"

        return {
            "state": state,
            "structure": regime,
            "pressure": pressure,
            "compression": round(compression, 2),
            "expansion": round(expansion, 2),
            "stability": round(stability, 2),
        }

    def _warmup_state(self):
        return {
            "state": "WARMUP",
            "structure": "UNKNOWN",
            "pressure": "NEUTRAL",
            "compression": 0.0,
            "expansion": 0.0,
            "stability": 0.0,
        }
