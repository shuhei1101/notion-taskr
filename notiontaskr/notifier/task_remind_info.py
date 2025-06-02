from dataclasses import dataclass
from typing import Optional

from notiontaskr import config
from notiontaskr.notifier.remind_minutes import RemindMinutes


@dataclass
class TaskRemindInfo:
    before_start_minutes: Optional[RemindMinutes] = None
    before_end_minutes: Optional[RemindMinutes] = None
    has_before_start: bool = False
    has_before_end: bool = False
    has_start: bool = False
    has_end: bool = False

    @classmethod
    def from_empty(cls) -> "TaskRemindInfo":
        """空のリマインド情報を生成する"""
        return cls()

    @classmethod
    def from_raw_values(
        cls,
        has_before_start: bool = False,
        has_before_end: bool = False,
        raw_before_start_minutes: Optional[int] = None,
        raw_before_end_minutes: Optional[int] = None,
        has_start: bool = False,
        has_end: bool = False,
    ) -> "TaskRemindInfo":
        if raw_before_start_minutes is None:
            before_start_minutes = None
        else:
            if raw_before_start_minutes < 0:
                raise ValueError("before_start_minutesは0以上でなければなりません")
            before_start_minutes = RemindMinutes(minutes=raw_before_start_minutes)

        if raw_before_end_minutes is None:
            before_end_minutes = None
        else:
            if raw_before_end_minutes < 0:
                raise ValueError("before_end_minutesは0以上でなければなりません")
            before_end_minutes = RemindMinutes(minutes=raw_before_end_minutes)

        return cls(
            has_before_start=has_before_start,
            has_before_end=has_before_end,
            before_start_minutes=before_start_minutes,
            before_end_minutes=before_end_minutes,
            has_start=has_start,
            has_end=has_end,
        )

    @classmethod
    def from_response_data(cls, data: dict) -> "TaskRemindInfo":
        """レスポンスデータからインスタンスを生成する"""
        try:
            return cls.from_raw_values(
                has_before_start=data["properties"]["開始前通知"]["checkbox"],
                has_before_end=data["properties"]["終了前通知"]["checkbox"],
                raw_before_start_minutes=data["properties"]["開始前通知時間(分)"].get(
                    "number"
                ),
                raw_before_end_minutes=data["properties"]["終了前通知時間(分)"].get(
                    "number"
                ),
                has_start=data["properties"]["開始通知"]["checkbox"],
                has_end=data["properties"]["終了通知"]["checkbox"],
            )
        except (KeyError, TypeError) as e:
            raise ValueError(f"レスポンスデータに必要なキーが存在しません")

    def get_default_self(self):
        """デフォルト値で初期化する"""
        before_start_minutes = self.before_start_minutes
        if before_start_minutes is None:
            before_start_minutes = RemindMinutes(
                minutes=config.DEFAULT_BEFORE_START_MINUTES
            )

        before_end_minutes = self.before_end_minutes
        if before_end_minutes is None:
            before_end_minutes = RemindMinutes(
                minutes=config.DEFAULT_BEFORE_END_MINUTES
            )

        return TaskRemindInfo(
            has_before_start=self.has_before_start,
            has_before_end=self.has_before_end,
            before_start_minutes=before_start_minutes,
            before_end_minutes=before_end_minutes,
        )

    def has_value(self) -> bool:
        """値が存在するか調べる"""
        return (
            self.before_start_minutes is not None or self.before_end_minutes is not None
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

    def __str__(self) -> str:
        return (
            f"開始前通知={self.has_before_start}, "
            f"終了前通知={self.has_before_end}, "
            f"開始前通知時間(分)={self.before_start_minutes}, "
            f"終了前通知時間(分)={self.before_end_minutes}), "
            f"開始通知={self.has_start}, "
            f"終了通知={self.has_end}"
        )
