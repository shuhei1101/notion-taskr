from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from notiontaskr.domain.value_objects.notion_date import NotionDate


@dataclass
class TaskRemindInfo:
    has_before_start: bool = False
    has_before_end: bool = False
    before_start_minutes: timedelta = timedelta(minutes=5)
    before_end_minutes: timedelta = timedelta(minutes=5)
    before_start_dt: Optional["datetime"] = None
    before_end_dt: Optional["datetime"] = None

    @classmethod
    def from_raw_values(
        cls,
        task_date: NotionDate,
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

        before_start_minutes = timedelta(minutes=raw_before_start_minutes)
        before_end_minutes = timedelta(minutes=raw_before_end_minutes)

        before_start_dt = None
        before_end_dt = None

        if has_before_start:
            before_start_dt = task_date.start - before_start_minutes
        if has_before_end:
            before_end_dt = task_date.end - before_end_minutes

        return cls(
            has_before_start=has_before_start,
            has_before_end=has_before_end,
            before_start_minutes=before_start_minutes,
            before_end_minutes=before_end_minutes,
            before_start_dt=before_start_dt,
            before_end_dt=before_end_dt,
        )
