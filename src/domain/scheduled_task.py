from dataclasses import dataclass

from domain.executed_task import ExecutedTask
from domain.name_labels.id_label import IdLabel
from domain.name_labels.man_days_label import ManDaysLabel
from domain.task import Task
from domain.task_name import TaskName
from domain.value_objects.man_days import ManDays
from domain.value_objects.notion_id import NotionId
from domain.value_objects.page_id import PageId

@dataclass
class ScheduledTask(Task):
    '''予定タスクモデル'''
    scheduled_man_days: ManDays = None
    executed_man_days: ManDays = None
    executed_tasks: list[ExecutedTask] = None  # 紐づいている実績タスク

    @classmethod
    def from_response_data(cls, data: dict):
        '''レスポンスデータからインスタンスを生成する
        
        :raise KeyError: 
        :raise ValueError: レスポンスデータに必要なキーが存在しない場合
        '''

        try:
            task_number = data['properties']['ID']['unique_id']['number']
            task_name = TaskName.from_raw_task_name(data['properties']['名前']['title'][0]['plain_text'])
            notion_id = NotionId(
                prefix=data['properties']['ID']['unique_id']['prefix'],
                number=task_number,
            )
            
            instance = cls(
                page_id=PageId(data['id']),
                name=task_name,
                tags=map(lambda tag: tag['name'], data['properties']['タグ']['multi_select']),
                id=notion_id,
                scheduled_man_days=ManDays(data['properties']['人日(予)']['number']),
                executed_man_days=ManDays(data['properties']['人日(実)']['number']),
            )

            # IDラベルを登録
            if not instance.name.id_label:
                instance.update_id_label(IdLabel.from_id(notion_id))

            return instance
        except KeyError as e:
            raise ValueError(f'In ScheduledTask[{task_number}] initialize error, {e}')
        except ValueError as e:
            raise ValueError(f'In ScheduledTask[{task_number}] initialize error, {e}')

    def update_executed_tasks(self, executed_tasks: list[ExecutedTask]):
        '''実績タスク配列を付与する'''
        self.executed_tasks = executed_tasks

        # 実績工数を集計する
        self._aggregate_executed_man_days()

        # 実績工数ラベルを更新する
        self.update_man_days_label(ManDaysLabel.from_man_days(
            executed_man_days=self.executed_man_days,
            scheduled_man_days=self.scheduled_man_days
        ))

    def update_executed_task_name(self):
        '''実績タスクのTaskNameを自身と紐づける
        
        :raise ValueError: 実績タスクが存在しない場合
        '''
        if self.executed_tasks is None:
            raise ValueError('実績タスクが存在しません')
        for executed_task in self.executed_tasks:
            executed_task.name = self.name

    def _aggregate_executed_man_days(self):
        '''実績工数を集計する'''
        self.executed_man_days = ManDays(sum(map(
                lambda executed_task: executed_task.man_days.value,
                self.executed_tasks
            )))
