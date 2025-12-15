# core/order_executor.py

from config.settings import EXECUTION_MODE, ExecutionMode

class OrderExecutor:

    def __init__(self, execution_gate):
        self.execution_gate = execution_gate

    def execute(
        self,
        *,
        symbol: str,
        side: str,
        volume: float,
        entry_price: float,
        sl: float,
        tp: float | None = None,
    ):
        if EXECUTION_MODE == ExecutionMode.OFF:
            return {"success": False, "reason": "EXECUTION_OFF"}

        if volume <= 0:
            return {"success": False, "reason": "INVALID_VOLUME"}

        if side not in ("BUY", "SELL"):
            return {"success": False, "reason": "INVALID_SIDE"}

        # 👇 فقط intent
        return self.execution_gate.send_limit_order(
            symbol=symbol,
            side=side,
            volume=volume,
            price=entry_price,
            sl=sl,
            tp=tp,
        )
