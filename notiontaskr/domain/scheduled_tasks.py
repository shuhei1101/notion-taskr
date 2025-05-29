from dataclasses import dataclass
from typing import TYPE_CHECKING, List

from notiontaskr.domain.name_labels.parent_id_label import ParentIdLabel
from notiontaskr.domain.value_objects.man_hours import ManHours
from notiontaskr.domain.executed_tasks import ExecutedTasks
from notiontaskr.domain.tasks import Tasks
from notiontaskr.domain.value_objects.notion_id import NotionId
from notiontaskr.domain.value_objects.page_id import PageId

if TYPE_CHECKING:
    from notiontaskr.domain.scheduled_task import ScheduledTask


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

    def update_parent_id_label(self, parent_id: NotionId) -> "ScheduledTasks":
        """親IDを更新する"""
        for task in self._tasks:
            task.update_parent_id_label(ParentIdLabel.from_property(parent_id))
        return self

    @dataclass
    class AggregatePropertiesResult:
        """集計結果の型"""

        scheduled_man_hours: ManHours
        executed_man_hours: ManHours

    def sum_properties(self) -> "AggregatePropertiesResult":
        """タスクのプロパティを集計する"""
        return self.AggregatePropertiesResult(
            executed_man_hours=sum(
                (task.executed_man_hours for task in self._tasks), start=ManHours(0)
            ),
            scheduled_man_hours=sum(
                (task.scheduled_man_hours for task in self._tasks), start=ManHours(0)
            ),
        )

    def get_updated_tasks(self) -> "ScheduledTasks":
        """更新されたタスクを取得する"""
        return ScheduledTasks.from_tasks(
            [task for task in self._tasks if task.is_updated]
        )

    def get_executed_tasks(self) -> "ExecutedTasks":
        """実績タスクを取得する"""
        executed_tasks = ExecutedTasks.from_empty()
        for task in self._tasks:
            if task.executed_tasks:
                executed_tasks.extend(task.executed_tasks)
        return executed_tasks
