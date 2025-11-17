import os
import pandas as pd
from datetime import datetime


class X8_7_QuantizedEnergyManager:
    def __init__(self, base_path="M1_X8_Factory"):
        self.base = base_path

        # Paths
        self.qvalue_path = os.path.join(self.base, "RL", "QValue.csv")
        self.cohesion_path = os.path.join(self.base, "Logs", "Cohesion_Log.txt")
        self.energy_path = os.path.join(self.base, "Energy", "Trading_Energy.csv")
        self.energy_log = os.path.join(self.base, "Logs", "Energy_Log.txt")

        # Default if missing
        self.default_q = 1.0
        self.default_coh = 1.0
        self.default_sharpe = 1.0

    # -----------------------------------------------------
    # Load Q-Value
    # -----------------------------------------------------
    def load_qvalue(self):
        if not os.path.exists(self.qvalue_path):
            df = pd.DataFrame([{"Timestamp": 0, "QValue": self.default_q}])
            df.to_csv(self.qvalue_path, index=False)
            return self.default_q

        df = pd.read_csv(self.qvalue_path)
        return float(df["QValue"].iloc[-1])

    # -----------------------------------------------------
    # Load CohesionWeighted from log
    # -----------------------------------------------------
    def load_cohesion(self):
        if not os.path.exists(self.cohesion_path):
            return self.default_coh

        lines = open(self.cohesion_path, "r", encoding="utf-8").read().strip().split("\n")
        if len(lines) == 0:
            return self.default_coh

        last = lines[-1]

        if "CohesionWeighted" not in last:
            return self.default_coh

        try:
            marker = "CohesionWeighted': "
            start = last.index(marker) + len(marker)
            raw = last[start:].split(",")[0].replace("}", "").strip()
            return float(raw)
        except:
            return self.default_coh

    # -----------------------------------------------------
    # Estimate Sharpe Ratio (simple rolling)
    # -----------------------------------------------------
    def compute_sharpe(self, qvalue):
        """
        فرمول رسمی در x6:
        فاکتور_ریسک_جدید = نسبت شارپ × تقویت انسجام

        در این نسخه ساده، شارپ = log(QValue) اگر QValue>1
        """
        import math

        if qvalue <= 1:
            return 1.0

        return round(1 + math.log(qvalue), 6)

    # -----------------------------------------------------
    # Compute Trading Energy
    # -----------------------------------------------------
    def compute_energy(self):
        q = self.load_qvalue()
        coh = self.load_cohesion()
        sharpe = self.compute_sharpe(q)

        # فرمول رسمی X8 طراحی‌شده:
        # TradingEnergy = (Q × Sharpe × Cohesion) ^ (1/3)
        energy = (q * sharpe * coh) ** (1 / 3)

        result = {
            "QValue": round(q, 6),
            "Sharpe": round(sharpe, 6),
            "Cohesion": round(coh, 6),
            "TradingEnergy": round(energy, 6),
        }

        self.store_energy(result)
        self.log(result)

        return result

    # -----------------------------------------------------
    # Save Trading Energy to CSV
    # -----------------------------------------------------
    def store_energy(self, result_dict):
        if not os.path.exists(self.energy_path):
            df = pd.DataFrame([], columns=["Timestamp", "TradingEnergy"])
        else:
            df = pd.read_csv(self.energy_path)

        df.loc[len(df)] = {
            "Timestamp": datetime.now(),
            "TradingEnergy": result_dict["TradingEnergy"],
        }

        df.to_csv(self.energy_path, index=False)

    # -----------------------------------------------------
    # Log
    # -----------------------------------------------------
    def log(self, result):
        with open(self.energy_log, "a", encoding="utf-8") as f:
            f.write(f"\n[{datetime.now()}] X8.7 EnergyManager → {result}\n")


if __name__ == "__main__":
    mgr = X8_7_QuantizedEnergyManager()
    print("X8.7 Energy Manager Output:")
    print(mgr.compute_energy())
