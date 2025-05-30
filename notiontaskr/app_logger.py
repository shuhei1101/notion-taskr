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
            self.logger = logging.getLogger("notiontaskr")
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

    def get(self):
        """ロガーを返す"""
        return self.logger
