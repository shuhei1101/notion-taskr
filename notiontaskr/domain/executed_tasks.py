from dataclasses import dataclass
from typing import List

from notiontaskr.domain.executed_task import ExecutedTask
from notiontaskr.domain.value_objects.man_hours import ManHours
from notiontaskr.domain.tasks import Tasks


@dataclass
class ExecutedTasks(Tasks[ExecutedTask]):
    """実績タスクを管理するクラス"""

    _tasks: List[ExecutedTask]

    @classmethod
    def from_empty(cls):
        return cls(_tasks=[])

    @classmethod
    def from_tasks(cls, tasks: List[ExecutedTask]):
        return cls(
            _tasks=tasks,
        )

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
