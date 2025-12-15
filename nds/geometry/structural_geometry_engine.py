# nds/geometry/structural_geometry_engine.py

class StructuralGeometryEngine:
    """
    Structural Geometry Engine (Phase‑8.2)

    Responsibility:
    - Describe market geometric condition
    - NO trade decisions
    - NO execution logic

    Philosophy:
    Strategy Suggests | NDS Decides | Execution Obeys
    """

    def evaluate(self, *args, **kwargs):
        """
        Supported call styles:
        - evaluate(context: dict)
        - evaluate(market_state=..., **kwargs)
        - evaluate(vwap_dev=..., bar_range=..., ...)
        """

        # -------------------------------------------------
        # Normalize Context
        # -------------------------------------------------
        if args and isinstance(args[0], dict):
            context = args[0]
        elif "context" in kwargs and isinstance(kwargs["context"], dict):
            context = kwargs["context"]
        else:
            context = dict(kwargs)

        # Optional higher-level state (Phase‑8.3+)
        market_state = context.get("market_state")

        # -------------------------------------------------
        # Geometry Inputs (Required)
        # -------------------------------------------------
        vwap_dev  = float(context.get("vwap_dev", 0.0))
        bar_range = float(context.get("bar_range", 0.0))
        avg_range = float(context.get("avg_range", 1.0))
        atr       = float(context.get("atr", 1.0))
        regime    = context.get("regime", "UNKNOWN")

        # Numerical safety
        avg_range = max(avg_range, 1e-6)
        atr       = max(atr, 1e-6)

        # -------------------------------------------------
        # Core Geometry Metrics
        # -------------------------------------------------
        compression = bar_range / avg_range
        slope_norm  = vwap_dev / atr

        # -------------------------------------------------
        # Structural Stability Logic
        # -------------------------------------------------
        if compression < 0.75 and abs(slope_norm) < 0.8:
            stability = "STABLE"
        elif compression > 1.25:
            stability = "EXPANDING"
        else:
            stability = "TRANSITION"

        # -------------------------------------------------
        # Geometry Descriptor (NO DECISION)
        # -------------------------------------------------
        geometry = {
            "compression": round(compression, 4),
            "slope_norm": round(slope_norm, 4),
            "stability": stability,
            "regime": regime,
        }

        if market_state is not None:
            geometry["market_state"] = market_state

        return geometry
