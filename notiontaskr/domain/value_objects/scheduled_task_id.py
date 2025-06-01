from typing import Optional
from notiontaskr.domain.value_objects.notion_id import NotionId


class ScheduledTaskId(NotionId):
    """スケジュールされたタスクのIDを表すクラス。

    NotionのタスクIDを継承し、スケジュールされたタスクに特化した機能を提供します。
    """

    @classmethod
    def from_task_name(cls, task_name) -> "Optional[ScheduledTaskId]":
        """タスク名からScheduledTaskIdを生成します。

        Args:
            task_name (TaskName): タスク名オブジェクト。

        Returns:
            ScheduledTaskId: タスク名から生成されたScheduledTaskId。
        """
        if task_name.id_label is None:
            return None
        return cls(task_name.id_label.value)
