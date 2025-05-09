from dataclasses import dataclass
from typing import TYPE_CHECKING
import config
import emoji
from util.validator import is_emoji_matches


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
        if not is_emoji_matches(key, config.MAN_HOURS_EMOJI):
            raise ValueError(f'Unknown key: {key}')
        
        delegate.register_man_hours_label(cls(
            key=key,
            value=str(value),
        ))

    def __eq__(self, other):
        if not isinstance(other, ManHoursLabel):
            return False
        return self.value == other.value
    
# 動作確認用
if __name__ == '__main__':
    value1=emoji.demojize('⏱')
    value2=emoji.demojize(config.MAN_HOURS_EMOJI)
    print(value1 == value2)