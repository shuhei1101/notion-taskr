from notiontaskr.domain.scheduled_task import ScheduledTask
from notiontaskr.infrastructure.task_update_properties import TaskUpdateProperties


class ScheduledTaskUpdateProperties(TaskUpdateProperties):
    """予定タスクの更新用プロパティ辞書を生成するクラス"""

    def __init__(self, task: ScheduledTask):
        super().__init__(task)
        self.task = task

    def set_executed_man_hours(self):
        """実際の人日数の更新"""
        self.properties["人時(実)"] = {"number": self.task.executed_man_hours.value}
        return self

    def set_scheduled_man_hours(self):
        """実際の人日数の更新"""
        self.properties["人時(予)"] = {"number": self.task.scheduled_man_hours.value}
        return self

    def set_progress_rate(self):
        """進捗率の更新"""
        self.properties["進捗率"] = {
            "number": self.task.progress_rate.value,
        }
        return self
