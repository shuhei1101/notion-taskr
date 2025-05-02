from dataclasses import dataclass

import config
from domain.name_labels.label_registable import LabelRegistable
from domain.name_labels.name_label import NameLabel
from domain.value_objects.notion_id import NotionId
from domain.value_objects.status import Status

@dataclass
class ParentIdLabel(NameLabel):
    
    @classmethod
    def from_property(cls, parent_id: NotionId, parent_status: Status) -> 'ParentIdLabel':
        '''親IDラベルを生成する'''

        return cls(
            key=config.PARENT_ID_EMOJI,
            value=str(parent_id.number),
        )

    @classmethod
    def parse_and_register(cls, key: str, value: str, delegate: 'LabelRegistable') -> 'ParentIdLabel':
        '''ラベルを解析して登録する'''
        if key == config.PARENT_ID_EMOJI:
            delegate.register_parent_id_label(cls(
                key=key,
                value=str(value),
            ))

        else:
            raise ValueError(f'Unknown key: {key}')

    def __eq__(self, other):
        if not isinstance(other, ParentIdLabel):
            return NotImplemented
        if self.value == other.value:
            return True
        return False