from dataclasses import dataclass
from typing import TYPE_CHECKING
from notiontaskr import config
from notiontaskr.util.validator import is_emoji_matches


if TYPE_CHECKING:
    from notiontaskr.domain.name_labels.label_registerable import LabelRegisterable
from notiontaskr.domain.value_objects.man_hours import ManHours
from notiontaskr.util.converter import truncate_decimal
from notiontaskr.domain.name_labels.name_label import NameLabel


@dataclass
class ManHoursLabel(NameLabel):
    """工数のラベルクラス"""

    @classmethod
    def from_man_hours(
        cls, scheduled_man_hours: ManHours, executed_man_hours: ManHours
    ) -> "ManHoursLabel":
        """工数タグを生成する"""

        return cls(
            key=config.MAN_HOURS_EMOJI,
            value=f"{truncate_decimal(executed_man_hours.value)}/{truncate_decimal(scheduled_man_hours.value)}",
        )

    @classmethod
    def parse_and_register(cls, key: str, value: str, delegate: "LabelRegisterable"):
        """ラベルを解析して登録する"""
        if not is_emoji_matches(key, config.MAN_HOURS_EMOJI):
            raise ValueError(f"Unknown key: {key}")

        delegate.register_man_hours_label(
            cls(
                key=key,
                value=str(value),
            )
        )

    def __eq__(self, other):
        if not isinstance(other, ManHoursLabel):
            return False
        return self.value == other.value
