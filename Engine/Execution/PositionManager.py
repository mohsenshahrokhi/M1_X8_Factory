# Engine/Core/Execution/PositionManager.py
# نسخه کامل، حرفه‌ای و هماهنگ با X6 و TradeExecutor

import traceback


class PositionManager:

    def __init__(self, mt5_connector, logger):
        self.mt5 = mt5_connector
        self.logger = logger
        self.symbol = "XAUUSD"

        # تنظیمات حفاظت سیستم
        self.max_positions = 1          # سیستم فقط یک معامله همزمان باز می‌کند
        self.reverse_enabled = True     # اجازه معامله معکوس
        self.close_on_transition = True # بسته شدن معامله در فاز "انتقالی"

        # محدودیت‌های عملکرد و ریسک
        self.max_drawdown_threshold = -0.015   # -1.5%
        self.min_regime_for_trade = ["روند قوی", "نوسانی"]

    # ----------------------------------------------------------------------
    # گرفتن پوزیشن‌های باز
    # ----------------------------------------------------------------------
    def get_positions(self):
        try:
            positions = self.mt5.positions_get(symbol=self.symbol)
            return positions if positions else []
        except Exception as e:
            self.logger.error(f"PositionManager get_positions error: {e}")
            return []

    # ----------------------------------------------------------------------
    # بررسی امکان ورود به معامله جدید
    # ----------------------------------------------------------------------
    def can_open_new_trade(self, x6_output, direction):
        positions = self.get_positions()

        # 1. بیش از حداکثر معامله باز
        if len(positions) >= self.max_positions:
            return False, "MAX_POSITIONS_REACHED"

        diag = x6_output.get("diagnostics", {})
        regime = diag.get("regime", "رنج")
        score = x6_output.get("x6_score", 0.0)

        # 2. ممنوعیت معامله در فاز انتقالی (transition)
        if regime == "انتقالی" and self.close_on_transition:
            return False, "REGIME_TRANSITION"

        # 3. عدم معامله در "رنج" با اسکور پایین
        if regime == "رنج" and abs(score) < 0.15:
            return False, "LOW_SCORE_IN_RANGE"

        return True, "OK"

    # ----------------------------------------------------------------------
    # اگر معامله مخالف باز است → اول ببند، بعد معامله جدید باز کن
    # ----------------------------------------------------------------------
    def handle_reverse(self, direction, candle, executor):
        try:
            positions = self.get_positions()
            if not positions:
                return True, "NO_POSITIONS"

            pos = positions[0]
            is_buy = pos.type == 0
            is_sell = pos.type == 1

            # اگر جهت جدید مخالف جهت فعلی بود
            if (
                (is_buy and direction == "sell") or
                (is_sell and direction == "buy")
            ):
                if self.reverse_enabled:
                    self.logger.info("Reverse trade triggered → closing old position")
                    executor.close_position(pos.ticket)
                    return True, "REVERSED"
                else:
                    return False, "REVERSE_DISABLED"

            return True, "SAME_DIRECTION"

        except Exception as e:
            self.logger.error(f"handle_reverse error: {e}\n{traceback.format_exc()}")
            return False, "ERROR"

    # ----------------------------------------------------------------------
    # بررسی شرایط خروج اضطراری (Hard Close)
    # ----------------------------------------------------------------------
    def emergency_exit_check(self, x6_output):
        try:
            diag = x6_output.get("diagnostics", {})
            risk_factor = diag.get("risk_factor", 1.0)
            regime = diag.get("regime", "رنج")
            score = x6_output.get("x6_score", 0.0)

            positions = self.get_positions()
            if not positions:
                return False, "NO_POSITION"

            pos = positions[0]
            profit = pos.profit / pos.balance if pos.balance != 0 else 0

            # 1. اگر دراوودان به حد خطرناک رسید
            if profit < self.max_drawdown_threshold:
                return True, "DRAWDOWN_LIMIT"

            # 2. خروج در فاز انتقالی
            if regime == "انتقالی" and self.close_on_transition:
                return True, "TRANSITION_EXIT"

            # 3. خروج اگر اسکور به شدت ضعیف شد
            if abs(score) < 0.05:
                return True, "LOW_SCORE_EXIT"

            return False, "SAFE"

        except Exception as e:
            self.logger.error(f"emergency_exit_check error: {e}")
            return False, "ERROR"

    # ----------------------------------------------------------------------
    # بستن معامله باز اگر شرایط خطر رسید
    # ----------------------------------------------------------------------
    def process_exit_rules(self, x6_output, candle, executor):
        try:
            exit_flag, reason = self.emergency_exit_check(x6_output)
            if exit_flag:
                positions = self.get_positions()
                if not positions:
                    return False, "NO_POSITION"

                pos = positions[0]
                executor.close_position(pos.ticket)
                self.logger.warning(f"Emergency exit → {reason}")
                return True, reason

            return False, "NO_EXIT"

        except Exception as e:
            self.logger.error(f"process_exit_rules error: {e}")
            return False, "ERROR"

    # ----------------------------------------------------------------------
    # چرخه مدیریت پوزیشن (فراخوانی در process_cycle)
    # ----------------------------------------------------------------------
    def process(self, x6_output, direction, allocation, candle, executor):
        try:
            # 1) بررسی قوانین خروج اضطراری
            exit_done, exit_reason = self.process_exit_rules(x6_output, candle, executor)
            if exit_done:
                return False, f"EXIT_{exit_reason}"

            # 2) بررسی باز کردن معامله جدید
            can_open, message = self.can_open_new_trade(x6_output, direction)
            if not can_open:
                return False, f"BLOCKED_{message}"

            # 3) مدیریت Reverse Trade
            ok, rev_msg = self.handle_reverse(direction, candle, executor)
            if not ok:
                return False, f"BLOCK_REVERSE_{rev_msg}"

            return True, "ALLOWED"

        except Exception as e:
            self.logger.error(f"PositionManager process error: {e}")
            return False, "ERROR"
