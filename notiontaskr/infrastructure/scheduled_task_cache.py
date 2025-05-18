import os
import pickle
from typing import Callable, List, Optional

from notiontaskr.domain.scheduled_task import ScheduledTask


class ScheduledTaskCache:
    def __init__(self, save_path: str):
        self.save_path = save_path

    def save(
        self,
        tasks: List[ScheduledTask],
        on_success: Optional[Callable[[], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
    ) -> None:
        """Task一覧をファイルに保存する"""
        try:
            with open(self.save_path, "wb") as f:
                pickle.dump(tasks, f)
            on_success() if on_success else None
        except Exception as e:
            on_error(e) if on_error else None

    def load(
        self,
        on_success: Optional[Callable[[], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
    ) -> List[ScheduledTask]:
        """ファイルからTask一覧を読み込む"""
        try:
            if not os.path.exists(self.save_path):
                raise FileNotFoundError(f"Cache file not found: {self.save_path}")
            with open(self.save_path, "rb") as f:
                on_success() if on_success else None
                return pickle.load(f)
        except Exception as e:
            on_error(e) if on_error else None
            return []
