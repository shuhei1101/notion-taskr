from dataclasses import dataclass

from domain.name_labels.label_registable import LabelRegistable
from domain.name_labels.name_label import NameLabel
from domain.value_objects.notion_id import NotionId
from domain.value_objects.status import Status
from util.validator import has_emoji

@dataclass
class IdLabel(NameLabel):
    
    @classmethod
    def from_property(cls, id: NotionId, status: Status) -> 'IdLabel':
        '''IDラベルを生成する'''
        key = ""
        if status == Status('完了'):
            key = "✓"

        return cls(
            key=key,
            value=str(id.number),
        )

    @classmethod
    def parse_and_register(cls, key: str, value: str, delegate: 'LabelRegistable') -> 'IdLabel':
        '''ラベルを解析して登録する
        
        if文の順番に注意。"✓"は絵文字に含まれないため、最初に判定する。
        '''
        label = key + value  # 文字列を結合する

        if label[0] == "✓":
            key = label[0]
            value = label[1:]

        elif not has_emoji(label):
            key = ""
            value = label

        else:
            raise ValueError(f'Unknown key: {key}')
        
        delegate.register_id_label(cls(
            key=key,
            value=str(value),
        ))
