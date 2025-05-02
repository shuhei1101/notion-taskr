from dataclasses import dataclass

from domain.task import Task
from domain.task_name import TaskName
from domain.value_objects.man_hours import ManHours
from domain.value_objects.notion_date import NotionDate
from domain.value_objects.notion_id import NotionId
from domain.value_objects.page_id import PageId
from domain.value_objects.status import Status
from domain.value_objects.tag import Tag

@dataclass
class ExecutedTask(Task):
    '''実績タスクモデル'''
    date: NotionDate = None
    man_hours: ManHours = None
    scheduled_task_id: NotionId = None  # 紐づいている予定タスクのID

    @classmethod
    def from_response_data(cls, data):
        '''レスポンスデータからインスタンスを生成する
        
        :raise KeyError: 
        :raise ValueError: レスポンスデータに必要なキーが存在しない場合
        '''
        try:
            task_number = data['properties']['ID']['unique_id']['number']
            task_name = TaskName.from_raw_task_name(
                data['properties']['名前']['title'][0]['plain_text']
            )
            
            start_date_str = data['properties']['日付']['date']['start']
            end_date_str = data['properties']['日付']['date']['end']
            notion_date = NotionDate.from_raw_date(
                start=start_date_str,
                end=end_date_str,
            )

            return cls(
                page_id=PageId(data['id']),
                name=task_name,
                tags=map(lambda tag: Tag(tag['name']), data['properties']['タグ']['multi_select']),
                id=NotionId(
                    prefix=data['properties']['ID']['unique_id']['prefix'],
                    number=task_number,
                ),
                status=Status(data['properties']['ステータス']['status']['name']),
                date=notion_date,
                man_hours=ManHours.from_notion_date(notion_date),
                scheduled_task_id=NotionId(
                    prefix="",
                    number=task_name.id_label.value,
                ) if task_name.id_label else None,
            )
        except KeyError as e:
            raise ValueError(f'In ExecutedTask[{task_number}] initialize error, {e}')
        except ValueError as e:
            raise ValueError(f'In ExecutedTask[{task_number}] initialize error, {e}')
        
    def update_scheduled_task_id(self, scheduled_task_id: NotionId):
        '''予定タスクIDを更新するメソッド'''
        if self.scheduled_task_id != scheduled_task_id:
            self.is_updated = True
            self.scheduled_task_id = scheduled_task_id

