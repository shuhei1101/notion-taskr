from datetime import datetime
from dataclasses import dataclass

from domain.task import Task
from domain.task_name import TaskName
from util.calculator import get_hours_diff
from util.converter import man_hour_to_man_days

@dataclass
class ExcutedTask(Task):
    '''実績タスクモデル'''
    start_date: datetime
    end_date: datetime
    man_days: float
    scheduled_task_id: str  # 紐づいている予定タスクのID

    @classmethod
    def from_response_data(cls, data):
        '''レスポンスデータからインスタンスを生成する'''

        name=data['properties']['名前']['title'][0]['plain_text']
        task_name = TaskName.from_raw_task_name(name)

        start_date_str = data['properties']['日付']['date']['start']
        end_date_str = data['properties']['日付']['date']['end']
        start_date = datetime.fromisoformat(start_date_str)
        end_date = datetime.fromisoformat(end_date_str)

        return cls(
            page_id=data['id'],
            name=task_name,
            tags=map(lambda tag: tag['name'], data['properties']['タグ']['multi_select']),
            start_date=start_date,
            end_date=end_date,
            man_days=man_hour_to_man_days(get_hours_diff(start_date, end_date)),
            scheduled_task_id=task_name.id_label.value if task_name.id_label else None,
        )
        
    def update_scheduled_task_id(self, scheduled_task_id: str):
        '''予定タスクIDを更新するメソッド'''
        self.is_updated = True
        self.scheduled_task_id = scheduled_task_id
