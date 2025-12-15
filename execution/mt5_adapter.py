import MetaTrader5 as mt5
from dataclasses import dataclass
from typing import Optional


@dataclass
class ExecutionRequest:
    symbol: str
    side: str  # BUY or SELL
    size: float
    limit_price: float
    stop_price: float
    take_profit: Optional[float] = None
    magic: int = 777
    comment: str = "X6_PHASE7"


@dataclass
class ExecutionResult:
    success: bool
    order_ticket: Optional[int]
    reason: str
    broker_code: Optional[int] = None
    filled_price: Optional[float] = None


class MT5ExecutionAdapter:
    """
    Phase‑7A MT5 Execution Adapter
    Limit‑Only / Live‑Safe
    """

    def __init__(self):
        if not mt5.initialize():
            raise RuntimeError("MT5 initialization failed")

    def _build_request(self, req: ExecutionRequest) -> dict:
        order_type = (
            mt5.ORDER_TYPE_BUY_LIMIT
            if req.side == "BUY"
            else mt5.ORDER_TYPE_SELL_LIMIT
        )

        payload = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": req.symbol,
            "volume": req.size,
            "type": order_type,
            "price": req.limit_price,
            "sl": req.stop_price,
            "tp": req.take_profit or 0.0,
            "magic": req.magic,
            "comment": req.comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_RETURN,
        }

        return payload

    def send(self, req: ExecutionRequest) -> ExecutionResult:
        payload = self._build_request(req)

        result = mt5.order_send(payload)

        if result is None:
            return ExecutionResult(
                success=False,
                order_ticket=None,
                reason="MT5 returned None",
            )

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            return ExecutionResult(
                success=False,
                order_ticket=None,
                reason=f"Broker reject: {result.comment}",
                broker_code=result.retcode,
            )

        return ExecutionResult(
            success=True,
            order_ticket=result.order,
            reason="Order accepted",
            filled_price=result.price,
        )

    def shutdown(self):
        mt5.shutdown()
