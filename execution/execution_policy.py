# =====================================================
# execution/execution_policy.py
# =====================================================

from dataclasses import dataclass


@dataclass
class ExecutionPolicy:
    trade_allowed: bool
    side: str | None
    reason: str


class ExecutionPolicyMapper:
    """
    Phase‑9A: NDS → Execution Policy
    --------------------------------
    Contract‑Safe:
    Input  → DecisionResult
    Output → ExecutionPolicy
    """

    def map(self, *, nds_result, confidence_threshold: float) -> ExecutionPolicy:
        """
        Parameters
        ----------
        nds_result : DecisionResult
            Output of NDSCore.evaluate(...).decision
        confidence_threshold : float
            Minimum confidence required to allow execution
        """

        # ✅ nds_result IS DecisionResult
        if not nds_result.accept:
            return ExecutionPolicy(
                trade_allowed=False,
                side=None,
                reason="NDS rejected trade",
            )

        if nds_result.confidence < confidence_threshold:
            return ExecutionPolicy(
                trade_allowed=False,
                side=None,
                reason=f"Confidence too low ({nds_result.confidence:.2f})",
            )

        # Phase‑9A restriction: Long‑only
        if "TREND_LONG" not in nds_result.allowed_styles:
            return ExecutionPolicy(
                trade_allowed=False,
                side=None,
                reason="Style not allowed",
            )
            

        return ExecutionPolicy(
            trade_allowed=True,
            side="LONG",
            reason="NDS approval",
        )
