from dataclasses import dataclass

from domain.excuted_task import ExcutedTask
from domain.name_labels.id_label import IdLabel
from domain.task import Task
from domain.task_name import TaskName

@dataclass
class ScheduledTask(Task):
    '''予定タスクモデル'''
    id: str
    id_prefix: str
    id_number: str
    scheduled_man_days: float
    excuted_man_days: float
    excuted_tasks: list[ExcutedTask] = None  # 紐づいている実績タスク

    @classmethod
    def from_response_data(cls, data: dict):
        '''レスポンスデータからインスタンスを生成する'''
        id_prefix = data['properties']['ID']['unique_id']['prefix']
        id_number = data['properties']['ID']['unique_id']['number']
        task_name = TaskName.from_raw_task_name(data['properties']['名前']['title'][0]['plain_text'])
        
        instance = cls(
            page_id=data['id'],
            name=task_name,
            tags=map(lambda tag: tag['name'], data['properties']['タグ']['multi_select']),
            id=id_number,
            id_prefix=id_prefix,
            id_number=id_number,
            scheduled_man_days=data['properties']['人日(予)']['number'],
            excuted_man_days=data['properties']['人日(実)']['number'],
        )

        # IDラベルを登録
        if not instance.name.id_label:
            instance.update_id_label(IdLabel.from_id(id_prefix, id_number))

        return instance
    
    def update_excuted_man_days(self, excuted_man_days: float):
        '''実績工数を更新するメソッド'''
        self.is_updated = True
        self.excuted_man_days = excuted_man_days
