from abc import ABC, abstractmethod
from dataclasses import dataclass

from typing import List

from domain.name_labels.label_registable import LabelRegistable
from domain.name_labels.parent_id_label import ParentIdLabel
from util.converter import remove_variant_selectors

@dataclass
class NameLabel(ABC):
    '''タスク名のラベルクラス'''
    key: str
    value: str

    def __eq__(self, other: 'NameLabel'):
        if not isinstance(other, NameLabel):
            return False
        return self.key == other.key and self.value == other.value

    def get_display_str(self) -> str:
        '''表示用の文字列を返す'''
        return f'[{self.key}{self.value}]'

    @classmethod
    @abstractmethod
    def parse_and_register(cls, key: str, value: str, delegate: 'LabelRegistable'):
        '''ラベルを解析してdelegeteのメンバへ登録する'''
        pass

    @staticmethod
    def parse_labels(label: str, delegate: 'LabelRegistable'):
        '''ラベルを解析してdelegeteのメンバへ登録する
        
        chain of responsibleパターンで検索する
        '''
        from domain.name_labels.id_label import IdLabel
        from domain.name_labels.man_hours_label import ManHoursLabel

        label = remove_variant_selectors(label)  # バリアントセレクタを除去

        key = label[0]  # 最初の文字をキーとする
        value = remove_variant_selectors(label[1:])  # 2文字目以降を値とする

        # 検索対象のクラスを配列に格納
        handlers: List['NameLabel'] = [
            IdLabel,
            ManHoursLabel,
            ManHoursLabel,
            ParentIdLabel,
        ]
    
        # ID以外のラベルを登録
        for handler in handlers:
            try:
                handler.parse_and_register(key, value, delegate)
                return
            except ValueError:
                continue


if __name__ == '__main__':
    import emoji
    print(emoji.emojize(':timer_clock:'))
    print(emoji.demojize('⏲️'))

