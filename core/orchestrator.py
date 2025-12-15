import numpy as np

from core.data_feed import MarketDataFeed
from core.vwap_engine import VWAPEngine
from core.vwap_regime import VWAPRegimeDetector

from monitoring.kill_switch import KillSwitch
from ai.hmm_stress import HMMStressDetector
from risk.risk_mapper import RiskBudgetMapper

from execution.stop_engine import StopEngine
from execution.position_sizer import PositionSizer
from execution.execution_intent import ExecutionIntent


class Orchestrator:
    """
    ====================================================
    X6 Orchestrator – Phase‑10A (Execution Wiring Dry‑Run)
    ----------------------------------------------------
    ✅ Feature + Stress
    ✅ Risk Budget
    ✅ Stop Engine
    ✅ Position Sizing
    ✅ ExecutionIntent creation
    ✅ ExecutionGate injection
    ❌ Ledger
    ❌ Forced Entry / Exit
    ====================================================
    """

    def __init__(self, data_feed: MarketDataFeed):
        if isinstance(data_feed, type):
            raise RuntimeError(
                "MarketDataFeed must be an instance, not a class"
            )

        self.data_feed = data_feed

        # ===============================
        # Kill Switch (Arm Once)
        # ===============================
        self.kill_switch = KillSwitch(
            max_drawdown_pct=3.0,
            max_rejections=3,
            cooldown_seconds=300,
        )
        self._armed = False

        # ===============================
        # Core Engines
        # ===============================
        self.vwap_engine = VWAPEngine()
        self.vwap_regime = VWAPRegimeDetector()
        self.hmm_stress = HMMStressDetector()
        self.risk_mapper = RiskBudgetMapper()
        self.stop_engine = StopEngine()

        # ===============================
        # Position Sizer
        # ===============================
        point_value = getattr(
            self.data_feed,
            "get_point_value",
            lambda: 1.0
        )()

        self.position_sizer = PositionSizer(
            point_value=point_value,
            min_size=0.01,
        )

        # ===============================
        # Execution (Injected by Runner)
        # ===============================
        self.execution_gate = None

        self._i = 0

    # ==================================================
    # One deterministic iteration – Phase‑10A
    # ==================================================
    def run_once(self):

        # ===== ARM KILL SWITCH (ONCE) =====
        if not self._armed:
            equity = self.data_feed.get_equity()
            self.kill_switch.arm(equity)
            self._armed = True

        if not self.kill_switch.can_trade():
            print(f"🚨 KILL SWITCH: {self.kill_switch.trip_reason}")
            return

        # ===== MARKET DATA =====
        df = self.data_feed.get_data()
        if df is None or len(df) < 50:
            print("⚠️ Not enough market data")
            return

        price = float(df["close"].iloc[-1])
        symbol = self.data_feed.symbol

        # ===== VWAP ENGINE =====
        vwap_df = self.vwap_engine.compute(df)

        vwap_dev   = float(vwap_df["vwap_dev"].iloc[-1])
        vol_weight = float(vwap_df["vol_weight"].iloc[-1])
        bar_range  = float(vwap_df["bar_range"].iloc[-1])
        avg_range  = float(vwap_df["avg_range"].iloc[-1])
        atr        = float(vwap_df["atr"].iloc[-1])

        # ===== REGIME =====
        regime = self.vwap_regime.detect(
            vwap_dev,
            vol_weight,
            bar_range,
            avg_range,
        )

        # ===== STRESS =====
        features = vwap_df[["vwap_dev", "vol_weight"]].values
        stress_score = float(self.hmm_stress.detect(features))

        self.kill_switch.check_stress(stress_score)
        self.kill_switch.check_equity(
            self.data_feed.get_equity()
        )

        if not self.kill_switch.can_trade():
            print(f"🚨 KILL SWITCH: {self.kill_switch.trip_reason}")
            return

        # ===== RISK =====
        equity = self.data_feed.get_equity()

        risk = self.risk_mapper.compute(
            equity=equity,
            stress_score=stress_score,
            regime=regime,
            vwap_dev=vwap_dev,
        )

        risk_amount = risk["risk_amount"]

        # ===== STOP =====
        returns = (
            df["close"]
            .pct_change()
            .dropna()
            .values[-100:]
        )

        stop_price, stop_reason = self.stop_engine.compute(
            direction="LONG",
            entry_price=price,
            atr=atr,
            stress_score=stress_score,
            nds_slope=vwap_dev,
            returns=returns,
        )

        # ===== POSITION SIZE =====
        size_info = self.position_sizer.compute(
            risk_budget=risk_amount,
            entry_price=price,
            stop_price=stop_price,
            regime=regime,
            stress_score=stress_score,
            nds_slope=vwap_dev,
        )

        if size_info["size"] <= 0:
            print("⚠️ SIZE = 0 → Skip")
            return

        # ===== EXECUTION INTENT =====
        if self.execution_gate is None:
            raise RuntimeError(
                "ExecutionGate is not injected"
            )

        intent = ExecutionIntent(
            symbol=symbol,
            side="BUY",
            size=size_info["size"],
            limit_price=price,
            stop_price=stop_price,
            take_profit=None,
            comment="PHASE10A_DRY",
        )

        exec_result = self.execution_gate.send(intent)

        # ===== LOG =====
        print("--------------------------------------------------")
        print(f"VWAP Dev : {vwap_dev:+.5f}")
        print(f"Regime   : {regime}")
        print(f"Stress   : {stress_score:.2f}")
        print(f"Equity   : {equity:.2f}")
        print(f"Risk USD : {risk_amount:.2f}")
        print(f"STOP     : {stop_price:.5f} ({stop_reason})")
        print(f"SIZE     : {size_info['size']}")
        print(f"EXEC     : {exec_result}")
        print("--------------------------------------------------")

        self._i += 1

    # Backward compatibility
    def run(self):
        self.run_once()
