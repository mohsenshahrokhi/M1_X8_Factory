# execution/feedback_controller.py

class ExecutionFeedbackController:
    """
    Phase‑10B Execution Feedback Controller
    ---------------------------------------
    Applies adaptive throttle & size controls
    based on execution quality metrics.
    """

    def __init__(
        self,
        kill_switch=None,
        max_reject_ratio=0.25,
        critical_reject_ratio=0.50,
        min_throttle=0.25,
        min_size_multiplier=0.30
    ):
        self.kill_switch = kill_switch

        self.max_reject_ratio = max_reject_ratio
        self.critical_reject_ratio = critical_reject_ratio

        self.min_throttle = min_throttle
        self.min_size_multiplier = min_size_multiplier

        self.reset()

    def reset(self):
        """
        Reset adaptive controls to neutral state.
        """
        self.throttle = 1.0
        self.size_multiplier = 1.0
        self.pause = False

    def evaluate(self, metrics):
        """
        Update adaptive controls based on execution metrics.
        """
        try:
            reject_ratio = metrics.reject_ratio_window()
        except Exception:
            # Metrics not ready or window empty
            return

        # ============================
        # HARD GUARD (system safety)
        # ============================
        if reject_ratio >= self.critical_reject_ratio:
            if self.kill_switch:
                self.kill_switch.trigger(
                    f"[ExecutionFeedback] Critical reject ratio: {reject_ratio:.2f}"
                )
            self.pause = True
            return

        # ============================
        # SOFT ADAPTIVE CONTROL
        # ============================
        if reject_ratio > self.max_reject_ratio:
            # Degrade execution aggressiveness
            self.throttle *= 0.8
            self.size_multiplier *= 0.9

        elif reject_ratio < self.max_reject_ratio * 0.5:
            # System recovered → allow sending again
            self.pause = False

        # ============================
        # CLAMP VALUES
        # ============================
        self.throttle = max(self.throttle, self.min_throttle)
        self.size_multiplier = max(
            self.size_multiplier,
            self.min_size_multiplier
        )

        # ============================
        # PAUSE CONDITION
        # ============================
        if self.throttle <= self.min_throttle:
            self.pause = True

    def allow_send(self):
        """
        Whether execution is currently allowed.
        """
        return not self.pause

    def adjust_size(self, size):
        """
        Apply adaptive size multiplier.
        """
        try:
            return round(size * self.size_multiplier, 2)
        except Exception:
            return size
