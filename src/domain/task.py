from dataclasses import dataclass
from typing import TYPE_CHECKING, List

from domain.task_name import TaskName
from domain.value_objects.notion_id import NotionId
from domain.value_objects.page_id import PageId
from domain.value_objects.tag import Tag

if TYPE_CHECKING:
    from domain.name_labels.id_label import IdLabel
    from domain.name_labels.man_days_label import ManDaysLabel

@dataclass
class Task:
    '''タスクモデル'''
    page_id: PageId
    name: TaskName
    tags: List[Tag]
    is_updated: bool = False
    id: NotionId = None
    
    def update_man_days_label(self, man_days_label: 'ManDaysLabel'):
        '''工数ラベルを登録するメソッド'''
        if self.name.man_days_label is None:
            self.is_updated = True
            self.name.man_days_label = man_days_label
        else:
            # 既に登録されている場合は、値を確認し、更新する
            if self.name.man_days_label.value != man_days_label.value:
                self.is_updated = True
                self.name.man_days_label = man_days_label

    def update_id_label(self, label: 'IdLabel'):
        '''IDラベルを登録するメソッド

        :param IdLabel label: IDラベル
        '''
        if self.name.id_label is None:
            self.is_updated = True
            self.name.id_label = label
        else:
            # 既に登録されている場合は、値を確認し、更新する
            if self.name.id_label.value != label.value:
                self.is_updated = True
                self.name.id_label = label    
        
    def get_display_name(self) -> str:
        '''表示用のタスク名を取得するメソッド

        :return: 表示用のタスク名
        '''
        return str(self.name)
    