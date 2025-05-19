from typing import TypeVar
from notiontaskr.domain.task import Task

T = TypeVar("T", bound=Task)


class TaskService:
    @staticmethod
    def get_updated_tasks(tasks: list[T]):
        """変更されたタスクを取得する"""
        updated_tasks = list(filter(lambda task: task.is_updated, tasks))

        return updated_tasks

    @staticmethod
    def upsert_tasks(to: list[T], source: T):
        """タスクを追加または更新する"""
        for i, task in enumerate(to):
            if task.id == source.id:
                to[i] = source  # 上書き
                return
        to.append(source)  # 見つからなければ追加
