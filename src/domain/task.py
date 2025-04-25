from dataclasses import dataclass
from typing import TYPE_CHECKING, List

from domain.task_name import TaskName

if TYPE_CHECKING:
    from domain.name_labels.id_label import IdLabel
    from domain.name_labels.man_days_label import ManDaysLabel

@dataclass
class Task:
    '''タスクモデル'''
    page_id: str
    name: TaskName
    tags: List[str]
    is_updated: bool = False
    
    def update_man_days_label(self, man_days_label: 'ManDaysLabel'):
        '''工数ラベルを登録するメソッド'''

        self.is_updated = True
        self.name.man_days_label = man_days_label

    def update_id_label(self, label: 'IdLabel'):
        '''IDラベルを登録するメソッド

        :param IdLabel label: IDラベル
        '''
        self.is_updated = True
        self.name.id_label = label    
        
    def get_display_name(self) -> str:
        '''表示用のタスク名を取得するメソッド

        :return: 表示用のタスク名
        '''
        return str(self.name)
    