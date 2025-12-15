# exit_engine/m15_trend_exit_detector.py
# =====================================
# Phase‑9C : M15 Trend Exit Detector
# Generates ExitWarning ONLY (No Execution)

from typing import Dict
from exit_engine.contracts import ExitWarning, ExitSignalType


class M15TrendExitDetector:
    """
    High‑timeframe exit warning detector.
    Stateless – deterministic – no execution side‑effects.
    """

    def __init__(
        self,
        min_confidence: float = 0.55,
        weakening_slope_drop: float = 0.35,
        reversal_slope_flip: float = 0.0,
        max_vwap_dev: float = 0.0015
    ):
        self.min_confidence = min_confidence
        self.weakening_slope_drop = weakening_slope_drop
        self.reversal_slope_flip = reversal_slope_flip
        self.max_vwap_dev = max_vwap_dev

    # ---------------------------------------------------------------------
    # Main Interface
    # ---------------------------------------------------------------------

    def evaluate(
        self,
        structure_ctx: Dict,
        vwap_ctx: Dict,
        fractal_ctx: Dict,
        side: str
    ) -> ExitWarning:
        """
        structure_ctx : output of structure / trend analyzer (M15)
        vwap_ctx      : VWAP metrics (deviation, slope)
        fractal_ctx   : fractal / cycle stability info
        side          : "LONG" | "SHORT"
        """

        # --- Extract core metrics ---
        slope_now = structure_ctx.get("slope_norm", 0.0)
        slope_prev = structure_ctx.get("slope_prev", slope_now)
        expansion = structure_ctx.get("expansion", 1.0)
        structure = structure_ctx.get("regime", "UNKNOWN")

        vwap_dev = abs(vwap_ctx.get("deviation", 0.0))
        fractal_stability = fractal_ctx.get("stability", 1.0)

        # --- Trend weakening ---
        slope_drop = abs(slope_prev - slope_now)

        weakening = (
            slope_drop > self.weakening_slope_drop and
            expansion < 1.0 and
            fractal_stability < 0.7
        )

        # --- Trend reversal ---
        reversal = False
        if side == "LONG":
            reversal = slope_now < self.reversal_slope_flip
        elif side == "SHORT":
            reversal = slope_now > -self.reversal_slope_flip

        # --- Distribution detection ---
        distribution = (
            expansion < 1.0 and
            vwap_dev < self.max_vwap_dev and
            structure in ("TREND", "TREND_WEAK")
        )

        # --- Confidence scoring ---
        confidence = 0.0
        if weakening:
            confidence += 0.4
        if reversal:
            confidence += 0.4
        if distribution:
            confidence += 0.2

        confidence = min(confidence, 1.0)

        # --- Signal decision ---
        if confidence < self.min_confidence:
            return ExitWarning(
                active=False,
                signal_type=ExitSignalType.NONE,
                confidence=confidence,
                reason="M15: Trend stable"
            )

        if reversal:
            sig = ExitSignalType.REVERSAL
            reason = "M15: Trend reversal detected"
        elif distribution:
            sig = ExitSignalType.DISTRIBUTION
            reason = "M15: Distribution / absorption detected"
        else:
            sig = ExitSignalType.WEAKENING
            reason = "M15: Trend weakening detected"

        return ExitWarning(
            active=True,
            signal_type=sig,
            confidence=confidence,
            reason=reason
        )
