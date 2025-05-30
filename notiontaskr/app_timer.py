import logging
import time


class AppTimer:
    def __init__(
        self,
        logger: logging.Logger,
    ) -> None:
        # 開始時間
        self.start_time = 0.0
        # 前回の経過時間
        self.previous_elapsed_time = 0.0
        # ロガー
        self.logger = logger

    @classmethod
    def init_and_start(
        cls,
        logger: logging.Logger,
        message: str = "",
    ) -> "AppTimer":
        """クラスメソッドでインスタンスを初期化し、開始時間を設定する"""
        instance = cls(logger)
        instance.start_time = time.time()
        if message:
            logger.info(f"{message}")
        return instance

    # 前回からの差分を取得
    def snap_delta(self, message: str) -> None:
        """経過時間を取得するメソッド

        少数点以下2桁までの精度で経過時間を取得する。
        """
        if self.start_time is None:
            raise ValueError("Timer has not been started.")

        current_time = time.time()
        elapsed_time = round(current_time - self.start_time, 2)
        diff = elapsed_time - self.previous_elapsed_time
        self.previous_elapsed_time = elapsed_time
        self._log_time(message, diff)

    # 合計経過時間を取得
    def snap_total(self, message: str) -> None:
        """合計経過時間を取得するメソッド"""
        if self.start_time is None:
            raise ValueError("Timer has not been started.")

        current_time = time.time()
        total_elapsed_time = round(current_time - self.start_time, 2)
        self._log_time(message, total_elapsed_time)

    def _log_time(self, message: str, second: float) -> None:
        """ロガーを使用してメッセージをログに記録する"""
        self.logger.info(f"{message} ({second:.2f}s)")
