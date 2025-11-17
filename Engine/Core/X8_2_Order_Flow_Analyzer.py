class OrderFlowAnalyzer:
    """
    تحلیل جریان سفارشات (Order Flow)
    خروجی:
        {
            "buy_pressure": value,
            "sell_pressure": value,
            "order_flow_score": value
        }
    """

    def compute(self, spread, volume):
        if spread is None:
            spread = 0
        if volume is None:
            volume = 0

        # فشار خرید و فروش
        # مدل ساده‌سازی شده
        if spread < 10:
            buy_pressure = volume * 0.6
            sell_pressure = volume * 0.4
        else:
            buy_pressure = volume * 0.4
            sell_pressure = volume * 0.6

        flow_score = buy_pressure - sell_pressure

        return {
            "buy_pressure": float(buy_pressure),
            "sell_pressure": float(sell_pressure),
            "order_flow_score": float(flow_score)
        }
