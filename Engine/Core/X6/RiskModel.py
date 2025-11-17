# Engine/Core/X6/RiskModel.py

class RiskModel:
    def compute_risk_factor(self, sharpe, coherence):
        return sharpe * coherence
