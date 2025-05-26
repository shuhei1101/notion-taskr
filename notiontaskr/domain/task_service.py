from typing import TypeVar
from notiontaskr.domain.task import Task

T = TypeVar("T", bound=Task)


class TaskService:

    @staticmethod
    def upsert_tasks(to: list[T], source: T):
        """タスクを追加または更新する"""
        for i, task in enumerate(to):
            if task.id == source.id:
                to[i] = source  # 上書き
                return
        to.append(source)  # 見つからなければ追加
