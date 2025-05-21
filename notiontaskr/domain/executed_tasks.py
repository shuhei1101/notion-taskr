from dataclasses import dataclass
from typing import List

from notiontaskr.domain.executed_task import ExecutedTask


@dataclass
class ExecutedTasks:
    """
    実績タスクを管理するクラス
    """

    tasks: List[ExecutedTask]

    @classmethod
    def from_empty(cls):
        return cls(tasks=[])

    @classmethod
    def from_tasks(cls, tasks: List[ExecutedTask]):
        return cls(
            tasks=tasks,
        )

    def append(self, task: ExecutedTask):
        """実績タスクを追加する"""

        self.tasks.append(task)

    def __len__(self):
        return len(self.tasks)

    def get_tasks_by_id(self):
        return {task.id: task for task in self.tasks}

    def get_tasks_by_page_id(self):
        return {task.page_id: task for task in self.tasks}
