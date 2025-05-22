from abc import ABC, abstractmethod
from typing import Generic, Iterator, TypeVar, List

from notiontaskr.domain.task import Task

T = TypeVar("T", bound=Task)


class Tasks(ABC, Generic[T]):
    """Taskのリストを表す抽象基底クラス"""

    @abstractmethod
    def _get_tasks(self) -> List[T]:  # type: ignore
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

    def __iter__(self) -> Iterator[T]:
        """タスクをイテレートする"""
        return iter(self._get_tasks())

    def get_updated_tasks(self):
        """変更されたタスクを取得する"""
        return list(filter(lambda task: task.is_updated, self._get_tasks()))
