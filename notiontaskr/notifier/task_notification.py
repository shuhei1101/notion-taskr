from dataclasses import dataclass
from datetime import timedelta


@dataclass
class TaskNotification:
    has_before_start: bool = False
    has_after_start: bool = False
    before_start_minutes: timedelta = timedelta(minutes=5)
    after_start_minutes: timedelta = timedelta(minutes=5)

    @classmethod
    def from_raw_values(
        cls,
        has_before_start: bool = False,
        has_after_start: bool = False,
        before_start_minutes: int = 5,
        after_start_minutes: int = 5,
    ) -> "TaskNotification":
        if before_start_minutes < 0:
            raise ValueError("before_start_minutesは0以上でなければなりません")
        if after_start_minutes < 0:
            raise ValueError("after_start_minutesは0以上でなければなりません")
        return cls(
            has_before_start=has_before_start,
            has_after_start=has_after_start,
            before_start_minutes=timedelta(minutes=before_start_minutes),
            after_start_minutes=timedelta(minutes=after_start_minutes),
        )
