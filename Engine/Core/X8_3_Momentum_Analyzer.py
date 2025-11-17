class MomentumAnalyzer:
    """
    محاسبه مومنتوم و انرژی قیمت
    """

    def compute(self, close_price):
        if isinstance(close_price, (float, int)):
            close_price = [close_price]

        if len(close_price) < 3:
            return {
                "momentum_raw": 0,
                "momentum_slope": 0,
                "momentum_acceleration": 0
            }

        # مومنتوم خام
        m1 = close_price[-1] - close_price[-2]
        m2 = close_price[-2] - close_price[-3]

        # نرخ تغییر (شتاب مومنتوم)
        acceleration = m1 - m2

        return {
            "momentum_raw": float(m1),
            "momentum_slope": float((m1 + m2) / 2),
            "momentum_acceleration": float(acceleration)
        }
