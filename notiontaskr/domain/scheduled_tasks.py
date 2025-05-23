from dataclasses import dataclass
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from notiontaskr.domain.scheduled_task import ScheduledTask
from notiontaskr.domain.tags import Tags
from notiontaskr.domain.value_objects.tag import Tag
from notiontaskr.domain.tasks import Tasks

from notiontaskr.domain.value_objects.notion_id import NotionId

from notiontaskr.domain.value_objects.page_id import PageId


@dataclass
class ScheduledTasks(Tasks["ScheduledTask"]):
    """スケジュールタスクを管理するクラス"""

    _tasks: List["ScheduledTask"]

    def _get_tasks(self):
        return self._tasks

    @classmethod
    def from_empty(cls):
        return cls(_tasks=[])

    @classmethod
    def from_tasks(cls, tasks: List["ScheduledTask"]):
        return cls(
            _tasks=tasks,
        )

    @classmethod
    def from_tasks_by_id(cls, tasks_by_id: dict[NotionId, "ScheduledTask"]):
        return cls(
            _tasks=list(tasks_by_id.values()),
        )

    @classmethod
    def from_tasks_by_page_id(cls, tasks_by_page_id: dict[PageId, "ScheduledTask"]):
        return cls(
            _tasks=list(tasks_by_page_id.values()),
        )

    def append(self, task: "ScheduledTask"):
        """スケジュールタスクを追加する"""

        self._tasks.append(task)

    def extend(self, tasks: "ScheduledTasks"):
        """スケジュールタスクを追加する"""

        self._tasks.extend(tasks._tasks)

    def upsert_by_id(self, task: "ScheduledTask"):
        """スケジュールタスクをIDで更新する"""
        self._tasks.append(task)
        self._tasks = list(self.get_tasks_by_id().values())

    def get_tasks_by_id(self):
        return {task.id: task for task in self._tasks}

    def get_tasks_by_page_id(self):
        return {task.page_id: task for task in self._tasks}

    def get_tasks_by_tag(self, tags: "Tags") -> dict[Tag, "ScheduledTasks"]:
        """指定したタグを持つスケジュールタスクを取得する"""
        scheduled_tasks_by_tags = {tag: ScheduledTasks.from_empty() for tag in tags}
        for task in self._tasks:
            for task_tag in task.tags:
                if task_tag in tags:
                    scheduled_tasks_by_tags[task_tag].append(task)
        return scheduled_tasks_by_tags
