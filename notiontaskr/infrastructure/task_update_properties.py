from abc import ABC

from notiontaskr.domain.task import Task


class TaskUpdateProperties(ABC):
    """タスクの更新用プロパティ辞書を生成するクラス"""

    def __init__(self, task: Task):
        self.task = task
        self.properties = {}

    def set_name(self):
        """名前の更新"""
        self.properties["名前"] = {
            "title": [{"text": {"content": self.task.get_display_name()}}]
        }
        return self

    def set_parent_task_page_id(self):
        """親アイテム(予)の更新"""
        if self.task.parent_task_page_id:
            self.properties["親アイテム(予)"] = {
                "relation": [{"id": str(self.task.parent_task_page_id)}]
            }
        return self

    def set_status(self):
        """ステータスの更新"""
        self.properties["ステータス"] = {"status": {"name": str(self.task.status)}}
        return self

    def set_has_before_start(self):
        """開始前通知の更新"""
        self.properties["開始前通知"] = {
            "checkbox": self.task.remind_info.has_before_start
        }
        return self

    def set_has_before_end(self):
        """終了前通知の更新"""
        self.properties["終了前通知"] = {
            "checkbox": self.task.remind_info.has_before_end
        }
        return self

    def set_before_start_minutes(self):
        """開始前通知時間(分)の更新"""
        self.properties["開始前通知時間(分)"] = {
            "number": int(self.task.remind_info.before_start_minutes)
        }
        return self

    def set_before_end_minutes(self):
        """終了前通知時間(分)の更新"""
        self.properties["終了前通知時間(分)"] = {
            "number": int(self.task.remind_info.before_end_minutes)
        }
        return self

    def build(self):
        """更新用の最終プロパティを返す"""
        return self.properties if self.properties else {}
