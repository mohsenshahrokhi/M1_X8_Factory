# exit_engine/m5_exit_confirmation_gate.py
# ========================================
# Phase‑9C : M5 Exit Confirmation Gate
# Decides EXIT SEVERITY (No Execution)

from typing import Dict
from exit_engine.contracts import (
    ExitWarning,
    ExitConfirmation,
    ExitSeverity,
    ExitSignalType,
)


class M5ExitConfirmationGate:
    """
    Mid‑timeframe exit confirmation layer.
    Takes M15 ExitWarning and decides HOLD / PARTIAL / FULL.
    """

    def __init__(
        self,
        min_confirm_confidence: float = 0.60,
        strong_momentum_threshold: float = -0.25,
        vwap_flip_threshold: float = 0.0,
    ):
        self.min_confirm_confidence = min_confirm_confidence
        self.strong_momentum_threshold = strong_momentum_threshold
        self.vwap_flip_threshold = vwap_flip_threshold

    # ------------------------------------------------------------------
    # Main Interface
    # ------------------------------------------------------------------

    def confirm(
        self,
        warning: ExitWarning,
        structure_ctx: Dict,
        vwap_ctx: Dict,
        momentum_ctx: Dict,
        side: str,
    ) -> ExitConfirmation:
        """
        structure_ctx : M5 structure / swing analysis
        vwap_ctx      : M5 VWAP metrics
        momentum_ctx  : short‑term momentum metrics
        side          : "LONG" | "SHORT"
        """

        # No warning → nothing to confirm
        if not warning.active:
            return ExitConfirmation(
                confirmed=False,
                severity=ExitSeverity.HOLD,
                reason="M5: No exit warning"
            )

        if warning.confidence < self.min_confirm_confidence:
            return ExitConfirmation(
                confirmed=False,
                severity=ExitSeverity.HOLD,
                reason="M5: Warning confidence too low"
            )

        # --- Extract metrics ---
        momentum = momentum_ctx.get("momentum_norm", 0.0)
        structure = structure_ctx.get("regime", "UNKNOWN")
        vwap_slope = vwap_ctx.get("slope", 0.0)

        # --- Directional interpretation ---
        momentum_against = (
            momentum < self.strong_momentum_threshold
            if side == "LONG"
            else momentum > -self.strong_momentum_threshold
        )

        vwap_flip = (
            vwap_slope < self.vwap_flip_threshold
            if side == "LONG"
            else vwap_slope > -self.vwap_flip_threshold
        )

        structure_break = structure in ("BREAK", "RANGE", "DISTRIBUTION")

        # --------------------------------------------------------------
        # FULL EXIT CONDITIONS
        # --------------------------------------------------------------

        if (
            warning.signal_type == ExitSignalType.REVERSAL and
            (momentum_against or structure_break)
        ):
            return ExitConfirmation(
                confirmed=True,
                severity=ExitSeverity.FULL,
                reason="M5: Reversal confirmed by momentum/structure"
            )

        if momentum_against and vwap_flip:
            return ExitConfirmation(
                confirmed=True,
                severity=ExitSeverity.FULL,
                reason="M5: Momentum + VWAP flip against position"
            )

        # --------------------------------------------------------------
        # PARTIAL EXIT CONDITIONS
        # --------------------------------------------------------------

        if warning.signal_type in (
            ExitSignalType.WEAKENING,
            ExitSignalType.DISTRIBUTION,
        ):
            return ExitConfirmation(
                confirmed=True,
                severity=ExitSeverity.PARTIAL,
                reason="M5: Weakening / distribution confirmed"
            )

        # --------------------------------------------------------------
        # DEFAULT HOLD
        # --------------------------------------------------------------

        return ExitConfirmation(
            confirmed=False,
            severity=ExitSeverity.HOLD,
            reason="M5: Conditions insufficient for exit"
        )
