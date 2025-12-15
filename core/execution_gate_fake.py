# core/execution_gate_fake.py

import itertools
from typing import Optional


class ExecutionGateFake:
    """
    Minimal Fake Execution Gate
    ---------------------------
    - Instant fill
    - No slippage
    - No latency simulation
    - Limit orders only
    """

    _order_id_counter = itertools.count(1)

    def __init__(self, execution_registry):
        self.execution_registry = execution_registry

    def send_limit_order(
        self,
        *,
        side: str,
        volume: float,
        price: float,
        sl: float,
        tp: Optional[float] = None,
        symbol: str = "XAUUSD"
    ):
        # ----------------------------
        # Create execution record
        # ----------------------------
        exec_plan = _ExecPlan(
            symbol=symbol,
            side=side,
            size=volume,
            limit_price=price,
        )

        execution_id = self.execution_registry.create(exec_plan)

        # ----------------------------
        # Mark as SENT
        # ----------------------------
        self.execution_registry.mark_sent(execution_id)

        # ----------------------------
        # Instant fill
        # ----------------------------
        order_id = next(self._order_id_counter)

        self.execution_registry.mark_filled(
            execution_id=execution_id,
            order_id=order_id,
            fill_price=price  # perfect fill
        )

        # ----------------------------
        # Minimal return contract
        # ----------------------------
        return {
            "status": "FILLED",
            "execution_id": execution_id,
            "order_id": order_id,
            "fill_price": price,
            "volume": volume,
            "side": side,
            "sl": sl,
            "tp": tp,
        }


class _ExecPlan:
    """
    Minimal execution plan object
    Only what ExecutionRegistry needs
    """
    def __init__(self, symbol, side, size, limit_price):
        self.symbol = symbol
        self.side = side
        self.size = size
        self.limit_price = limit_price
