import numpy as np


class SmartCohesionAnalyzer:
    def __init__(self):
        self.recent_closes = []

    def compute(self, close_price):
        self.recent_closes.append(close_price)
        if len(self.recent_closes) > 20:
            self.recent_closes.pop(0)

        if len(self.recent_closes) < 5:
            return 0.0

        # Cohesion: inverse of volatility
        arr = np.array(self.recent_closes)
        vol = np.std(arr)

        if vol == 0:
            return 1.0

        cohesion = 1.0 / (1.0 + vol)
        return round(float(cohesion), 4)
