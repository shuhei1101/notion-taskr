from dataclasses import dataclass
from typing import List

from notiontaskr.domain.executed_task import ExecutedTask

from notiontaskr.domain.tags import Tags

from notiontaskr.domain.value_objects.tag import Tag


@dataclass
class ExecutedTasks:
    """
    実績タスクを管理するクラス
    """

    _tasks: List[ExecutedTask]

    @classmethod
    def from_empty(cls):
        return cls(_tasks=[])

    @classmethod
    def from_tasks(cls, tasks: List[ExecutedTask]):
        return cls(
            _tasks=tasks,
        )

    def append(self, task: ExecutedTask):
        """実績タスクを追加する"""

        self._tasks.append(task)

    def extend(self, tasks: "ExecutedTasks"):
        """実績タスクを追加する"""

        self._tasks.extend(tasks._tasks)

    def __len__(self):
        return len(self._tasks)

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
