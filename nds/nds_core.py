from collections import deque
from copy import deepcopy

from nds.market_state import MarketStateEngine
from nds.geometry import GeometryEngine
from nds.pressure import PressureEngine
from nds.capacity import CapacityEngine
from nds.judgment_engine import JudgmentEngine
from nds.decision_engine import DecisionEngine
from nds.verdict import NDSVerdictEnvelope

from config.settings import (
    # Warm‑Up
    WARMUP_MODE,
    WARMUP_JUDGMENT_DEBUG,

    # Phase‑9B
    PHASE_9B_ENABLED,
    MIN_TREND_EXPANSION,
    MIN_VWAP_DEV,
    MAX_TRADE_STRESS,
)


class NDSCore:
    """
    NDS Core — Phase‑9A / Phase‑9B (Adaptive, Production‑Safe)

    Responsibilities:
    - Multi‑layer market evaluation
    - Contract‑safe verdict generation
    - Adaptive Phase‑9B override (NO mutation)
    """

    def __init__(self, logger=None):
        # ===== Engines =====
        self.market_state_engine = MarketStateEngine()
        self.geometry_engine = GeometryEngine()
        self.pressure_engine = PressureEngine()
        self.capacity_engine = CapacityEngine()

        self.judgment_engine = JudgmentEngine()      # Phase‑8.x
        self.decision_engine = DecisionEngine()      # Phase‑9A

        # ===== Adaptive Confirmation Memory =====
        self._confirm_memory = deque(maxlen=5)

        # ===== Logging =====
        self.logger = logger
        self._warmup_tick = 0

    # --------------------------------------------------
    # Adaptive confirmation bars (volatility aware)
    # --------------------------------------------------
    def _adaptive_confirmation_bars(self, volatility_norm: float) -> int:
        bars = round(1 + volatility_norm * 2)
        return max(1, min(3, bars))

    # ==================================================
    # Core Evaluation
    # ==================================================
    def evaluate(self, context: dict) -> NDSVerdictEnvelope:

        # ---------- Market State ----------
        market = self.market_state_engine.evaluate(
            vwap_dev=context["vwap_dev"],
            bar_range=context["bar_range"],
            avg_range=context["avg_range"],
            atr=context["atr"],
            vol_weight=context["vol_weight"],
            stress_score=context["stress"],
            regime=context["regime"],
        )

        # ---------- Geometry / Structure ----------
        structure = self.geometry_engine.evaluate(
            market_state=market,
            vwap_dev=context["vwap_dev"],
            bar_range=context["bar_range"],
            avg_range=context["avg_range"],
            atr=context["atr"],
            regime=context["regime"],
        )

        # ---------- Pressure ----------
        pressure = self.pressure_engine.evaluate(
            market_state=market
        )

        # ---------- Capacity ----------
        capacity = self.capacity_engine.evaluate(
            market_state=market
        )

        # ---------- Judgment ----------
        judgment = self.judgment_engine.evaluate(
            vwap_dev=context["vwap_dev"],
            regime=context["regime"],
            stress=context["stress"],
            bar_range=context["bar_range"],
            avg_range=context["avg_range"],
        )

        # ---------- Decision (Phase‑9A) ----------
        base_decision = self.decision_engine.evaluate(
            market=market,
            structure=structure,
            pressure=pressure,
            capacity=capacity,
            judgment=judgment,
        )

        decision = base_decision

        # ==================================================
        # Phase‑9B — Adaptive Conditional Override (SAFE)
        # ==================================================
        if PHASE_9B_ENABLED and not base_decision.accept:

            trend_type = structure.get("structure")           # "TREND" | ...
            trend_dir = structure.get("trend_direction")     # "UP" | "DOWN"
            expansion = structure.get("expansion", 0.0)

            vwap_dev = abs(context["vwap_dev"])
            stress = context["stress"]
            volatility = context.get("volatility_norm", 0.0)

            hard_gate_passed = (
                trend_type == "TREND"
                and trend_dir in ("UP", "DOWN")
                and expansion >= MIN_TREND_EXPANSION
                and vwap_dev >= MIN_VWAP_DEV
                and stress <= MAX_TRADE_STRESS
            )

            # ---- Reset confirmation memory if gate fails ----
            if not hard_gate_passed:
                self._confirm_memory.clear()

            if hard_gate_passed:
                needed = self._adaptive_confirmation_bars(volatility)

                self._confirm_memory.append(trend_dir)
                aligned = [d for d in self._confirm_memory if d == trend_dir]

                if len(aligned) >= needed:
                    decision = deepcopy(base_decision)
                    decision.accept = True
                    decision.allowed_styles = (
                        ["TREND_LONG"] if trend_dir == "UP"
                        else ["TREND_SHORT"]
                    )
                    decision.confidence = round(
                        min(0.70 + expansion * 0.10, 0.95), 2
                    )
                    decision.explanation = (
                        f"Phase‑9B adaptive confirmation "
                        f"{len(aligned)}/{needed}"
                    )
                else:
                    decision = deepcopy(base_decision)
                    decision.explanation = (
                        f"Phase‑9B waiting confirmation "
                        f"{len(aligned)}/{needed}"
                    )
            else:
                decision = deepcopy(base_decision)
                decision.explanation = "Phase‑9B hard‑gate rejection"

        # ==================================================
        # Verdict Envelope (IMMUTABLE CONTRACT)
        # ==================================================
        verdict = NDSVerdictEnvelope(
            market_state=market,
            structure_state=structure,
            pressure_state=pressure,
            capacity_state=capacity,
            decision=decision,
        )

        # ---------- Logger (SAFE) ----------
        if self.logger:
            self.logger.info("[NDS VERDICT] %s", verdict)

        # ---------- Warm‑Up Debug (RATE‑LIMITED) ----------
        if WARMUP_MODE and WARMUP_JUDGMENT_DEBUG:
            if self._warmup_tick % 200 == 0:
                print("🧪 [WARMUP][NDS SNAPSHOT]")
                print("CONTEXT:", context)
                print("MARKET:", market)
                print("STRUCTURE:", structure)
                print("PRESSURE:", pressure)
                print("CAPACITY:", capacity)
                print("DECISION:", decision)
                print("-" * 60)
            self._warmup_tick += 1

        return verdict
