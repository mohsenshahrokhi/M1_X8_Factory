# AutoEngine_M1.py
# نسخه کامل با اتصال 100% به X6

from Engine.Core.X6.X6_Master import X6_Master


class AutoEngine_M1:

    def __init__(self, connector, allocator, logger):
        self.connector = connector
        self.allocator = allocator
        self.logger = logger

        # موتور تحلیلگر X6
        self.x6 = X6_Master()

        # آستانه جهت‌دهی
        self.direction_threshold = 0.15

    # ----------------------------------------------------------------------
    # تحلیل بازار: فراخوانی X6
    # ----------------------------------------------------------------------
    def analyze_market(self, candle):
        try:
            return self.x6.run(candle)
        except Exception as e:
            self.logger.error(f"X6 analyze error: {e}")
            return {
                "x6_score": 0.0,
                "feature_vector": [],
                "diagnostics": {}
            }

    # ----------------------------------------------------------------------
    # ساخت state برای سیستم یادگیری و تشخیص
    # ----------------------------------------------------------------------
    def build_state(self, x6_output):
        try:
            score = float(x6_output.get("x6_score", 0.0))
            fv = x6_output.get("feature_vector", [])
            diag = x6_output.get("diagnostics", {})
            regime = diag.get("regime", "رنج")

            # کدگذاری عددی رژیم بازار
            regime_code = {
                "روند قوی": 1,
                "نوسانی": 0.5,
                "رنج": 0,
                "انتقالی": -0.5
            }.get(regime, 0)

            return (round(score, 3), fv, regime_code)

        except Exception as e:
            self.logger.error(f"state build error: {e}")
            return (0.0, [], 0)

    # ----------------------------------------------------------------------
    # تصمیم‌گیری جهت حرکت
    # ----------------------------------------------------------------------
    def decide_direction(self, x6_output):
        try:
            score = float(x6_output.get("x6_score", 0.0))
            diag = x6_output.get("diagnostics", {})

            mmt = diag.get("momentum", 0)
            coherence = diag.get("coherence", 0)
            regime = diag.get("regime", "رنج")

            # تقویت‌کننده جهت بر اساس انسجام + رژیم
            bias = 0
            if regime == "روند قوی":
                bias += 0.10
            if coherence > 0.6:
                bias += 0.05

            adjusted = score + bias

            if adjusted >= self.direction_threshold:
                return "buy"
            elif adjusted <= -self.direction_threshold:
                return "sell"
            else:
                return "hold"

        except Exception as e:
            self.logger.error(f"direction decide error: {e}")
            return "hold"

    # ----------------------------------------------------------------------
    # چرخه کامل پردازش M1
    # ----------------------------------------------------------------------
    def process_cycle(self):

        # 1. دریافت کندل از MT5
        candle = self.connector.get_latest_candle()
        if not candle:
            self.logger.warning("No candle received.")
            return None

        # 2. تحلیل توسط X6
        x6_output = self.analyze_market(candle)

        # 3. تصمیم‌گیری جهت
        direction = self.decide_direction(x6_output)

        # 4. تخصیص بنابراین output جدید X6
        try:
            allocation = self.allocator.allocate(
                score=float(x6_output.get("x6_score", 0.0)),
                risk_factor=float(x6_output["diagnostics"].get("risk_factor", 1.0))
            )
        except Exception as e:
            self.logger.error(f"Allocator error: {e}")
            allocation = 0.0

        # 5. ساخت state برای RL یا لاگ
        state = self.build_state(x6_output)

        # 6. خروجی نهایی چرخه
        return {
            "candle": candle,
            "direction": direction,
            "allocation": allocation,
            "x6_score": x6_output.get("x6_score"),
            "state": state,
            "diagnostics": x6_output.get("diagnostics", {})
        }
