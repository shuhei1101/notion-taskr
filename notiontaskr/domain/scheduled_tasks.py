from dataclasses import dataclass
from typing import List

from notiontaskr.domain.scheduled_task import ScheduledTask

from notiontaskr.domain.tags import Tags

from notiontaskr.domain.value_objects.tag import Tag


@dataclass
class ScheduledTasks:
    """スケジュールタスクを管理するクラス"""

    _tasks: List[ScheduledTask]

    @classmethod
    def from_empty(cls):
        return cls(_tasks=[])

    @classmethod
    def from_tasks(cls, tasks: List[ScheduledTask]):
        return cls(
            _tasks=tasks,
        )

    def append(self, task: ScheduledTask):
        """スケジュールタスクを追加する"""

        self._tasks.append(task)

    def extend(self, tasks: "ScheduledTasks"):
        """スケジュールタスクを追加する"""

        self._tasks.extend(tasks._tasks)

    def __len__(self):
        return len(self._tasks)

    def __iter__(self):
        return iter(self._tasks)

    def __getitem__(self, index: int):
        return self._tasks[index]

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
