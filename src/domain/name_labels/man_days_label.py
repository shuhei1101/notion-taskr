from dataclasses import dataclass
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from domain.name_labels.label_registable import LabelRegistable
from domain.value_objects.man_days import ManDays
import emoji
from util.converter import truncate_decimal
from domain.name_labels.name_label import NameLabel

@dataclass
class ManDaysLabel(NameLabel):
    '''工数のラベルクラス'''

    @classmethod
    def from_man_days(cls, scheduled_man_days: ManDays, executed_man_days: ManDays) -> str:
        '''工数タグを生成する'''

        return cls(
            key=emoji.emojize(':hourglass_done:'),
            value=f'{truncate_decimal(executed_man_days.value)}/{truncate_decimal(scheduled_man_days.value)}',
        )
    
    @classmethod
    def parse_and_register(cls, key: str, value: str, delegate: 'LabelRegistable'):
        '''ラベルを解析して登録する'''
        if key == emoji.emojize(':hourglass_done:'):
            delegate.register_man_days_label(cls(
                key=key,
                value=str(value),
            ))

        else:
            raise ValueError(f'Unknown key: {key}')
