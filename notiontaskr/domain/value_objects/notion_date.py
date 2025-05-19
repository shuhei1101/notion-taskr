from dataclasses import dataclass
from datetime import datetime


@dataclass
class NotionDate:
    start: datetime
    end: datetime

    def __init__(self, start: datetime, end: datetime):
        if not isinstance(start, datetime):
            raise TypeError(f"開始日はdatetime型でなければなりません。")
        if not end:
            end = start
        if start > end:
            raise ValueError(
                f"開始日`{start}`は終了日`{end}`よりも前でなければなりません。"
            )
        self.start = start
        self.end = end

    @classmethod
    def from_raw_date(cls, start: str, end: str):
        """文字列からNotionDateを生成する"""
        if not start:
            raise ValueError(f"開始日は必須です。")
        if not end:
            end = start
        start_date = datetime.fromisoformat(start)
        end_date = datetime.fromisoformat(end)
        return cls(start=start_date, end=end_date)
