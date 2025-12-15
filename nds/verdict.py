from dataclasses import dataclass
from typing import Dict, Any


@dataclass(frozen=True)
class NDSVerdictEnvelope:
    market_state: Dict[str, Any]
    structure_state: Dict[str, Any]
    pressure_state: Dict[str, Any]
    capacity_state: Dict[str, Any]
    decision: Dict[str, Any]
