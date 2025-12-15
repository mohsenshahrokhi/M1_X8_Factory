# =====================================================
# bt/bt_phase10a_runner.py
# PHASE‑10A – EXECUTION WIRING (DRY‑RUN)
# =====================================================

import sys
import os
from datetime import datetime

# -----------------------------------------------------
# PATH FIX
# -----------------------------------------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

# -----------------------------------------------------
# IMPORTS
# -----------------------------------------------------
import MetaTrader5 as mt5

from bt.mt5_replay_feed import MT5ReplayFeed
from core.orchestrator import Orchestrator

from execution import ExecutionGate
print(ExecutionGate)
from execution.mock_execution_adapter import MockExecutionAdapter

# -----------------------------------------------------
# CONFIG
# -----------------------------------------------------
SYMBOL = "BTCUSD"

START_DATE = datetime(2022, 1, 1)
END_DATE   = datetime(2022, 1, 10)

TF_SEQUENCE = ["M5"]
WINDOW_BARS = 500


def run_phase10a():

    if not mt5.initialize():
        raise RuntimeError("❌ MT5 init failed")

    print("✅ MT5 Initialized (Replay Only)")

    feed = MT5ReplayFeed(
        symbol=SYMBOL,
        start_date=START_DATE,
        end_date=END_DATE,
        timeframes=TF_SEQUENCE,
        bars=WINDOW_BARS,
    )
    feed.load()
    print("✅ Historical data loaded")

    orchestrator = Orchestrator(feed)

    # ---- PHASE‑10A WIRING ----
    mock_adapter = MockExecutionAdapter()
    execution_gate = ExecutionGate(adapter=mock_adapter)
    orchestrator.execution_gate = execution_gate

    print("🚀 Phase‑10A (Dry‑Run) Started")

    iteration = 0
    while feed.step():
        orchestrator.run_once()
        iteration += 1

        if iteration >= 5:
            break

    print("✅ PHASE‑10A DRY‑RUN COMPLETE")
    mt5.shutdown()


if __name__ == "__main__":
    run_phase10a()
