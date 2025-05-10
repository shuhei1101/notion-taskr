

from abc import ABC

from notiontaskr.domain.task import Task


class TaskUpdateProperties(ABC):
    '''タスクの更新用プロパティ辞書を生成するクラス'''

    def __init__(self, task: Task):
        self.task = task
        self.properties = {}

    def set_name(self):
        '''名前の更新'''
        self.properties['名前'] = {
            'title': [{'text': {'content': self.task.get_display_name()}}]
        }
        return self

    def set_executed_man_hours(self, executed_man_hour: float):
        '''実際の人日数の更新'''
        self.properties['人時(実)'] = {'number': executed_man_hour}
        return self
    
    def set_parent_task_page_id(self):
        '''親タスクIDの更新'''
        if self.task.parent_task_page_id:
            self.properties['親アイテム(予)'] = {
                'relation': [{'id': str(self.task.parent_task_page_id)}]
            }
        return self

    def set_status(self):
        '''ステータスの更新'''
        self.properties['ステータス'] = {'status': {'name': str(self.task.status)}}
        return self

    def set_scheduled_flag(self, scheduled_flag: bool):
        '''予定フラグの更新'''
        self.properties['予定フラグ'] = {'checkbox': {'equals': scheduled_flag}}
        return self

    def set_price(self, price: float):
        '''価格の更新'''
        self.properties['Price'] = {'number': price}
        return self

    def build(self):
        '''更新用の最終プロパティを返す'''
        return self.properties if self.properties else {}
