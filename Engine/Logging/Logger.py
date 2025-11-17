# Engine/Logging/Logger.py

import os
from datetime import datetime

class Logger:
    def __init__(self, name="Engine", base_dir="logs"):
        self.name = name
        self.base_dir = base_dir

        # ساخت پوشه لاگ اگر وجود ندارد
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

        # نام فایل لاگ روزانه
        self.file_path = os.path.join(base_dir, f"{name}_{datetime.now().date()}.log")

    def _write(self, level, msg):
        time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{time_str}] [{self.name}] [{level}] {msg}"

        # چاپ روی کنسول
        print(line)

        # ذخیره در فایل
        with open(self.file_path, "a", encoding="utf-8") as f:
            f.write(line + "\n")

    def info(self, msg):
        self._write("INFO", msg)

    def warning(self, msg):
        self._write("WARNING", msg)

    def error(self, msg):
        self._write("ERROR", msg)
