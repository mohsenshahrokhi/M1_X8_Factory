class Trade:
    """
    Immutable trade result (after close)
    """
    def __init__(self, direction, entry_price, exit_price, size, t_entry, t_exit):
        self.direction = direction
        self.entry_price = entry_price
        self.exit_price = exit_price
        self.size = size
        self.t_entry = t_entry
        self.t_exit = t_exit

        if direction == "LONG":
            self.pnl = (exit_price - entry_price) * size
        else:
            self.pnl = (entry_price - exit_price) * size


class TradeLedger:
    """
    Phase‑9C / 9D Trade Ledger
    -------------------------
    * Single open position
    * Deterministic equity
    * Backtest safe
    """

    def __init__(self, initial_equity: float = 100_000.0):
        self.initial_equity = float(initial_equity)
        self.equity = float(initial_equity)

        self.position = None
        self.closed_trades = []

    # ===============================
    # ENTRY
    # ===============================
    def open(self, direction, entry_price, stop_price, size, t):
        if self.position is not None:
            return False

        self.position = {
            "direction": direction,
            "entry_price": float(entry_price),
            "stop_price": float(stop_price),
            "size": float(size),
            "t_entry": t,
        }
        return True

    # ===============================
    # STOP‑BASED EXIT
    # ===============================
    def check_stop(self, price: float, t: int):
        if self.position is None:
            return None

        d = self.position["direction"]
        stop = self.position["stop_price"]

        hit = (d == "LONG" and price <= stop) or (d == "SHORT" and price >= stop)
        if not hit:
            return None

        return self._close(price, t)

    # ===============================
    # FORCED / SIGNAL EXIT ✅
    # ===============================
    def close(self, exit_price: float, t: int):
        if self.position is None:
            return None
        return self._close(exit_price, t)

    # ===============================
    # INTERNAL CLOSE
    # ===============================
    def _close(self, price: float, t: int):
        trade = Trade(
            direction=self.position["direction"],
            entry_price=self.position["entry_price"],
            exit_price=price,
            size=self.position["size"],
            t_entry=self.position["t_entry"],
            t_exit=t,
        )

        self.equity += trade.pnl
        self.closed_trades.append(trade)
        self.position = None
        return trade

    # ===============================
    # HELPERS
    # ===============================
    def has_open_position(self):
        return self.position is not None

    def reset(self):
        self.equity = self.initial_equity
        self.position = None
        self.closed_trades.clear()
