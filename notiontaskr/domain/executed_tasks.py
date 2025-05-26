from dataclasses import dataclass
from typing import List

from notiontaskr.domain.executed_task import ExecutedTask
from notiontaskr.domain.tags import Tags
from notiontaskr.domain.value_objects.tag import Tag
from notiontaskr.domain.value_objects.man_hours import ManHours
from notiontaskr.domain.tasks import Tasks

from notiontaskr.domain.value_objects.notion_id import NotionId

from notiontaskr.domain.value_objects.page_id import PageId


@dataclass
class ExecutedTasks(Tasks[ExecutedTask]):
    """実績タスクを管理するクラス"""

    _tasks: List[ExecutedTask]

    def _get_tasks(self):
        return self._tasks

    @classmethod
    def from_empty(cls):
        return cls(_tasks=[])

    @classmethod
    def from_tasks(cls, tasks: List[ExecutedTask]):
        return cls(
            _tasks=tasks,
        )

    @classmethod
    def from_tasks_by_id(cls, tasks_by_id: dict[NotionId, ExecutedTask]):
        return cls(
            _tasks=list(tasks_by_id.values()),
        )

    @classmethod
    def from_tasks_by_page_id(cls, tasks_by_page_id: dict[PageId, ExecutedTask]):
        return cls(
            _tasks=list(tasks_by_page_id.values()),
        )

    def append(self, task: ExecutedTask):
        """実績タスクを追加する"""

        self._tasks.append(task)

    def extend(self, tasks: "ExecutedTasks"):
        """実績タスクを追加する"""

        self._tasks.extend(tasks._tasks)

    def upsert_by_id(self, task: ExecutedTask):
        """実績タスクをIDで更新する"""
        self._tasks.append(task)
        self._tasks = list(self.get_tasks_by_id().values())

    def get_tasks_by_id(self):
        return {task.id: task for task in self._tasks}

    def get_tasks_by_page_id(self):
        return {task.page_id: task for task in self._tasks}

    def get_tasks_by_tag(self, tags: "Tags") -> dict[Tag, "ExecutedTasks"]:
        """指定したタグを持つ実績タスクを取得する"""
        executed_tasks_by_tags = {tag: ExecutedTasks.from_empty() for tag in tags}
        for task in self._tasks:
            for task_tag in task.tags:
                if task_tag in tags:
                    executed_tasks_by_tags[task_tag].append(task)
        return executed_tasks_by_tags

    def get_total_man_hours(self) -> ManHours:
        """実績タスクの工数の合計を取得する"""
        total_man_hours = ManHours(0.0)
        for task in self._tasks:
            total_man_hours += task.man_hours

        return total_man_hours

    @dataclass
    class AggregatePropertiesResult:
        """集計結果の型"""

        man_hours: ManHours

    def sum_properties(self) -> "AggregatePropertiesResult":
        """タスクのプロパティを集計する"""
        return self.AggregatePropertiesResult(
            man_hours=sum((task.man_hours for task in self._tasks), start=ManHours(0)),
        )

    def get_updated_tasks(self) -> "ExecutedTasks":
        """更新されたタスクを取得する"""
        return ExecutedTasks.from_tasks(
            [task for task in self._tasks if task.is_updated]
        )
