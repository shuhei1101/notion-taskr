import os
import pickle
from typing import List

from notiontaskr.domain.scheduled_task import ScheduledTask


class ScheduledTaskCache:
    def __init__(self, save_path: str):
        self.save_path = save_path

    def save(
        self,
        tasks: List[ScheduledTask],
    ) -> None:
        """Task一覧をファイルに保存する"""
        try:
            with open(self.save_path, "wb") as f:
                pickle.dump(tasks, f)
        except Exception as e:
            raise e

    def load(
        self,
    ) -> List[ScheduledTask]:
        """ファイルからTask一覧を読み込む"""
        try:
            if not os.path.exists(self.save_path):
                raise FileNotFoundError(f"Cache file not found: {self.save_path}")
            with open(self.save_path, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            raise e
