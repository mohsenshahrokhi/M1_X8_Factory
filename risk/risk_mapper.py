from config.settings import FORCE_TRADE_MODE, FORCE_MIN_RISK_USD


class RiskBudgetMapper:
    """
    Phase‑5: Institutional Risk Budget Mapper
    -----------------------------------------
    Converts Market Context → Risk Allocation
    """

    BASE_RISK = 0.01  # 1% of equity

    STRESS_MULT = {
        "LOW_STRESS": 1.00,
        "MED_STRESS": 0.60,
        "HIGH_STRESS": 0.25,
        "PANIC": 0.00,
        "WARMUP": 0.00
    }

    REGIME_MULT = {
        "TREND": 1.20,
        "ACCUMULATION": 0.90,
        "DISTRIBUTION": 0.70,
        "MEAN_REVERSION": 0.55,
        "UNKNOWN": 0.00
    }

    def __init__(self, min_risk=0.0, max_risk=0.015):
        self.min_risk = min_risk
        self.max_risk = max_risk

    def _vwap_clamp(self, vwap_dev_abs: float) -> float:
        if vwap_dev_abs < 0.0003:
            return 1.00
        elif vwap_dev_abs < 0.0007:
            return 0.80
        elif vwap_dev_abs < 0.0012:
            return 0.50
        else:
            return 0.25

    def _score_to_state(self, score: float) -> str:
        if score == 0.0:
            return "WARMUP"
        elif score <= 0.3:
            return "LOW_STRESS"
        elif score <= 0.6:
            return "MED_STRESS"
        elif score <= 0.9:
            return "HIGH_STRESS"
        else:
            return "PANIC"

    def compute(
        self,
        equity: float,
        stress_score: float,
        regime: str,
        vwap_dev: float
    ) -> dict:

        stress_state = self._score_to_state(stress_score)

        stress_mult = self.STRESS_MULT.get(stress_state, 0.0)
        regime_mult = self.REGIME_MULT.get(regime, 0.0)
        vwap_mult = self._vwap_clamp(abs(vwap_dev))

        raw_risk = (
            equity
            * self.BASE_RISK
            * stress_mult
            * regime_mult
            * vwap_mult
        )

        risk_final = max(
            self.min_risk,
            min(raw_risk, equity * self.max_risk)
        )

        # ─────────────────────────────────────────────
        # FORCE TRADE MODE (Phase‑7 plumbing test only)
        # ─────────────────────────────────────────────
        if FORCE_TRADE_MODE and risk_final <= 0:
            risk_final = FORCE_MIN_RISK_USD

        return {
            "risk_amount": round(risk_final, 2),
            "stress_mult": stress_mult,
            "regime_mult": regime_mult,
            "vwap_mult": vwap_mult
        }
