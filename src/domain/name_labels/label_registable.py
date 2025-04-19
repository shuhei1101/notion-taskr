from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from domain.name_labels.id_label import IdLabel
    from domain.name_labels.man_days_label import ManDaysLabel

class LabelRegistable(ABC):
    '''ラベルを登録するクラスのインターフェース'''

    @abstractmethod
    def register_id_label(self, label: 'IdLabel'):
        '''IDラベルを登録するメソッド'''
        pass

    @abstractmethod
    def register_man_days_label(self, label: 'ManDaysLabel'):
        '''工数ラベルを登録するメソッド'''
        pass