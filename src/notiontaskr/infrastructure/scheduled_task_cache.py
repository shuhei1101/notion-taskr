import os
import pickle
from typing import Callable, List

from notiontaskr.domain.scheduled_task import ScheduledTask


class ScheduledTaskCache:
    def __init__(self, save_path: str):
        self.save_path = save_path

    def save(self, tasks: List[ScheduledTask],
             on_success: Callable[[None], None] = None,
             on_error: Callable[[Exception], None] = None
             ) -> None:
        '''Task一覧をファイルに保存する'''
        try:
            with open(self.save_path, "wb") as f:
                pickle.dump(tasks, f)
            on_success() if on_success else None
        except Exception as e:
            on_error(e) if on_error else None

    def load(self,
             on_success: Callable[[None], None] = None,
             on_error: Callable[[Exception], None] = None
             ) -> List[ScheduledTask]:
        '''ファイルからTask一覧を読み込む'''
        try:
            if not os.path.exists(self.save_path):
                raise FileNotFoundError(f"Cache file not found: {self.save_path}")
            with open(self.save_path, "rb") as f:
                on_success() if on_success else None
                return pickle.load(f)
        except Exception as e:
            on_error(e) if on_error else None

# 動作確認
if __name__ == "__main__":
    from notiontaskr.domain.value_objects.man_hours import ManHours
    # テスト用のデータを作成
    tasks = [
        ScheduledTask(
            page_id="page_1",
            name="Task 1",
            tags=["tag1", "tag2"],
            id="id_1",
            status="Not Started",
            scheduled_man_hours=ManHours(5),
            executed_man_hours=ManHours(3),
            executed_tasks=[]
        ),
        ScheduledTask(
            page_id="page_2",
            name="Task 2",
            tags=["tag3"],
            id="id_2",
            status="In Progress",
            scheduled_man_hours=ManHours(8),
            executed_man_hours=ManHours(6),
            executed_tasks=[]
        )
    ]
    
    # キャッシュに保存
    cache = ScheduledTaskCache()
    cache.save(tasks)
    
    # キャッシュから読み込み
    loaded_tasks = cache.load()
    
    # 読み込んだデータを見やすく表示
    for task in loaded_tasks:
        print(f"Task Name: {task.name}")
        print(f"  Page ID: {task.page_id}")
        print(f"  Tags: {', '.join(task.tags)}")
        print(f"  ID: {task.id}")
        print(f"  Status: {task.status}")
        print(f"  Executed Tasks: {task.executed_tasks}")
        print("-" * 40)

        