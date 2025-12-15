# core/vwap_regime.py

import numpy as np
import pandas as pd


class VWAPRegimeDetector:
    """
    Symbol‑agnostic VWAP regime detector.
    Fully backward‑compatible:
      • detect(df)
      • detect(vwap_dev, vol_weight, bar_range, avg_range)
      • detect(vwap_dev=..., vol_weight=..., bar_range=..., avg_range=...)

    Phase‑7 / Phase‑8 SAFE
    """

    def __init__(self, window: int = 100, atr_window: int = 14):
        self.window = window
        self.atr_window = atr_window

        # ─────────────────────────────────────────────
        # Regime thresholds (CRITICAL)
        # ─────────────────────────────────────────────
        self.trend_threshold = 2.5
        self.range_threshold = 1.0

    # ─────────────────────────────────────────────
    # Main API (CANONICAL)
    # ─────────────────────────────────────────────
    def detect(self, *args, **kwargs):
        """
        Supported contracts:
        - detect(df)
        - detect(vwap_dev, vol_weight, bar_range, avg_range)
        - detect(
            vwap_dev=...,
            vol_weight=...,
            bar_range=...,
            avg_range=...
          )

        Returns:
        - "TREND" | "RANGE" | "NEUTRAL" | "WARMUP"
        """

        # ─────────────────────────────────────────────
        # MODE 1: Keyword‑based (Phase‑8 default)
        # ─────────────────────────────────────────────
        if kwargs:
            vwap_dev = kwargs.get("vwap_dev")
            vol_weight = kwargs.get("vol_weight")
            bar_range = kwargs.get("bar_range")
            avg_range = kwargs.get("avg_range")

        # ─────────────────────────────────────────────
        # MODE 2: DF‑based API
        # ─────────────────────────────────────────────
        elif len(args) == 1:
            df = args[0]

            if df is None or getattr(df, "empty", True):
                return "WARMUP"

            required = {"vwap_dev", "vol_weight", "bar_range", "avg_range"}
            if not required.issubset(df.columns):
                return "WARMUP"

            vwap_dev = float(df["vwap_dev"].iloc[-1])
            vol_weight = float(df["vol_weight"].iloc[-1])
            bar_range = float(df["bar_range"].iloc[-1])
            avg_range = float(df["avg_range"].iloc[-1])

        # ─────────────────────────────────────────────
        # MODE 3: Positional legacy API
        # ─────────────────────────────────────────────
        elif len(args) == 4:
            vwap_dev, vol_weight, bar_range, avg_range = args

        else:
            raise TypeError(
                "VWAPRegimeDetector.detect expects:\n"
                "  • detect(df)\n"
                "  • detect(vwap_dev, vol_weight, bar_range, avg_range)\n"
                "  • detect(vwap_dev=..., vol_weight=..., bar_range=..., avg_range=...)"
            )

        # ─────────────────────────────────────────────
        # Safety / Warmup
        # ─────────────────────────────────────────────
        if avg_range is None or avg_range <= 0 or np.isnan(avg_range):
            return "WARMUP"

        # ─────────────────────────────────────────────
        # Regime logic
        # ─────────────────────────────────────────────
        abs_dev = abs(vwap_dev)

        # Trend
        if abs_dev > self.trend_threshold and bar_range > avg_range:
            return "TREND"

        # Range
        if abs_dev < self.range_threshold:
            return "RANGE"

        return "NEUTRAL"
