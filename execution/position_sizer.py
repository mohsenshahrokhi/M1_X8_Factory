class PositionSizer:
    def __init__(self, point_value: float, min_size: float = 0.01):
        self.point_value = point_value
        self.min_size = min_size

    def size(self, risk_budget, entry_price, stop_price):
        risk_per_unit = abs(entry_price - stop_price) * self.point_value

        if risk_per_unit <= 0:
            return 0.0

        raw_size = risk_budget / risk_per_unit

        if raw_size < self.min_size:
            return 0.0

        return round(raw_size, 2)
    
    # اضافه کردن متد compute برای سازگاری
    def compute(self, risk_budget, entry_price, stop_price, regime, stress_score, nds_slope):
        """
        برای سازگاری با orchestrator
        """
        size = self.size(risk_budget, entry_price, stop_price)
        
        risk_per_unit = abs(entry_price - stop_price) * self.point_value
        effective_risk = size * risk_per_unit
        
        return {
            "size": size,
            "effective_risk": round(effective_risk, 2),
            "reason": f"Regime: {regime}, Stress: {stress_score:.2f}, Slope: {nds_slope:.5f}"
        }