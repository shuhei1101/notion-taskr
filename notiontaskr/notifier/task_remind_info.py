from dataclasses import dataclass
from typing import Optional

from notiontaskr.notifier.remind_minutes import RemindMinutes


@dataclass
class TaskRemindInfo:
    has_before_start: bool = False
    has_before_end: bool = False
    before_start_minutes: RemindMinutes = RemindMinutes(minutes=5)
    before_end_minutes: RemindMinutes = RemindMinutes(minutes=5)

    @classmethod
    def from_empty(cls) -> "TaskRemindInfo":
        """空のリマインド情報を生成する"""
        return cls(
            has_before_start=False,
            has_before_end=False,
            before_start_minutes=RemindMinutes(minutes=5),
            before_end_minutes=RemindMinutes(minutes=5),
        )

    @classmethod
    def from_raw_values(
        cls,
        has_before_start: bool = False,
        has_before_end: bool = False,
        raw_before_start_minutes: Optional[int] = 5,
        raw_before_end_minutes: Optional[int] = 5,
    ) -> "TaskRemindInfo":
        if raw_before_start_minutes is None:
            raw_before_start_minutes = 5
        if raw_before_end_minutes is None:
            raw_before_end_minutes = 5

        if raw_before_start_minutes < 0:
            raise ValueError("before_start_minutesは0以上でなければなりません")
        if raw_before_end_minutes < 0:
            raise ValueError("before_end_minutesは0以上でなければなりません")

        before_start_minutes = RemindMinutes(minutes=raw_before_start_minutes)
        before_end_minutes = RemindMinutes(minutes=raw_before_end_minutes)

        return cls(
            has_before_start=has_before_start,
            has_before_end=has_before_end,
            before_start_minutes=before_start_minutes,
            before_end_minutes=before_end_minutes,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TaskRemindInfo):
            return NotImplemented
        return (
            self.has_before_start == other.has_before_start
            and self.has_before_end == other.has_before_end
            and self.before_start_minutes == other.before_start_minutes
            and self.before_end_minutes == other.before_end_minutes
        )
