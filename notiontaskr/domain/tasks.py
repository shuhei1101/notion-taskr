from abc import ABC, abstractmethod
import copy
from typing import Generic, Iterator, Type, TypeVar, List, Self
from notiontaskr.domain.task import Task
from notiontaskr.domain.tags import Tags
from notiontaskr.domain.value_objects.tag import Tag

T = TypeVar("T", bound=Task)
SelfType = TypeVar("SelfType", bound="Tasks")


class Tasks(ABC, Generic[T]):
    """Taskのリストを表す抽象基底クラス"""

    _tasks: List[T]

    @abstractmethod
    def get_updated_tasks(self) -> Self:
        """変更されたタスクを取得する"""
        pass

    @classmethod
    @abstractmethod
    def from_empty(cls: Type[SelfType]) -> SelfType:
        pass

    @classmethod
    @abstractmethod
    def from_tasks(cls: Type[SelfType], tasks: List["T"]) -> SelfType:
        pass

    def upserted_by_id(self, tasks: Self) -> Self:
        """IDで重複を除去したタスクのリストを取得する"""
        result_tasks = copy.deepcopy(self)
        result_tasks.upsert_by_id(tasks)
        return result_tasks

    def upsert_by_id(self, tasks: Self) -> None:
        """IDで重複を除去したタスクのリストを追加もしくは更新する"""
        for task in tasks._tasks:
            self.append(task)
        self._tasks = self.get_unique_tasks_by_id()._tasks

    def get_unique_tasks_by_id(self) -> Self:
        """IDで重複を除去したタスクのリストを取得する"""
        return self.from_tasks(list(self.get_tasks_by_id().values()))

    def get_tasks_by_id(self):
        """ID毎のタスク辞書を取得する"""
        return {task.id: task for task in self._tasks}

    def get_tasks_by_page_id(self):
        """ページID毎のタスク辞書を取得する"""
        return {task.page_id: task for task in self._tasks}

    def get_tasks_by_tag(self, tags: "Tags") -> dict[Tag, "Self"]:
        """指定したタグを持つ予定タスクを取得する"""
        scheduled_tasks_by_tags = {tag: self.from_empty() for tag in tags}
        for task in self._tasks:
            for task_tag in task.tags:
                if task_tag in tags:
                    scheduled_tasks_by_tags[task_tag].append(task)
        return scheduled_tasks_by_tags

    def get_remind_tasks(self) -> "Self":
        """リマインド対象のタスクを取得する"""
        return self.from_tasks(
            [
                task
                for task in self._tasks
                if task.remind_info.has_before_start or task.remind_info.has_before_end
            ]
        )

    def __len__(self) -> int:
        """タスクの数を取得する"""
        return len(self._tasks)

    def __getitem__(self, index: int):
        """タスクを取得する"""
        return self._tasks[index]

    def __iter__(self) -> Iterator[T]:
        """タスクをイテレートする"""
        return iter(self._tasks)

    def append(self, task: "T"):
        """スケジュールタスクを追加する"""

        self._tasks.append(task)

    def extend(self, tasks: "Self"):
        """スケジュールタスクを追加する"""

        self._tasks.extend(tasks._tasks)
