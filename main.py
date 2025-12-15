import time
import logging
import os
import MetaTrader5 as MT5
from core.market_data import MarketDataFeed
from core.orchestrator import Orchestrator

print("✅ RUNNING MAIN FROM:", os.path.abspath(__file__))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

def main():
    logging.info("🚀 X6 ENGINE STARTED")

    feed = MarketDataFeed(
        mt5=MT5,
        base_symbol="BTCUSD",
        timeframe=MT5.TIMEFRAME_M1,
        bars=2000
    )

    orchestrator = Orchestrator(feed)

    while True:
        try:
            orchestrator.run()        # ✅ single iteration
            time.sleep(1.0)           # ✅ heartbeat (not decision rate)
        except KeyboardInterrupt:
            logging.warning("🛑 ENGINE STOPPED BY USER")
            break
        except Exception as e:
            logging.exception(f"🔥 ENGINE ERROR: {e}")
            time.sleep(5.0)

if __name__ == "__main__":
    main()
