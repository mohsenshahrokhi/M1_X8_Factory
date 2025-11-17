# Engine/Core/X6/X6_Master.py

from Engine.Core.X6.QuantumModel import QuantumModel
from Engine.Core.X6.MarketPhase import MarketPhase
from Engine.Core.X6.CoherenceModel import CoherenceModel
from Engine.Core.X6.CyclesModel import CyclesModel
from Engine.Core.X6.RiskModel import RiskModel
from Engine.Core.X6.ScoringModel import ScoringModel
from Engine.Core.X6.FeatureBuilder import FeatureBuilder

class X6Master:

    def __init__(self):
        self.qm = QuantumModel()
        self.quantum = QuantumModel()
        self.phase = MarketPhase()
        self.coherence = CoherenceModel()
        self.cycles = CyclesModel()
        self.risk = RiskModel()
        self.scorer = ScoringModel()
        self.features = FeatureBuilder()


    def run(self, candle, htf_signals=None):

        close = candle.get("close", 0)
        high = candle.get("high", close)
        low = candle.get("low", close)
        volume = candle.get("volume", 1)

        # 1. کوانتومی
        mmt = self.qm.compute_momentum(close, high, low)
        volp = self.qm.compute_volume_pressure(volume)
        of = self.qm.compute_order_flow(high, low, close)
        rally = self.qm.compute_rally_probability(mmt, volp, of)

        # 2. رژیم بازار
        trend = self.reg.compute_trend_strength(close, high, low)
        vol = self.reg.compute_volatility(high, low)
        regime = self.reg.detect_regime(trend, vol)

        # 3. انسجام
        coherence = self.co.compute_coherence(htf_signals or {})

        # 4. فرکتال سیکل
        cycle_strength = self.cy.compute_cycle_strength(close, high, low)

        # 5. ریسک
        risk_factor = self.risk.compute_risk_factor(
            sharp_ratio=0.5,
            coherence=coherence
        )

        # 6. امتیازدهی
        total_score = self.sc.compute_total_score(
            confidence=trend,
            performance=mmt,
            rr_ratio=0.6,
            regime_match=1 if regime in ("روند قوی", "نوسانی") else 0.4,
            liquidity=volp,
            coherence=coherence,
            rally_prob=rally
        )

        # 7. ساخت وکتور ویژگی
        fv = self.fb.build_vector(
            momentum=mmt,
            volume_pressure=volp,
            order_flow=of,
            trend_strength=trend,
            volatility=vol,
            coherence=coherence,
            cycle_strength=cycle_strength,
            risk_factor=risk_factor,
            rally_prob=rally,
            total_score=total_score
        )

        diagnostics = {
            "momentum": mmt,
            "volume_pressure": volp,
            "order_flow": of,
            "rally_probability": rally,
            "trend_strength": trend,
            "volatility": vol,
            "regime": regime,
            "coherence": coherence,
            "cycle_strength": cycle_strength,
            "risk_factor": risk_factor,
            "total_score": total_score
        }

        return {
            "feature_vector": fv,
            "diagnostics": diagnostics,
            "x6_score": total_score
        }
