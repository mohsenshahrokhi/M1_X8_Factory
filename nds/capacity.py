class CapacityEngine:
    """
    Phase‑8.4 Capacity Engine
    ------------------------
    Measures market's risk absorption capacity
    """

    def evaluate(self, *args, **kwargs):
        """
        Contract‑Safe evaluate
        Accepts full NDS context safely
        """

        market_state = kwargs.get("market_state", {})
        pressure = kwargs.get("pressure", {})
        stress = kwargs.get("stress")
        regime = kwargs.get("regime")

        # ---- Extract signals safely ----
        capacity = 1.0

        # Market structure penalty
        if isinstance(market_state, dict):
            if market_state.get("state") in ("RANGE_COMPRESSION", "BREAKOUT_RISK"):
                capacity *= 0.7

        # Pressure penalty
        if isinstance(pressure, dict):
            p = pressure.get("pressure", 0.0)
            capacity *= max(0.2, 1.0 - p)

        # Stress penalty
        if stress is not None:
            capacity *= max(0.1, 1.0 - stress)

        # Regime adjustment
        if regime in ("RANGE", "CHOP"):
            capacity *= 0.8

        capacity = float(min(1.0, max(0.05, capacity)))

        return {
            "capacity": capacity,
            "state": market_state.get("state", "UNKNOWN"),
            "regime": regime,
        }
