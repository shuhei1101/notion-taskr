from typing import Optional
from notiontaskr.domain.value_objects.page_id import PageId


class ParentTaskPageId(PageId):
    """親タスクのページIDを表すクラス"""

    @classmethod
    def from_response_data_for_scheduled_task(cls, data: dict) -> "Optional[ParentTaskPageId]":  # type: ignore
        """スケジュールされたタスクのレスポンスデータからParentTaskPageIdのインスタンスを生成します"""
        try:
            return cls(value=data["properties"]["親アイテム"]["relation"][0]["id"])
        except (KeyError, IndexError, TypeError):
            return None

    @classmethod
    def from_response_data_for_executed_task(
        cls, data: dict
    ) -> "Optional[ParentTaskPageId]":
        """実績タスクのレスポンスデータからParentTaskPageIdのインスタンスを生成します"""
        try:
            return cls(value=data["properties"]["親アイテム(予)"]["relation"][0]["id"])
        except (KeyError, IndexError, TypeError):
            return None
