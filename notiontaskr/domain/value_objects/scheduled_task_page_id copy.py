from typing import Optional
from notiontaskr.domain.value_objects.page_id import PageId


class ScheduledTaskPageId(PageId):
    """親タスクのページIDを表すクラス"""

    @classmethod
    def from_response_data_for_scheduled_task(cls, data: dict) -> "Optional[ScheduledTaskPageId]":  # type: ignore
        """レスポンスデータからParentTaskPageIdのインスタンスを生成します"""
        try:
            return cls(value=data["properties"]["予定タスク"]["relation"][0]["id"])
        except (KeyError, IndexError, TypeError):
            return None
