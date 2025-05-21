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

    tasks: List[ExecutedTask]

    @classmethod
    def from_empty(cls):
        return cls(
            tasks=[]
        )

    @classmethod
    def from_tasks(cls, tasks: List[ExecutedTask]):
        return cls(
            tasks=tasks,
        )

    def upsert(self, task: ExecutedTask):
        """実績タスクを追加する"""

        if not task.id or not task.page_id or not task.name:
            raise ValueError("実績タスクにはID、ページID、名前が必要です")
        self.tasks.append(task)

    def __len__(self):
        return len(self.tasks)

    def get_by_id(self, id: NotionId) -> ExecutedTask | None:
        """NotionIdを指定し対象の実績タスクを取得する"""
        return self.executed_tasks_by_id.get(id)

    def get_by_page_id(self, page_id: PageId) -> ExecutedTask | None:
        """ページIDを指定し対象の実績タスクを取得する"""
        return self.executed_tasks_by_page_id.get(page_id)
