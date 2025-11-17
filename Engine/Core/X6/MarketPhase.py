# Engine/Core/X6/MarketPhase.py

class MarketPhase:
    def detect_phase(self, trend_strength, volatility):
        if trend_strength > 0.7 and volatility < 0.02:
            return "strong_trend"
        if trend_strength < 0.3 and volatility < 0.01:
            return "range"
        if volatility > 0.03:
            return "volatile"
        return "transition"
