# Engine/Execution/TradeExecutor_M1.py

import MetaTrader5 as mt5
import time


class TradeExecutor_M1:

    def __init__(self, symbol, logger, sl_points=300, tp_points=600):
        self.symbol = symbol
        self.logger = logger
        self.sl_points = sl_points
        self.tp_points = tp_points

    # ----------------------------------------------------------------------
    # دریافت پوزیشن باز
    # ----------------------------------------------------------------------
    def get_open_position(self):
        positions = mt5.positions_get(symbol=self.symbol)
        if positions:
            return positions[0]
        return None

    # ----------------------------------------------------------------------
    # بستن پوزیشن
    # ----------------------------------------------------------------------
    def close_position(self, ticket, lot):
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "position": ticket,
            "symbol": self.symbol,
            "volume": lot,
            "type": mt5.ORDER_TYPE_BUY if lot < 0 else mt5.ORDER_TYPE_SELL,
            "magic": 10001,
            "comment": "X8 Auto Close",
        }
        result = mt5.order_send(request)
        return result

    # ----------------------------------------------------------------------
    # باز کردن پوزیشن جدید
    # ----------------------------------------------------------------------
    def open_position(self, direction, lot):
        if direction == "buy":
            order_type = mt5.ORDER_TYPE_BUY
        else:
            order_type = mt5.ORDER_TYPE_SELL

        price = mt5.symbol_info_tick(self.symbol).ask if direction == "buy" else mt5.symbol_info_tick(self.symbol).bid
        point = mt5.symbol_info(self.symbol).point

        sl = price - self.sl_points * point if direction == "buy" else price + self.sl_points * point
        tp = price + self.tp_points * point if direction == "buy" else price - self.tp_points * point

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "type": order_type,
            "volume": lot,
            "price": price,
            "sl": sl,
            "tp": tp,
            "magic": 10001,
            "comment": "X8 Auto Entry",
        }

        result = mt5.order_send(request)
        return result

    # ----------------------------------------------------------------------
    # اجرای تصمیم نهایی موتور
    # ----------------------------------------------------------------------
    def execute(self, direction, allocation):

        pos = self.get_open_position()

        # HOLD → هیچ کاری
        if direction == "hold":
            return "hold"

        # اگر پوزیشن وجود دارد
        if pos:
            pos_type = "buy" if pos.type == 0 else "sell"

            # اگر جهت جدید با جهت فعلی یکی است → برو بیرون
            if pos_type == direction:
                return "no_change"

            # اگر جهت مخالف است → پوزیشن قبلی بسته می‌شود
            close_result = self.close_position(pos.ticket, pos.volume)
            time.sleep(0.4)

        # باز کردن پوزیشن جدید
        result = self.open_position(direction, allocation)
        return result
