import time
import traceback
from datetime import datetime

from Engine.Core.X8_MT5_Connector import MT5Connector
from Engine.Core.X8_6_MarketWeighted_SignalAnalyzer import MarketWeightedSignalAnalyzer
from Engine.Core.X8_8_Dynamic_Trade_Allocator import DynamicTradeAllocator
from Engine.Core.X8_4_RL_Core import RLCore


class AutoEngineM1:

    def __init__(self):

        print("✅ AutoEngine_M1 initialized")

        # ---------------------------------------------------------
        # PARAMETERS
        # ---------------------------------------------------------
        self.symbol = "XAUUSD_o"
        self.timeframe = 1
        self.direction_threshold = 0.45          # Market score threshold
        self.run_interval = 1                    # seconds

        # ---------------------------------------------------------
        # CONNECTOR
        # ---------------------------------------------------------
        self.mt5 = MT5Connector()                # ✅ AUTO login handled inside
        self.mt5.select_symbol(self.symbol)      # ✅ Symbol activation

        # ---------------------------------------------------------
        # MODULES
        # ---------------------------------------------------------
        self.analyzer = MarketWeightedSignalAnalyzer()
        self.allocator = DynamicTradeAllocator()
        self.rl = RLCore(learning_rate=0.1, discount_factor=0.9)

        # RL state tracking
        self.prev_state = None
        self.prev_action = None


    # ======================================================================
    # ✅ FETCH CANDLE FROM MT5
    # ======================================================================
    def get_latest_candle(self):
        candle = self.mt5.get_latest_candle(self.symbol)
        return candle


    # ======================================================================
    # ✅ RL STATE BUILDER (must be hashable → tuple)
    # ======================================================================
    def build_state(self, candle, market_score):

        # Extract values safely
        ms = market_score.get("market_score", 0.0)
        momentum = market_score.get("momentum", 0.0)
        direction = market_score.get("direction", "hold")

        return (
            round(candle["close"], 2),
            round(candle["volume"], 2),
            round(ms, 3),                 # ✅ FIXED: use float not dict
            round(momentum, 3),           # ✅ include momentum
            1 if direction == "buy" else -1 if direction == "sell" else 0
        )



    # ======================================================================
    # ✅ MARKET DECISION LOGIC
    # ======================================================================
    def decide_direction(self, market_score):

        # Extract individual values
        ms = market_score.get("market_score", 0.0)
        momentum = market_score.get("momentum", 0.0)
        direction_hint = market_score.get("direction", "hold")

        # ✅ Enhanced logic
        # 1. If market score high enough → buy/sell
        if ms >= self.direction_threshold:
            return "buy"
        elif ms <= -self.direction_threshold:
            return "sell"

        # 2. If momentum strongly positive/negative
        if momentum >= 0.6:
            return "buy"
        if momentum <= -0.6:
            return "sell"

        # 3. Otherwise fallback to MWSA direction
        return direction_hint

    # ======================================================================
    # ✅ ORDER EXECUTION HANDLER
    # ======================================================================
    def execute_order(self, direction, lot):

        if direction == "BUY":
            print("🚀 Sending BUY...")
            return self.mt5.send_order(self.symbol, "BUY", lot)

        if direction == "SELL":
            print("🔻 Sending SELL...")
            return self.mt5.send_order(self.symbol, "SELL", lot)

        return None


    # ======================================================================
    # ✅ MAIN LOOP
    # ======================================================================
    def process_cycle(self):

        try:
            # ---------------------------------------------------------
            # Grab last candle
            # ---------------------------------------------------------
            candle = self.get_latest_candle()
            if candle is None:
                print("⚠️ No candle data received. Skipping cycle.")
                return

            close = candle["close"]
            volume = candle["volume"]

            # ---------------------------------------------------------
            # Analyzer computes market score
            # ---------------------------------------------------------
            market_score = self.analyzer.compute(close, volume)
            print(f"📊 Market Score: {market_score}")

            # ---------------------------------------------------------
            # Build RL state
            # ---------------------------------------------------------
            state = self.build_state(candle, market_score)

            # ---------------------------------------------------------
            # Decide direction (BUY / SELL / HOLD)
            # ---------------------------------------------------------
            direction = self.decide_direction(market_score)
            print(f"🎯 Direction Decision: {direction}")

            # ---------------------------------------------------------
            # Use allocator to determine lot & action type
            # ---------------------------------------------------------
            allocation = self.allocator.allocate(
                 market_score["market_score"],   # ✅ FIXED
                 direction,
                 candle["close"]
)

            print(f"📦 Allocation: {allocation}")

            # ---------------------------------------------------------
            # Execute trade if needed
            # ---------------------------------------------------------
            order_result = None

            if allocation["type"] in ["buy", "sell"]:
                order_result = self.execute_order(
                    direction=allocation["type"].upper(),
                    lot=allocation["lot"]
                )

            # ---------------------------------------------------------
            # RL Update for last cycle
            # ---------------------------------------------------------
            reward = 0
            if order_result and order_result.retcode == 10009:  # TRADE_RETCODE_DONE
                reward = 1
            elif allocation["type"] == "hold":
                reward = 0.05
            else:
                reward = -0.1

            if self.prev_state is not None:
                self.rl.update_q(self.prev_state, self.prev_action, reward, state)

            self.prev_state = state
            self.prev_action = direction

        except Exception as e:
            print(f"❌ Error in cycle: {e}")
            traceback.print_exc()


    # ======================================================================
    # ✅ LOOP RUNNER
    # ======================================================================
    def run(self):

        print("✅ AutoEngine M1 is now running...")

        while True:
            self.process_cycle()
            time.sleep(self.run_interval)



# ======================================================================
# ✅ ENTRY POINT
# ======================================================================
if __name__ == "__main__":
    engine = AutoEngineM1()
    engine.run()
