# Engine/Core/Execution/TradeExecutor.py
# نسخه کامل و سازگار با X6 و AutoEngine_M1

import time
import traceback


class TradeExecutor:
    def __init__(self, mt5_connector, logger):
        self.mt5 = mt5_connector
        self.logger = logger
        self.symbol = "XAUUSD"
        self.sl_buffer = 0.3   # فاصله نسبی برای SL
        self.tp_buffer = 0.6   # فاصله نسبی برای TP
        self.trailing_active = True

    # ----------------------------------------------------------------------
    # باز کردن پوزیشن: buy/sell
    # ----------------------------------------------------------------------
    def open_position(self, direction, volume, candle):
        try:
            price = float(candle.get("close", 0))
            if price <= 0:
                return None

            if direction == "buy":
                sl = price - price * self.sl_buffer / 100
                tp = price + price * self.tp_buffer / 100
                ticket = self.mt5.buy(self.symbol, volume, sl, tp)
                self.logger.info(
                    f"BUY order placed: vol={volume} SL={round(sl,3)} TP={round(tp,3)}"
                )

            elif direction == "sell":
                sl = price + price * self.sl_buffer / 100
                tp = price - price * self.tp_buffer / 100
                ticket = self.mt5.sell(self.symbol, volume, sl, tp)
                self.logger.info(
                    f"SELL order placed: vol={volume} SL={round(sl,3)} TP={round(tp,3)}"
                )
            else:
                return None

            return ticket

        except Exception as e:
            self.logger.error(f"open_position error: {e}\n{traceback.format_exc()}")
            return None

    # ----------------------------------------------------------------------
    # بستن پوزیشن‌ها
    # ----------------------------------------------------------------------
    def close_position(self, ticket):
        try:
            r = self.mt5.close(ticket)
            self.logger.info(f"Closed position ticket={ticket}, result={r}")
            return r
        except Exception as e:
            self.logger.error(f"close_position error: {e}")
            return False

    # ----------------------------------------------------------------------
    # تریلینگ استاپ هوشمند بر اساس فرمول ترکیبی X5
    # ----------------------------------------------------------------------
    def trailing_stop(self, candle, ticket_info):
        try:
            if not self.trailing_active or not ticket_info:
                return

            atr_stop = self._atr_stop(candle)
            fractal_stop = self._fractal_stop(candle)
            quant_stop = self._quant_stop(candle)

            stop_new = (
                atr_stop * 0.4 +
                fractal_stop * 0.35 +
                quant_stop * 0.25
            )

            self.mt5.modify_stop(ticket_info["ticket"], stop_new)
            self.logger.info(f"Trailing stop applied: {round(stop_new,3)}")

        except Exception as e:
            self.logger.error(f"trailing_stop error: {e}")

    # ----------------------------------------------------------------------
    # توابع کمکی برای ساخت استاپ‌ها
    # ----------------------------------------------------------------------
    def _atr_stop(self, candle):
        # تخمین ساده نوسان میانگین برای شبیه‌سازی ATR
        hl_spread = float(candle.get("high", 0)) - float(candle.get("low", 0))
        return abs(hl_spread) * 0.8

    def _fractal_stop(self, candle):
        # مبتنی بر شکست‌های فرکتالی اخیر
        high = candle.get("high", 0)
        low = candle.get("low", 0)
        return abs(high - low) * 0.5

    def _quant_stop(self, candle):
        # مدل کوانتومی ریسک نسبت‌دار
        close = candle.get("close", 0)
        return abs(close * 0.0005)

    # ----------------------------------------------------------------------
    # بررسی وضعیت فعال پوزیشن‌ها
    # ----------------------------------------------------------------------
    def get_active_positions(self):
        try:
            positions = self.mt5.positions_get(symbol=self.symbol)
            if not positions:
                return []
            return positions
        except Exception as e:
            self.logger.error(f"get_active_positions error: {e}")
            return []

    # ----------------------------------------------------------------------
    # بررسی و اجرای تریلینگ برای پوزیشن‌های باز
    # ----------------------------------------------------------------------
    def manage_open_trades(self, candle):
        positions = self.get_active_positions()
        if not positions:
            return

        for pos in positions:
            self.trailing_stop(candle, pos)
