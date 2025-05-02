from dataclasses import dataclass
from typing import TYPE_CHECKING
import config


if TYPE_CHECKING:
    from domain.name_labels.label_registable import LabelRegistable
from domain.value_objects.man_hours import ManHours
from util.converter import truncate_decimal
from domain.name_labels.name_label import NameLabel


@dataclass
class ManHoursLabel(NameLabel):
    '''工数のラベルクラス'''

    @classmethod
    def from_man_hours(cls, scheduled_man_hours: ManHours, executed_man_hours: ManHours) -> str:
        '''工数タグを生成する'''

        return cls(
            key=config.MAN_HOURS_EMOJI,
            value=f'{truncate_decimal(executed_man_hours.value)}/{truncate_decimal(scheduled_man_hours.value)}',
        )
    
    @classmethod
    def parse_and_register(cls, key: str, value: str, delegate: 'LabelRegistable'):
        '''ラベルを解析して登録する'''
        if key == config.MAN_HOURS_EMOJI:
            delegate.register_man_hours_label(cls(
                key=key,
                value=str(value),
            ))

        else:
            raise ValueError(f'Unknown key: {key}')

    def __eq__(self, other):
        if not isinstance(other, ManHoursLabel):
            return NotImplemented
        if self.value == other.value:
            return True
        return False