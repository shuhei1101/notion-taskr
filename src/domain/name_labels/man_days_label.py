from dataclasses import dataclass

from domain.name_labels.name_label import NameLabel

@dataclass
class ManDaysLabel(NameLabel):
    @classmethod
    def from_man_days(cls, budget_man_days: float, actual_man_days: float) -> str:
        '''工数タグを生成する'''
        return cls(
            key='⌛️',
            value=f'{actual_man_days:.1f}/{budget_man_days:.1f}',
        )
    
    @classmethod
    def parse_and_register(cls, key: str, value: str, delegate):
        '''ラベルを解析して登録する'''
        if key == '⌛️':
            instance = cls(
                key=key,
                value=value,
            )
            delegate.man_days_label = instance

        else:
            raise ValueError(f'Unknown key: {key}')