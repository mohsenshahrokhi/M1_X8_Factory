
class DynamicTradeAllocator:
    def __init__(self, base_lot=0.01, max_lot=1.0):
        self.base_lot = base_lot
        self.max_lot = max_lot

    # ---------------------------------------------------------
    # ✅ Fully compatible allocate() with AutoEngine_M1
    # Supports both:
    # allocate(momentum, order_flow, score, cohesion)
    # allocate(direction=..., momentum=..., order_flow=..., score=..., cohesion=...)
    # ---------------------------------------------------------
    def allocate(self, *args, **kwargs):

        # If called with positional arguments (old engine mode)
        if len(args) == 4:
            momentum, order_flow, score, cohesion = args
            direction = None

        # Called with named parameters (new engine mode)
        else:
            momentum = kwargs.get("momentum", 0.0)
            order_flow = kwargs.get("order_flow", 0.0)
            score = kwargs.get("score", 0.0)
            cohesion = kwargs.get("cohesion", 0.0)
            direction = kwargs.get("direction", None)

        # ---------------------------------------------------------
        # ✅ Compute signal strength (weighted)
        # ---------------------------------------------------------
        strength = (
            (momentum * 0.4) +
            (order_flow * 0.3) +
            (score * 0.2) +
            (cohesion * 0.1)
        )

        # Clamp strength to [0,1]
        strength = max(0.0, min(1.0, strength))

        # ---------------------------------------------------------
        # ✅ Compute dynamic lot size
        # ---------------------------------------------------------
        lot = self.base_lot + strength * (self.max_lot - self.base_lot)
        lot = round(lot, 2)

        # ---------------------------------------------------------
        # ✅ Direction handling
        # ---------------------------------------------------------
        if direction == "buy":
            return {"lot": lot, "type": "buy"}

        if direction == "sell":
            return {"lot": lot, "type": "sell"}

        # ---------------------------------------------------------
        # ✅ Safe fallback (HOLD)
        # ---------------------------------------------------------
        return {"lot": lot, "type": "hold"}
