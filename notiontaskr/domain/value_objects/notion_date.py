from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


@dataclass
class NotionDate:
    start: datetime
    end: datetime

    def __init__(self, start: datetime, end: Optional[datetime]):
        if not isinstance(start, datetime):
            raise TypeError(f"開始日はdatetime型でなければなりません。")
        if not end:
            end = start
            # 時刻を23:59:59に設定
            end = end.replace(hour=23, minute=59, second=59, microsecond=999999)
        # tzinfo がない場合、UTC を追加
        if start.tzinfo is None:
            start = start.replace(tzinfo=timezone.utc)
        if end.tzinfo is None:
            end = end.replace(tzinfo=timezone.utc)
        if start > end:
            raise ValueError(
                f"開始日`{start}`は終了日`{end}`よりも前でなければなりません。"
            )
        self.start = start
        self.end = end

    @classmethod
    def from_raw_date(cls, start: str, end: Optional[str]):
        """文字列からNotionDateを生成する"""
        end_date = None
        if not start:
            raise ValueError(f"開始日は必須です。")
        if end:
            end_date = datetime.fromisoformat(end)
        start_date = datetime.fromisoformat(start)
        return cls(start=start_date, end=end_date)

    @classmethod
    def from_response_data(cls, data: dict) -> "NotionDate":
        """レスポンスデータからインスタンスを生成する"""
        try:
            start_date_str = data["properties"]["日付"]["date"]["start"]
            end_date_str = data["properties"]["日付"]["date"]["end"]
            return cls.from_raw_date(start=start_date_str, end=end_date_str)
        except (KeyError, TypeError, KeyError) as e:
            raise ValueError(f"レスポンスデータに必要なキーが存在しません: {e}")
