class MarketWeightedSignalAnalyzer:
    def __init__(self):
        pass

    # -------------------------------------------------------
    # ✅ Smart compute (accepts float, list, array)
    # -------------------------------------------------------
    def compute(self, close_price, volume=None):
        try:
            # --- normalize close_price ---
            if isinstance(close_price, (float, int)):
                close_price = [close_price]
            if "numpy" in str(type(close_price)):
                try:
                    close_price = close_price.tolist()
                except:
                    close_price = [float(close_price)]

            # --- normalize volume ---
            if volume is None:
                volume = [0] * len(close_price)

            if isinstance(volume, (float, int)):
                volume = [volume]
            if "numpy" in str(type(volume)):
                try:
                    volume = volume.tolist()
                except:
                    volume = [float(volume)]

            momentum = self.compute_momentum(close_price)
            volume_pressure = self.compute_volume_pressure(volume)
            order_flow = self.compute_order_flow(close_price)
            score = self.compute_market_score(momentum, volume_pressure, order_flow)
            direction = self.compute_direction(momentum, order_flow)

            return {
                "momentum": momentum,
                "volume_pressure": volume_pressure,
                "order_flow": order_flow,
                "market_score": score,
                "direction": direction,
            }

        except Exception as e:
            print(f"❌ MarketWeightedSignalAnalyzer Error: {e}")
            return {
                "momentum": 0,
                "volume_pressure": 0,
                "order_flow": 0,
                "market_score": 0,
                "direction": "hold",
            }

    # ----------------------------------------
    # ✅ Sub‑methods
    # ----------------------------------------
    def compute_momentum(self, close_price):
        if len(close_price) < 2:
            return 0
        return float(close_price[-1] - close_price[-2])

    def compute_volume_pressure(self, volume):
        if len(volume) < 2:
            return 0
        return float(volume[-1] - volume[-2])

    def compute_order_flow(self, close_price):
        if len(close_price) < 3:
            return 0
        return float((close_price[-1] - close_price[-2]) + (close_price[-2] - close_price[-3]))

    def compute_market_score(self, momentum, volume_pressure, order_flow):
        return float(momentum * 0.4 + volume_pressure * 0.3 + order_flow * 0.3)

    def compute_direction(self, momentum, order_flow):
        if momentum > 0 and order_flow > 0:
            return "buy"
        elif momentum < 0 and order_flow < 0:
            return "sell"
        else:
            return "hold"
