# execution/execution_intent.py

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ExecutionIntent:
    symbol: str
    side: str               # "BUY" / "SELL"
    size: float
    limit_price: float
    stop_price: float
    take_profit: Optional[float] = None
    comment: str = "PH10A_DRY"
    source: str = "Orchestrator"
