# Engine/Core/X6/FeatureBuilder.py

class FeatureBuilder:
    def build_vector(
        self,
        momentum,
        volume_pressure,
        order_flow,
        trend_strength,
        volatility,
        coherence,
        cycle_strength,
        risk_factor,
        rally_prob,
        total_score
    ):
        fv = [
            momentum,
            volume_pressure,
            order_flow,
            trend_strength,
            volatility,
            coherence,
            cycle_strength,
            risk_factor,
            rally_prob,
            total_score,

            # مشتق‌ها
            momentum * volatility,
            trend_strength * coherence,
            cycle_strength * rally_prob,

            # نرمالیزه‌ها
            min(1, abs(momentum)),
            min(1, abs(order_flow)),
            min(1, volatility * 10),
        ]

        return fv
