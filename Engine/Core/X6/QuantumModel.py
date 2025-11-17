# Engine/Core/X6/QuantumModel.py

class QuantumModel:
    def __init__(self):
        pass

    def compute_rally_probability(self, momentum, volume_pressure, order_flow):
        return (
            momentum * 0.4 +
            volume_pressure * 0.3 +
            order_flow * 0.3
        )
