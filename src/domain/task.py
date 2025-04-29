from dataclasses import dataclass
from typing import TYPE_CHECKING, List

from domain.task_name import TaskName
from domain.value_objects.notion_id import NotionId
from domain.value_objects.page_id import PageId
from domain.value_objects.status import Status
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
    status: Status = None

    def __init__(self, page_id: PageId, name: TaskName, tags: List[Tag], id: NotionId = None, status: Status = None):
        self.page_id = page_id
        self.name = name
        self.tags = tags
        self.id = id
        self.status = status
    
    def update_man_days_label(self, man_days_label: 'ManDaysLabel'):
        '''工数ラベルを登録し、is_updatedをTrueにする'''
        if self.name.man_days_label != man_days_label:
            self.is_updated = True
            self.name.man_days_label = man_days_label

    def update_id_label(self, label: 'IdLabel'):
        '''IDラベルを登録し、is_updatedをTrueにする'''
        if self.name.id_label != label:
            self.is_updated = True
            self.name.id_label = label   

    def update_status(self, status: Status):
        '''ステータスを更新し、is_updatedをTrueにする'''
        if self.status != status:
            self.is_updated = True
            self.status = status

    def update_name(self, name: TaskName):
        '''タスク名を更新し、is_updatedをTrueにする'''
        if self.name != name:
            self.is_updated = True
            self.name = name
        
    def get_display_name(self) -> str:
        '''表示用のタスク名を取得する

        :return: 表示用のタスク名
        '''
        return str(self.name)
    