# Engine/Core/X6/ScoringModel.py

class ScoringModel:
    def compute_total_score(
        self, confidence, performance,
        rr_ratio, regime_match,
        liquidity, coherence,
        rally_prob
    ):
        return (
            confidence * 0.25 +
            performance * 0.20 +
            rr_ratio * 0.15 +
            regime_match * 0.15 +
            liquidity * 0.10 +
            coherence * 0.10 +
            rally_prob * 0.05
        )
