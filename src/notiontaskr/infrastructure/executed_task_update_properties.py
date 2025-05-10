from notiontaskr.domain.executed_task import ExecutedTask
from notiontaskr.infrastructure.task_update_properties import TaskUpdateProperties


class ExecutedTaskUpdateProperties(TaskUpdateProperties):
    """実績タスクの更新用プロパティ辞書を生成するクラス"""

    def __init__(self, task: ExecutedTask):
        super().__init__(task)
        self.task = task

    def set_scheduled_task_page_id(self):
        """予定タスクの更新"""
        if self.task.scheduled_task_page_id:
            self.properties["予定タスク"] = {
                "relation": [{"id": str(self.task.scheduled_task_page_id)}]
            }
        return self
