from Engine.Connectors.X8_MT5_Connector import MT5Connector
from Engine.Logging.Logger import Logger
from Engine.Execution.TradeExecutor import TradeExecutor
from Engine.Execution.PositionManager import PositionManager
from Engine.Core.X6.X6_Master import X6Master


class AutoEngineM1Operational:
    """
    موتور اجرایی AutoEngine M1
    """

    def __init__(self, symbol):
        # اتصال متاتریدر
        self.mt5 = MT5Connector(symbol)

        # لاگر
        self.logger = Logger("AutoEngine_M1")

        # موتور تحلیل X6
        self.x6 = X6Master()

        # مدیریت موقعیت
        self.position_manager = PositionManager(self.mt5, self.logger)

        # اکسکیوشن
        self.executor = TradeExecutor(self.mt5, self.logger)

        self.symbol = symbol

    def process_tick(self, price, volume, high, low, spread):
        """
        پردازش یک تیک بازار
        """

        x6_output = self.x6.process(price, volume, high, low, spread)

        score = x6_output["score"]
        direction = x6_output["direction"]

        # تصمیم‌گیری
        if score > 0.7 and direction == "BUY":
            self.executor.open_buy()
        elif score > 0.7 and direction == "SELL":
            self.executor.open_sell()

        # مدیریت پوزیشن‌های باز
        self.position_manager.manage_positions()

        return x6_output
