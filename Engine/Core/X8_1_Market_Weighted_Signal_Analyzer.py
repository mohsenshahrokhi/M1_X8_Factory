import numpy as np

class MarketWeightedSignalAnalyzer:
    """
    تحلیل وزن‌دار بازار
    خروجی:
        {
            "momentum": value,
            "order_flow": value,
            "cohesion": value,
            "score": value
        }
    """

    def __init__(self):
        pass

    def compute(self, close_price, volume):
        # اگر ورودی float بود → تبدیل به لیست
        if isinstance(close_price, (float, int)):
            close_price = [close_price]
        if isinstance(volume, (float, int)):
            volume = [volume]

        # ایمنی داده
        if len(close_price) < 3:
            return {
                "momentum": 0,
                "order_flow": 0,
                "cohesion": 0,
                "score": 0
            }

        # مومنتوم ساده
        momentum = close_price[-1] - close_price[-2]

        # فشار حجم
        volume_flow = volume[-1] - volume[-2]

        # انسجام (cohesion)
        cohesion = 1.0 if (momentum > 0 and volume_flow > 0) else \
                   -1.0 if (momentum < 0 and volume_flow < 0) else 0.0

        # **Score اصلی سیستم X8**
        score = (
            (momentum * 0.4) +
            (volume_flow * 0.3) +
            (cohesion * 0.3)
        )

        return {
            "momentum": float(momentum),
            "order_flow": float(volume_flow),
            "cohesion": float(cohesion),
            "score": float(score)
        }
