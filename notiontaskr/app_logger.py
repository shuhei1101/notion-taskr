import logging
from notiontaskr import config


class AppLogger:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(AppLogger, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):
            self.logger = logging.getLogger("AppLogger")
            self.logger.setLevel(config.LOG_LEVEL)

            # StreamHandler
            sh = logging.StreamHandler()
            sh_formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            sh.setFormatter(sh_formatter)
            self.logger.addHandler(sh)

            # TimedRotatingFileHandler
            # trfh = TimedRotatingFileHandler(config.LOG_PATH, when="midnight", interval=1, backupCount=7)
            # trfh_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            # trfh.setFormatter(trfh_formatter)
            # self.logger.addHandler(trfh)

            self._initialized = True

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def error(self, message):
        self.logger.error(message)

    def warning(self, message):
        self.logger.warning(message)

    def critical(self, message):
        self.logger.critical(message)


# 動作確認用
if __name__ == "__main__":
    AppLogger().debug("This is a debug message")
    AppLogger().info("This is an info message")
    AppLogger().warning("This is a warning message")
    AppLogger().error("This is an error message")
    AppLogger().critical("This is a critical message")
