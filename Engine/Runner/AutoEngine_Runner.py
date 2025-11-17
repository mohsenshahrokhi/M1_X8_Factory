import json
import time
from Engine.AutoEngine.AutoEngine_M1_Operational import AutoEngineM1Operational
from Engine.Connectors.X8_MT5_Connector import MT5Connector
from Engine.Logging.Logger import Logger


class AutoEngineRunner:
    """
    اجراکننده‌ی اصلی موتور معاملاتی.
    وظیفه:
      - بارگذاری تنظیمات از فایل config
      - ساخت اتصال MT5 در حالت LIVE
      - اجرای حلقه‌ی مداوم پردازش دیتا (CSV یا LIVE)
    """

    def __init__(self, config_path="config/runner_config.json"):
        """Initialize runner and load configuration."""
        self.logger = Logger("Runner")

        with open(config_path, "r") as f:
            self.config = json.load(f)

        self.mode = self.config.get("mode", "CSV")
        self.symbol = self.config.get("symbol", "XAUUSD")
        self.csv_path = self.config.get("csv_path")

        # Initialize MT5 connector if needed
        self.mt5_connector = None
        if self.mode == "LIVE":
            self.mt5_connector = MT5Connector()
            self.mt5_connector.initialize()

        # Initialize operational engine
        self.engine = AutoEngineM1Operational(
            symbol=self.symbol,
            mode=self.mode,
            csv_path=self.csv_path,
            mt5_connector=self.mt5_connector
        )

        self.logger.log("Runner initialized successfully.")

    # -------------------------------------------------------------------------
    def run(self):
        """Main loop for runner execution."""
        self.logger.log(f"Starting AutoEngine Runner | Mode={self.mode}")
        active = True

        while active:
            active = self.engine.process_cycle()
            time.sleep(0.1)  # 100ms between ticks

        self.logger.log("Runner execution stopped (CSV sequence finished).")


if __name__ == "__main__":
    runner = AutoEngineRunner()
    runner.run()
