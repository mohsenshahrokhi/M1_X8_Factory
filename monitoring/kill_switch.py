# kill_switch.py
# monitoring/kill_switch.py

import time


class KillSwitch:
    """
    Phase-7 Kill Switch
    -------------------
    Last line of defense before LIVE execution.
    """

    def __init__(
        self,
        max_drawdown_pct=3.0,
        max_rejections=3,
        cooldown_seconds=300
    ):
        self.max_drawdown_pct = max_drawdown_pct
        self.max_rejections = max_rejections
        self.cooldown_seconds = cooldown_seconds

        self.start_equity = None
        self.rejections = 0
        self.tripped = False
        self.trip_reason = None
        self.trip_time = None

    # ---------- ARM ----------
    def arm(self, equity):
        self.start_equity = equity
        self.tripped = False
        self.rejections = 0

    # ---------- CHECKS ----------
    def check_equity(self, current_equity):
        if self.start_equity is None:
            return

        dd = (self.start_equity - current_equity) / self.start_equity * 100
        if dd >= self.max_drawdown_pct:
            self.trip(f"Max drawdown exceeded: {dd:.2f}%")

    def register_rejection(self):
        self.rejections += 1
        if self.rejections >= self.max_rejections:
            self.trip("Too many order rejections")

    def check_mt5_connection(self, connected):
        if not connected:
            self.trip("MT5 disconnected")

    def check_stress(self, stress):
        if stress is not None and stress > 0.95:
            self.trip("Extreme market stress")

    # ---------- TRIP ----------
    def trip(self, reason):
        if self.tripped:
            return

        self.tripped = True
        self.trip_reason = reason
        self.trip_time = time.time()

    # ---------- STATE ----------
    def can_trade(self):
        return not self.tripped

    def status(self):
        return {
            "armed": self.start_equity is not None,
            "tripped": self.tripped,
            "reason": self.trip_reason,
            "time": self.trip_time,
        }

    # ---------- RESET ----------
    def reset(self):
        if self.trip_time is None:
            return False

        if time.time() - self.trip_time >= self.cooldown_seconds:
            self.tripped = False
            self.rejections = 0
            self.trip_reason = None
            return True

        return False
