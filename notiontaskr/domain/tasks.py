from abc import ABC, abstractmethod


class Tasks(ABC):
    """Taskのリストを表す抽象基底クラス"""

    @abstractmethod
    def _get_tasks(self) -> list:
        """タスクのリストを取得する

        :return Tasks: Tasksを継承したクラスのインスタンス

        このメソッドは、各実装クラスで自身のタスクのリストを返すように実装すること
        """
        pass

    def __len__(self) -> int:
        """タスクの数を取得する"""
        return len(self._get_tasks())

    def __getitem__(self, index: int):
        """タスクを取得する"""
        return self._get_tasks()[index]

    def __iter__(self):
        """タスクをイテレートする"""
        return iter(self._get_tasks())

    def get_updated_tasks(self):
        """変更されたタスクを取得する"""
        return [task for task in self._get_tasks() if task.is_updated]
