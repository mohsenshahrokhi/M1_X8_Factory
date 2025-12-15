class ExecutionFeedbackController:
    def __init__(self, kill_switch):
        self.kill_switch = kill_switch

    def adapt(self, metrics, config):
        health = metrics.health_score()

        if health < 0.35:
            self.kill_switch.arm("Phase‑7C: execution health low")

        if metrics.reject_rate() > 0.25:
            config.slice_count = max(1, config.slice_count - 1)

        if health < 0.6:
            config.cooldown_sec = min(10, config.cooldown_sec + 1)

        return config
