from dataclasses import dataclass

from domain.task import Task

@dataclass
class BudgetTask(Task):
    '''予定タスクモデル'''
    id: str
    budget_man_hour: float
    actual_man_hour: float

    @classmethod
    def from_response_data(cls, data):
        '''レスポンスデータからインスタンスを生成する'''
        id_prefix = data['properties']['ID']['unique_id']['prefix']
        id_number = data['properties']['ID']['unique_id']['number']
        return cls(
            page_id=data['id'],
            name=data['properties']['名前']['title'][0]['plain_text'],
            tag=data['properties']['タグ']['multi_select'],
            id=f'{id_prefix}-{id_number}',
            budget_man_hour=data['properties']['人日(予)']['number'],
            actual_man_hour=data['properties']['人日(実)']['number'],
        )