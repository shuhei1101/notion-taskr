from abc import ABC, abstractmethod
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from domain.name_labels.id_label import IdLabel
    from domain.name_labels.man_hours_label import ManHoursLabel

class LabelRegistable(ABC):
    '''ラベルを登録するクラスのインターフェース'''

    @abstractmethod
    def register_id_label(self, label: 'IdLabel'):
        '''IDラベルを登録するメソッド'''
        pass

    @abstractmethod
    def register_man_hours_label(self, label: 'ManHoursLabel'):
        '''人時ラベルを登録するメソッド'''
        pass

    @abstractmethod
    def register_parent_id_label(self, label: 'IdLabel'):
        '''親IDラベルを登録するメソッド'''
        pass