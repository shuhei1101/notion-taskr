from dataclasses import dataclass
from datetime import timedelta
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from notiontaskr.domain.name_labels.remind_label import RemindLabel


@dataclass
class TaskRemindInfo:
    has_before_start: bool = False
    has_before_end: bool = False
    before_start_minutes: timedelta = timedelta(minutes=5)
    before_end_minutes: timedelta = timedelta(minutes=5)

    @classmethod
    def from_raw_values(
        cls,
        has_before_start: bool = False,
        has_before_end: bool = False,
        before_start_minutes: Optional[int] = 5,
        before_end_minutes: Optional[int] = 5,
    ) -> "TaskRemindInfo":
        if before_start_minutes is None:
            before_start_minutes = 5
        if before_end_minutes is None:
            before_end_minutes = 5

        if before_start_minutes < 0:
            raise ValueError("before_start_minutesは0以上でなければなりません")
        if before_end_minutes < 0:
            raise ValueError("before_end_minutesは0以上でなければなりません")
        return cls(
            has_before_start=has_before_start,
            has_before_end=has_before_end,
            before_start_minutes=timedelta(minutes=before_start_minutes),
            before_end_minutes=timedelta(minutes=before_end_minutes),
        )

    @classmethod
    def from_remind_label(cls, label: "RemindLabel") -> "TaskRemindInfo":
        if not label.value:
            return cls()

        parts = label.value.split("|")
        # mを取り除いて整数に変換
        before_start_minutes = int(parts[0].replace("m", "")) if parts[0] else 5
        before_end_minutes = (
            int(parts[1].replace("m", "")) if len(parts) > 1 and parts[1] else 5
        )

        return cls.from_raw_values(
            has_before_start=bool(parts[0]),
            has_before_end=bool(parts[1]),
            before_start_minutes=before_start_minutes,
            before_end_minutes=before_end_minutes,
        )
