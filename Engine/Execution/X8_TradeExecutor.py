# Engine/Execution/X8_TradeExecutor.py
# نسخه پیشرفته، سازگار با X6 و AutoEngine_M1

import math
import time

class X8_TradeExecutor:
    def __init__(self, connector, logger):
        self.connector = connector
        self.logger = logger

        # تنظیمات پایه
        self.default_lot_size = 0.1
        self.atr_window = 14
        self.stop_factor = 1.5
        self.trailing_factor = 1.2

    # ------------------------------------------------------------------
    # محاسبه استاپ هوشمند ترکیبی بر اساس فرمول X6
    # ------------------------------------------------------------------
    def compute_dynamic_stop(self, candle, volatility, coherence, quantum_score):
        # استاپ_ATR × ۰.۴ + استاپ_فرکتالی × ۰.۳۵ + استاپ_کوانتومی × ۰.۲۵
        atr_stop = (candle["high"] - candle["low"]) * self.stop_factor
        fractal_stop = abs(candle["close"] - ((candle["high"] + candle["low"]) / 2)) * 1.1
        quantum_stop = volatility * (1 - coherence) * (1 + abs(quantum_score))

        final_stop = (atr_stop * 0.4) + (fractal_stop * 0.35) + (quantum_stop * 0.25)
        return round(final_stop, 3)

    # ------------------------------------------------------------------
    # مدل تخصیص حجم معامله بر اساس امتیاز X6
    # ------------------------------------------------------------------
    def compute_trade_volume(self, x6_score, risk_factor, base_volume=0.1):
        if x6_score <= 0:
            return 0.0
        adj = min(2.0, 1 + (x6_score * risk_factor))
        return round(base_volume * adj, 2)

    # ------------------------------------------------------------------
    # اجرای فرمان معاملاتی
    # ------------------------------------------------------------------
    def execute_trade(self, direction, candle, x6_diag):
        try:
            if direction == "hold":
                return "No trade (hold)"

            x6_score = x6_diag.get("total_score", 0.0)
            volatility = x6_diag.get("volatility", 0.01)
            coherence = x6_diag.get("coherence", 0.5)

            volume = self.compute_trade_volume(
                x6_score=x6_score,
                risk_factor=x6_diag.get("risk_factor", 1.0),
                base_volume=self.default_lot_size
            )

            stop_distance = self.compute_dynamic_stop(
                candle,
                volatility=volatility,
                coherence=coherence,
                quantum_score=x6_score
            )

            # دستور معکوس برای فروش
            if direction == "sell":
                price = candle["bid"] if "bid" in candle else candle["close"]
                sl = price + stop_distance
                tp = price - (stop_distance * self.trailing_factor)
                self.connector.send_order(
                    symbol="XAUUSD",
                    action="sell",
                    lot=volume,
                    sl=sl,
                    tp=tp
                )
                msg = f"SELL @{price} sl={sl} tp={tp} vol={volume}"

            elif direction == "buy":
                price = candle["ask"] if "ask" in candle else candle["close"]
                sl = price - stop_distance
                tp = price + (stop_distance * self.trailing_factor)
                self.connector.send_order(
                    symbol="XAUUSD",
                    action="buy",
                    lot=volume,
                    sl=sl,
                    tp=tp
                )
                msg = f"BUY @{price} sl={sl} tp={tp} vol={volume}"

            else:
                msg = "Invalid direction"

            self.logger.info(f"[EXECUTOR] {msg}")
            return msg

        except Exception as e:
            self.logger.error(f"Trade Execution Error: {e}")
            return f"Error: {e}"
