class PressureEngine:
    """
    Phase‑8.3 Pressure Engine
    ------------------------
    Order‑Flow × Volume × Momentum × Market State
    """

    def evaluate(self, *args, **kwargs):
        """
        Contract‑Safe evaluate
        Accepts both positional & keyword context
        """

        # ✅ Extract context safely
        market_state = kwargs.get("market_state")
        stress = kwargs.get("stress")
        regime = kwargs.get("regime")

        vwap_dev = kwargs.get("vwap_dev")
        vol_weight = kwargs.get("vol_weight")
        bar_range = kwargs.get("bar_range")

        # ---- Temporary / LOG‑ONLY SAFE DEFAULTS ----
        if market_state is None:
            market_state = {"state": "UNKNOWN", "stability": 0.5}

        # ---- Simple baseline pressure (Phase‑8.3 draft) ----
        pressure = 0.0

        if vwap_dev is not None:
            pressure += abs(vwap_dev)

        if vol_weight is not None:
            pressure *= (1.0 + vol_weight)

        if stress is not None:
            pressure *= (1.0 + stress)

        return {
            "pressure": float(min(1.0, pressure)),
            "state": market_state.get("state"),
            "confidence": market_state.get("stability", 0.5),
        }
