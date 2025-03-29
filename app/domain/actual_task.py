from datetime import datetime
import re
from dataclasses import dataclass

from domain.task import Task
from domain.task_name import TaskName
from util.calculator import get_hours_diff
from util.converter import man_hour_to_man_days

@dataclass
class ActualTask(Task):
    '''実績タスクモデル'''
    start_date: datetime
    end_date: datetime
    man_days: float
    budget_task_id: str  # 紐づいている予定タスクのID

    @classmethod
    def from_response_data(cls, data):
        '''レスポンスデータからインスタンスを生成する'''

        name=data['properties']['名前']['title'][0]['plain_text']
        id_prefix = data['properties']['ID']['unique_id']['prefix']
        budget_task_id_number = cls._extract_task_number(name, id_prefix)
        start_date_str = data['properties']['日付']['date']['start']
        end_date_str = data['properties']['日付']['date']['end']
        start_date = datetime.fromisoformat(start_date_str)
        end_date = datetime.fromisoformat(end_date_str)

        return cls(
            page_id=data['id'],
            name=TaskName.from_raw_task_name(name),
            tags=map(lambda tag: tag['name'], data['properties']['タグ']['multi_select']),
            start_date=start_date,
            end_date=end_date,
            man_days=man_hour_to_man_days(get_hours_diff(start_date, end_date)),
            budget_task_id=f'{id_prefix}-{budget_task_id_number}'
        )
    
    @staticmethod
    def _extract_task_number(task_name, id_prefix):
        '''タスク名からタスク番号を抽出する

        IDは[]で囲まれ、SN-999のような形式である必要がある
        ただし、SNの部分はid_tagで指定されたものである
        例: [SN-999]タスク名
        '''
        match = re.match(rf".*\[{id_prefix}-(\d+)\].*", task_name)
        if match:
            return match.group(1)  # グループ1にマッチした文字列を返す
        else:
            return None

if __name__ == '__main__':
    # task = ActualTask(
    #     name='[999]タスク名',
    #     tag=[],
    #     start_date=datetime.now(),
    #     end_date=datetime.now,
    #     man_hour=1.0
    # )
    # print(task)
    # print(task.get_name_id())
    str = '[999]タスク名'
    print(str.split(']'))