import time
import traceback

from Engine.Runner.AutoEngine_Runner import AutoEngineRunner
from Engine.Logging.Logger import Logger


def main():
    logger = Logger("Launcher")

    while True:
        try:
            logger.info("Starting AutoEngine Runner...")
            runner = AutoEngineRunner("config/runner_config.json")
            runner.run()

        except Exception as e:
            logger.error(f"Engine crashed: {e}\n{traceback.format_exc()}")
            logger.info("Restarting engine in 5 seconds...")
            time.sleep(5)


if __name__ == "__main__":
    main()
