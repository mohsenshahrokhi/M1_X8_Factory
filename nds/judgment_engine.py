from dataclasses import dataclass


@dataclass
class JudgmentVerdict:
    accept: bool
    allowed_styles: list
    confidence_score: float
    time_sensitivity: str
    explanation: str


class JudgmentEngine:
    """
    Phase-8.5 Judgment Engine
    -------------------------
    Role:
    - Decide IF trading is allowed
    - Decide WHAT trading style is allowed
    - Assign confidence score (0.0 → 1.0)
    """

    def evaluate(
        self,
        *,
        vwap_dev: float,
        regime: str,
        stress: float,
        bar_range: float,
        avg_range: float,
    ) -> JudgmentVerdict:

        explanation = []
        confidence = 0.0
        allowed_styles = []

        # --------------------------------------------------
        # HARD STRESS BLOCK
        # --------------------------------------------------
        if stress >= 0.85:
            return JudgmentVerdict(
                accept=False,
                allowed_styles=["NO_TRADE"],
                confidence_score=0.0,
                time_sensitivity="HIGH",
                explanation="Stress too high"
            )

        # --------------------------------------------------
        # REGIME LOGIC
        # --------------------------------------------------
        if regime == "TREND":

            if vwap_dev > 0:
                confidence += 0.5
                allowed_styles.append("LONG_TREND")
                explanation.append("Positive VWAP trend")

        elif regime == "RANGE":

            if abs(vwap_dev) < 0.004:
                confidence += 0.3
                allowed_styles.append("LONG_MEAN")
                explanation.append("Mean reversion zone")

        # --------------------------------------------------
        # VOLATILITY FILTER
        # --------------------------------------------------
        if bar_range > avg_range * 1.8:
            confidence -= 0.2
            explanation.append("Excess volatility")

        # --------------------------------------------------
        # STRESS MODULATION
        # --------------------------------------------------
        if stress < 0.35:
            confidence += 0.2
        elif stress > 0.65:
            confidence -= 0.3
            explanation.append("Stress drag")

        # --------------------------------------------------
        # FINAL DECISION
        # --------------------------------------------------
        if confidence >= 0.55 and allowed_styles:
            accept = True
        else:
            accept = False
            allowed_styles = ["NO_TRADE"]

        return JudgmentVerdict(
            accept=accept,
            allowed_styles=allowed_styles,
            confidence_score=round(max(confidence, 0.0), 2),
            time_sensitivity="NORMAL",
            explanation=" | ".join(explanation) or "Low confidence"
        )
