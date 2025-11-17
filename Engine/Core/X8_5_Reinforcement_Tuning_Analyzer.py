import numpy as np


class ReinforcementTuningAnalyzer:
    def __init__(self):
        pass

    # ---------------------------------------------------------
    # ✅ Compute market stability
    # AutoEngine passes: (momentum, order_flow)
    # ---------------------------------------------------------
    def compute_stability(self, momentum, order_flow):
        momentum = float(momentum)
        order_flow = float(order_flow)

        # Stability is inverse of market chaos
        chaos = abs(momentum - order_flow)
        stability = 1.0 / (1.0 + chaos)

        return round(float(stability), 4)

    # ---------------------------------------------------------
    # ✅ Compute adjustment based on stability and cohesion
    # AutoEngine calls: compute_adjustment(stability, cohesion)
    # ---------------------------------------------------------
    def compute_adjustment(self, stability, cohesion):
        stability = float(stability)
        cohesion = float(cohesion)

        # Weighted combination
        adjust = (stability * 0.6) + (cohesion * 0.4)

        return round(float(adjust), 4)
