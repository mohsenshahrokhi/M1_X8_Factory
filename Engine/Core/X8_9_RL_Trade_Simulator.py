import os
import pandas as pd
from datetime import datetime

class X8_9_RL_TradeSimulator:
    def __init__(self, base_path="M1_X8_Factory"):
        self.base = base_path

        # Inputs
        self.market_paths = [
            os.path.join(self.base, "Market", "XAUUSD_M1_Cleaned_Data.csv"),
            os.path.join(self.base, "Data", "XAUUSD_M1_Cleaned_Data.csv"),
            "XAUUSD_M1_Cleaned_Data.csv"
        ]

        self.alloc_path = os.path.join(self.base, "State", "Allocation.csv")
        self.qvalue_path = os.path.join(self.base, "State", "QValue.csv")

        # Outputs
        self.reward_path = os.path.join(self.base, "Rewards", "TotalReward_Enhanced.csv")
        self.log_path = os.path.join(self.base, "Logs", "RL_Log.txt")

        # Parameters
        self.alpha = 0.15
        self.gamma = 0.95

    # -----------------------------------------------------
    # Load market data
    # -----------------------------------------------------
    def load_market(self):
        for p in self.market_paths:
            if os.path.exists(p):
                return pd.read_csv(p)
        raise FileNotFoundError("Market data (XAUUSD_M1_Cleaned_Data.csv) not found in Market/, Data/, or root.")

    # -----------------------------------------------------
    # Load last allocation (Lot Size)
    # -----------------------------------------------------
    def load_allocation(self):
        if not os.path.exists(self.alloc_path):
            raise FileNotFoundError("Allocation.csv not found. Run X8.8 first.")
        df = pd.read_csv(self.alloc_path)
        return float(df["LotSize"].iloc[-1])

    # -----------------------------------------------------
    # Load Q-Value
    # -----------------------------------------------------
    def load_qvalue(self):
        if not os.path.exists(self.qvalue_path):
            df = pd.DataFrame([{"QValue": 1.0}])
            df.to_csv(self.qvalue_path, index=False)
            return 1.0
        df = pd.read_csv(self.qvalue_path)
        return float(df["QValue"].iloc[-1])

    # -----------------------------------------------------
    # Load latest adjusted reward
    # -----------------------------------------------------
    def load_reward(self):
        if not os.path.exists(self.reward_path):
            df = pd.DataFrame([{"Timestamp": 0, "Reward": 1.0}])
            df.to_csv(self.reward_path, index=False)
            return 1.0
        df = pd.read_csv(self.reward_path)
        return float(df["Reward"].iloc[-1])

    # -----------------------------------------------------
    # Simulate a trade
    # -----------------------------------------------------
    def simulate_trade(self, lot):
        df = self.load_market()
        entry = float(df["close"].iloc[-2])
        exit = float(df["close"].iloc[-1])
        pnl = (exit - entry) * lot
        return entry, exit, pnl

    # -----------------------------------------------------
    # Compute final reward
    # -----------------------------------------------------
    def compute_reward(self, pnl, adjusted_reward):
        # reward = pnl + adjusted_reward  (base formula)
        reward = pnl + adjusted_reward

        new_row = {
            "Timestamp": str(datetime.now()),
            "Reward": round(reward, 6)
        }

        df = pd.read_csv(self.reward_path)
        df.loc[len(df)] = new_row
        df.to_csv(self.reward_path, index=False)

        return round(reward, 6)

    # -----------------------------------------------------
    # Q-Learning update
    # -----------------------------------------------------
    def update_qvalue(self, q_old, reward):
        q_new = q_old + self.alpha * (reward + self.gamma * q_old - q_old)

        df = pd.read_csv(self.qvalue_path)
        df.loc[len(df)] = {"QValue": round(q_new, 12)}
        df.to_csv(self.qvalue_path, index=False)

        return round(q_new, 12)

    # -----------------------------------------------------
    # Log data
    # -----------------------------------------------------
    def log(self, data):
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(f"\n[{datetime.now()}] X8.9 RL Update → {data}")

    # -----------------------------------------------------
    # Execute full RL cycle
    # -----------------------------------------------------
    def run(self):
        lot = self.load_allocation()
        q_old = self.load_qvalue()
        adj_reward = self.load_reward()

        entry, exit, pnl = self.simulate_trade(lot)
        reward = self.compute_reward(pnl, adj_reward)
        q_new = self.update_qvalue(q_old, reward)

        result = {
            "Entry": entry,
            "Exit": exit,
            "PnL": pnl,
            "AdjustedReward": adj_reward,
            "FinalReward": reward,
            "QValue_Old": q_old,
            "QValue_New": q_new,
            "LotSize": lot
        }

        self.log(result)
        return result


if __name__ == "__main__":
    sim = X8_9_RL_TradeSimulator()
    print(sim.run())
