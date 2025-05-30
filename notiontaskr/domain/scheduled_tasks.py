from dataclasses import dataclass
from typing import TYPE_CHECKING, List

from notiontaskr.domain.name_labels.man_hours_label import ManHoursLabel
from notiontaskr.domain.name_labels.parent_id_label import ParentIdLabel
from notiontaskr.domain.value_objects.man_hours import ManHours
from notiontaskr.domain.executed_tasks import ExecutedTasks
from notiontaskr.domain.tasks import Tasks
from notiontaskr.domain.value_objects.notion_id import NotionId

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

    def update_tasks_properties(self):
        """スケジュールタスクのプロパティを更新する"""
        for task in self._tasks:
            # サブアイテムに親IDラベルを付与する
            task.update_sub_tasks_properties()
            # サブアイテムの工数を集計し、ラベルを更新する
            task.aggregate_man_hours()
            # 予定タスクのステータスを更新する
            task.update_status_by_checking_properties()
            # 進捗率を更新する
            task.calc_progress_rate()
            # 実績人時ラベルを更新する
            task.update_man_hours_label(
                ManHoursLabel.from_man_hours(
                    executed_man_hours=task.executed_man_hours,
                    scheduled_man_hours=task.scheduled_man_hours,
                )
            )
            # 予定タスクが持つ実績タスクのプロパティを更新する
            task.update_executed_tasks_properties()
