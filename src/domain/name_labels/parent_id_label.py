from dataclasses import dataclass

from domain.name_labels.label_registable import LabelRegistable
from domain.name_labels.name_label import NameLabel
from domain.value_objects.notion_id import NotionId

@dataclass
class ParentIdLabel(NameLabel):
    
    @classmethod
    def from_property(cls, parent_id: NotionId) -> 'ParentIdLabel':
        '''親IDラベルを生成する'''

        return cls(
            key="親",
            value=str(parent_id.number),
        )

    @classmethod
    def parse_and_register(cls, key: str, value: str, delegate: 'LabelRegistable') -> 'ParentIdLabel':
        '''ラベルを解析して登録する'''
        if not key == "親":
            raise ValueError(f'Unknown key: {key}')

        delegate.register_parent_id_label(cls(
            key=key,
            value=str(value),
        ))

    def __eq__(self, other):
        if not isinstance(other, ParentIdLabel):
            return NotImplemented
        return self.value == other.value
    