# nds/decision_engine.py

from dataclasses import dataclass


@dataclass
class DecisionResult:
    """
    Final NDS Decision Object
    -------------------------
    This is what Orchestrator / Execution layer should read.
    """
    accept: bool
    allowed_styles: list
    confidence: float
    explanation: str


class DecisionEngine:
    """
    Meta Decision Engine (Phase‑8.x → Phase‑9 bridge)

    Role:
    - Merge low-level engines with Judgment verdict
    - Apply final veto logic
    """

    def evaluate(
        self,
        *,
        market,
        structure,
        pressure,
        capacity,
        judgment,
    ) -> DecisionResult:

        # -----------------------------
        # Hard vetoes
        # -----------------------------
        if not judgment.accept:
            return DecisionResult(
                accept=False,
                allowed_styles=["NO_TRADE"],
                confidence=0.0,
                explanation="Judgment rejected trade"
            )

        # -----------------------------
        # Confidence Fusion
        # -----------------------------
        confidence = judgment.confidence_score

        # Optional modulation (future-safe)
        # These attrs are soft assumed; safe getattr
        confidence += 0.05 if getattr(structure, "coherent", False) else 0.0
        confidence -= 0.10 if getattr(pressure, "exhausted", False) else 0.0
        confidence -= 0.15 if getattr(capacity, "thin", False) else 0.0

        confidence = max(round(confidence, 2), 0.0)

        # -----------------------------
        # Final Gate
        # -----------------------------
        if confidence < 0.55:
            return DecisionResult(
                accept=False,
                allowed_styles=["NO_TRADE"],
                confidence=confidence,
                explanation="Confidence below threshold"
            )

        return DecisionResult(
            accept=True,
            allowed_styles=judgment.allowed_styles,
            confidence=confidence,
            explanation="Decision accepted"
        )
