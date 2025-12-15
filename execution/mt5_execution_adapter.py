import MetaTrader5 as mt5


class MT5ExecutionAdapter:
    """
    Real MT5 execution adapter
    LIMIT orders only (Phase‑10B)
    """

    def __init__(self):
        if not mt5.initialize():
            raise RuntimeError("❌ MT5 initialization failed")

    def send(self, intent):
        order_type = (
            mt5.ORDER_TYPE_BUY_LIMIT
            if intent.side == "BUY"
            else mt5.ORDER_TYPE_SELL_LIMIT
        )

        request = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": intent.symbol,
            "volume": intent.size,
            "type": order_type,
            "price": intent.limit_price,
            "sl": intent.stop_price,
            "tp": intent.take_profit or 0.0,
            "deviation": 10,
            "magic": 60010,
            "comment": getattr(intent, "comment", "X6_EXEC"),
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_RETURN,
        }

        result = mt5.order_send(request)

        if result is None:
            return {
                "success": False,
                "reason": "MT5 order_send() returned None"
            }

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            return {
                "success": False,
                "reason": f"MT5 reject: {result.retcode}"
            }

        return {
            "success": True,
            "order_ticket": result.order,
            "filled_price": intent.limit_price,
            "reason": "LIMIT order accepted"
        }

    def shutdown(self):
        mt5.shutdown()
