class CohesionRewardIntegrator:
    def __init__(self):
        pass

    # ---------------------------------------------------------
    # ✅ Fully synced with AutoEngine (3-argument version)
    # integrate(market_score, cohesion, stability)
    # ---------------------------------------------------------
    def integrate(self, market_score, cohesion, stability):
        market_score = float(market_score)
        cohesion = float(cohesion)
        stability = float(stability)

        # Simplified and stable reward formula
        reward = (
            (market_score * 0.50) +
            (cohesion * 0.30) +
            (stability * 0.20)
        )

        return round(float(reward), 4)
