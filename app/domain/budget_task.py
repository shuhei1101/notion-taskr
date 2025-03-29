from dataclasses import dataclass

from app.domain.task import Task
from app.domain.task_name import TaskName

@dataclass
class BudgetTask(Task):
    '''予定タスクモデル'''
    id: str
    id_prefix: str
    id_number: str
    budget_man_days: float
    actual_man_days: float

    @classmethod
    def from_response_data(cls, data):
        '''レスポンスデータからインスタンスを生成する'''
        id_prefix = data['properties']['ID']['unique_id']['prefix']
        id_number = data['properties']['ID']['unique_id']['number']
        return cls(
            page_id=data['id'],
            name=TaskName.from_raw_task_name(data['properties']['名前']['title'][0]['plain_text']),
            tags=map(lambda tag: tag['name'], data['properties']['タグ']['multi_select']),
            id=f'{id_prefix}-{id_number}',
            id_prefix=id_prefix,
            id_number=id_number,
            budget_man_days=data['properties']['人日(予)']['number'],
            actual_man_days=data['properties']['人日(実)']['number'],
        )