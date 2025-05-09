from dataclasses import dataclass

from domain.executed_task import ExecutedTask
from domain.name_labels.id_label import IdLabel
from domain.name_labels.man_hours_label import ManHoursLabel
from domain.name_labels.parent_id_label import ParentIdLabel
from domain.task import Task
from domain.task_name import TaskName
from domain.value_objects.man_hours import ManHours
from domain.value_objects.notion_id import NotionId
from domain.value_objects.page_id import PageId
from domain.value_objects.status import Status

@dataclass
class ScheduledTask(Task):
    '''予定タスクモデル'''
    scheduled_man_hours: ManHours = None
    executed_man_hours: ManHours = None
    executed_tasks: list['ExecutedTask'] = None  # 紐づいている実績タスク
    child_task_page_ids: list['PageId'] = None  # サブアイテムのページID
    child_tasks: list['ScheduledTask'] = None  # サブアイテム

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

            status = Status(data['properties']['ステータス']['status']['name'])
            tags = []
            for tag in data['properties']['タグ']['multi_select']:
                tags.append(tag['name'])

            instance = cls(
                page_id=PageId(data['id']),
                name=task_name,
                tags=tags,
                id=notion_id,
                status=status,
                parent_task_page_id=PageId(
                    value=data['properties']['親アイテム']['relation'][0]['id'],
                ) if data['properties']['親アイテム']['relation'] else None,
                scheduled_man_hours=ManHours(data['properties']['人時(予)']['number']),
                executed_man_hours=ManHours(data['properties']['人時(実)']['number']),
                executed_tasks=[],
                child_task_page_ids=[PageId(relation['id']) for relation in data['properties']['サブアイテム']['relation']],
                child_tasks=[],
            )

            # IDラベルを更新
            instance.update_id_label(IdLabel.from_property(
                id=notion_id,
                status=status,
            ))

            return instance
        except KeyError as e:
            raise ValueError(f'In ScheduledTask[{task_number}] initialize error, {e}')
        except ValueError as e:
            raise ValueError(f'In ScheduledTask[{task_number}] initialize error, {e}')

    def update_executed_tasks(self, executed_tasks: list[ExecutedTask]):
        '''実績タスク配列を付与する'''
        self.executed_tasks = executed_tasks

    def update_executed_tasks_properties(self):
        '''実績タスクのプロパティを更新する
        
        :raise ValueError: 実績タスクが存在しない場合
        '''
        if self.executed_tasks is None:
            raise ValueError('実績タスクが存在しません。')
        
        for executed_task in self.executed_tasks:
            executed_task.update_name(self.name)
            executed_task.update_status(self.status)
            executed_task.update_parent_task_page_id(self.parent_task_page_id)

    def update_child_tasks(self, child_tasks: list['ScheduledTask']):
        '''サブアイテムを付与する'''
        self.child_tasks = child_tasks

    def update_child_tasks_properties(self):
        '''サブアイテムのプロパティを更新する'''
        # サブアイテムの親IDラベルを更新する
        for child_task in self.child_tasks:
            child_task.update_parent_id_label(ParentIdLabel.from_property(
                parent_id=self.id
            ))

    def aggregate_executed_man_hours(self):
        '''実績工数を集計し、ラベルを更新する'''
        if self.executed_tasks is None:
            self.executed_man_hours = self.update_executed_man_hours(ManHours(0))
        else:
            man_hours_total = 0

            for executed_task in self.executed_tasks:
                man_hours_total += executed_task.man_hours.value

            self.update_executed_man_hours(ManHours(man_hours_total))

        # 実績人時ラベルを更新する
        self.update_man_hours_label(ManHoursLabel.from_man_hours(
            executed_man_hours=self.executed_man_hours,
            scheduled_man_hours=self.scheduled_man_hours
        ))

    def update_executed_man_hours(self, executed_man_hours: ManHours):
        '''実績人日を更新する'''
        if self.executed_man_hours != executed_man_hours:
            self._toggle_is_updated(f'実績人日: {self.executed_man_hours} -> {executed_man_hours}')
            self.executed_man_hours = executed_man_hours


