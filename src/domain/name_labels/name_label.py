from abc import ABC, abstractmethod
from dataclasses import dataclass
import re
from typing import List
from typing import TYPE_CHECKING

from domain.name_labels.label_registable import LabelRegistable

if TYPE_CHECKING:
    from domain.name_labels.man_days_label import ManDaysLabel



@dataclass
class NameLabel(ABC):

    '''タスク名のラベルクラス'''
    key: str
    value: str

    def get_display_str(self) -> str:
        '''表示用の文字列を返す'''
        return f'[{self.key}{self.value}]'

    @classmethod
    @abstractmethod
    def parse_and_register(cls, key: str, value: str, delegate: 'LabelRegistable'):
        '''ラベルを解析してdelegeteのメンバへ登録する'''
        pass
    

    @staticmethod
    def parse_labels(str: str, delegate: 'LabelRegistable'):
        from domain.name_labels.id_label import IdLabel
        
        '''ラベルを解析してdelegeteのメンバへ登録する
        
        chain of responsibleパターンで検索する
        '''
        # 正規表現で[絵文字]を含まない場合、IDラベルとする
        pattern = r'([^\U0001F300-\U0001FAD6]+)'
        if re.match(pattern, str):
            # IDラベルを登録
            delegate.register_id_label(IdLabel.from_id("", str))
        else:
            # 正規表現で[絵文字value]形式で取得
            # match[0]が絵文字、match[1]がvalue
            pattern = r'([\U0001F300-\U0001FAD6])([^\U0001F300-\U0001FAD6]+)'
            match = re.search(pattern, str)
            if not match:
                raise ValueError('No match found')
            match = match.groups()
            # 検索対象のクラスを配列に格納
            handlers: List['NameLabel'] = [
                ManDaysLabel,
            ]
        
            # ID以外のラベルを登録
            for handler in handlers:
                try:
                    handler.parse_and_register(match[0], match[1], delegate)
                except ValueError:
                    continue

