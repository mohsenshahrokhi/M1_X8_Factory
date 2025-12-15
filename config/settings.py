# =====================================================
# X6 SYSTEM SETTINGS
# =====================================================

import os
from enum import Enum

# =====================================================
# STRESS MODE
# =====================================================

class StressMode(Enum):
    OFF  = "OFF"
    SOFT = "SOFT"
    FULL = "FULL"


STRESS_MODE = StressMode(
    os.getenv("STRESS_MODE", StressMode.OFF.value)
)

# =====================================================
# EXECUTION MODE
# =====================================================

class ExecutionMode(Enum):
    OFF     = "OFF"
    DRY_RUN = "DRY_RUN"
    LIVE    = "LIVE"


_exec_env = os.getenv("EXECUTION_MODE", ExecutionMode.DRY_RUN.value)

try:
    EXECUTION_MODE = ExecutionMode(_exec_env)
except ValueError:
    EXECUTION_MODE = ExecutionMode.DRY_RUN

# =====================================================
# FORCE TRADE MODE (DRY_RUN ONLY)
# =====================================================

FORCE_TRADE_MODE = (
    os.getenv("FORCE_TRADE_MODE", "1") == "1"
    and EXECUTION_MODE == ExecutionMode.DRY_RUN
)

FORCE_MIN_RISK_USD = float(
    os.getenv("FORCE_MIN_RISK_USD", "0.25")
)

# =====================================================
# EXECUTION POLICY (Phase-9A)
# =====================================================

CONF_THRESHOLD = float(
    os.getenv("CONF_THRESHOLD", "0.60")
)

# =====================================================
# DEBUG / WARM-UP FLAGS
# =====================================================

LOG_EXEC_POLICY = os.getenv("LOG_EXEC_POLICY", "1") == "1"

REQUIRE_LIVE_CONFIRM = (
    os.getenv("REQUIRE_LIVE_CONFIRM", "0") == "1"
)

WARMUP_MODE = os.getenv("WARMUP_MODE", "1") == "1"
WARMUP_MAX_ITER = 500
WARMUP_LOG_EVERY = 10
WARMUP_JUDGMENT_DEBUG = True

# =====================================================
# PHASE-9B: CONDITIONAL ACTIVATION
# =====================================================

PHASE_9B_ENABLED = True

MIN_TREND_EXPANSION = float(
    os.getenv("MIN_TREND_EXPANSION", "0.7")
)

MIN_VWAP_DEV = float(
    os.getenv("MIN_VWAP_DEV", "0.0025")
)

MAX_TRADE_STRESS = float(
    os.getenv("MAX_TRADE_STRESS", "0.35")
)
