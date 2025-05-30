from dataclasses import dataclass

from notiontaskr.domain.name_labels.label_registerable import LabelRegisterable
from notiontaskr.domain.name_labels.name_label import NameLabel

from notiontaskr.notifier.task_remind_info import TaskRemindInfo

from notiontaskr import config

from notiontaskr.util.validator import is_emoji_matches

from notiontaskr.util.converter import timedelta_to_minutes


@dataclass
class RemindLabel(NameLabel):

    @classmethod
    def from_property(cls, remind_info: TaskRemindInfo) -> "RemindLabel":
        """親IDラベルを生成する"""

        parts = [
            (
                str(timedelta_to_minutes(remind_info.before_start_minutes)) + "m"
                if remind_info.has_before_start
                else ""
            ),
            (
                str(timedelta_to_minutes(remind_info.before_end_minutes)) + "m"
                if remind_info.has_before_end
                else ""
            ),
        ]
        value = "|".join(parts)

        return cls(
            key=config.REMIND_EMOJI,
            value=value,
        )

    @classmethod
    def parse_and_register(cls, key: str, value: str, delegate: "LabelRegisterable"):
        """ラベルを解析して登録する"""
        if not is_emoji_matches(key, config.REMIND_EMOJI):
            raise ValueError(f"Unknown key: {key}")

        delegate.register_remind_label(
            cls(
                key=key,
                value=str(value),
            )
        )

    def __eq__(self, other):
        if not isinstance(other, RemindLabel):
            return NotImplemented
        return self.value == other.value
