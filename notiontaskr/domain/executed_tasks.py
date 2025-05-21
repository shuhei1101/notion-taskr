from dataclasses import dataclass
from typing import List

from notiontaskr.domain.executed_task import ExecutedTask

from notiontaskr.domain.value_objects.notion_id import NotionId

from notiontaskr.domain.value_objects.page_id import PageId


@dataclass
class ExecutedTasks:
    """
    実績タスクを管理するクラス
    """

    executed_tasks: List[ExecutedTask]
    executed_tasks_by_id: dict
    executed_tasks_by_page_id: dict

    @classmethod
    def from_empty(cls):
        return cls(
            executed_tasks=[], executed_tasks_by_id={}, executed_tasks_by_page_id={}
        )

    @classmethod
    def from_tasks(cls, tasks: List[ExecutedTask]):
        return cls(
            executed_tasks=tasks,
            executed_tasks_by_id={task.id: task for task in tasks},
            executed_tasks_by_page_id={
                task.page_id: task for task in tasks if task.page_id is not None
            },
        )

    def upsert(self, task: ExecutedTask):
        """実績タスクを追加する"""
        if not task.id or not task.page_id or not task.name:
            raise ValueError("実績タスクにはID、ページID、名前が必要です")
        self.executed_tasks_by_page_id[task.page_id] = task
        self.executed_tasks_by_id[task.id] = task
        self.executed_tasks_by_name[task.name.task_name] = task
        self.executed_tasks.append(task)

    def __len__(self):
        return len(self.executed_tasks)

    def get_by_id(self, id: NotionId) -> ExecutedTask | None:
        """NotionIdを指定し対象の実績タスクを取得する"""
        return self.executed_tasks_by_id.get(id)

    def get_by_page_id(self, page_id: PageId) -> ExecutedTask | None:
        """ページIDを指定し対象の実績タスクを取得する"""
        return self.executed_tasks_by_page_id.get(page_id)
