# exit_engine/m1_exit_executor.py
# ===============================
# Phase‑9C : M1 Exit Executor
# Converts ExitConfirmation → ExitAction
# NO analysis | NO execution | deterministic

from exit_engine.contracts import (
    ExitConfirmation,
    ExitAction,
    ExitSeverity,
    ExitContext,
)


class M1ExitExecutor:
    """
    Final exit execution policy.
    Stateless and side‑effect free.
    """

    def __init__(
        self,
        partial_close_ratio: float = 0.33,
        pnl_protect_threshold: float = 0.0,
    ):
        """
        partial_close_ratio : default scale‑out ratio
        pnl_protect_threshold : minimum unrealized PnL to allow PARTIAL exit
        """
        self.partial_close_ratio = max(0.0, min(partial_close_ratio, 1.0))
        self.pnl_protect_threshold = pnl_protect_threshold

    # ------------------------------------------------------------------
    # Main Interface
    # ------------------------------------------------------------------

    def execute(
        self,
        confirmation: ExitConfirmation,
        ctx: ExitContext,
    ) -> ExitAction:
        """
        Returns an ExitAction to be consumed by ExecutionPolicy.
        """

        # -----------------------------
        # HOLD
        # -----------------------------
        if (
            not confirmation.confirmed or
            confirmation.severity == ExitSeverity.HOLD
        ):
            return ExitAction(
                close=False,
                close_ratio=0.0,
                reason="M1: HOLD – no confirmed exit"
            )

        # -----------------------------
        # PARTIAL EXIT
        # -----------------------------
        if confirmation.severity == ExitSeverity.PARTIAL:

            # Optional PnL protection (institutional behavior)
            if ctx.unrealized_pnl < self.pnl_protect_threshold:
                return ExitAction(
                    close=False,
                    close_ratio=0.0,
                    reason="M1: PARTIAL blocked – PnL below protection threshold"
                )

            return ExitAction(
                close=True,
                close_ratio=self.partial_close_ratio,
                reason="M1: PARTIAL exit approved"
            )

        # -----------------------------
        # FULL EXIT
        # -----------------------------
        if confirmation.severity == ExitSeverity.FULL:
            return ExitAction(
                close=True,
                close_ratio=1.0,
                reason="M1: FULL exit approved"
            )

        # -----------------------------
        # Fallback (should never hit)
        # -----------------------------
        return ExitAction(
            close=False,
            close_ratio=0.0,
            reason="M1: Undefined exit state"
        )
