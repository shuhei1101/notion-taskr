from dataclasses import dataclass
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from domain.name_labels.label_registable import LabelRegistable
from util.converter import truncate_decimal
from domain.name_labels.name_label import NameLabel

@dataclass
class ManDaysLabel(NameLabel):
    '''工数のラベルクラス'''

    @classmethod
    def from_man_days(cls, budget_man_days: float, actual_man_days: float) -> str:
        '''工数タグを生成する'''

        return cls(
            key='⌛️',
            value=f'{truncate_decimal(actual_man_days)}/{truncate_decimal(budget_man_days)}',
        )
    
    @classmethod
    def parse_and_register(cls, key: str, value: str, delegate: 'LabelRegistable'):
        '''ラベルを解析して登録する'''
        if key == '⌛️':
            delegate.register_man_days_label(cls(
                key=key,
                value=value,
            ))

        else:
            raise ValueError(f'Unknown key: {key}')
