from typing import List
from notion_client import Client

from domain.scheduled_task import ScheduledTask
from infrastructure.operator import CheckboxOperator
from infrastructure.task_search_condition import TaskSearchConditions
from infrastructure.task_update_properties import TaskUpdateProperties

class ScheduledTaskRepository:
    def __init__(self, token, db_id):
        self.client = Client(
            auth=token,
        )
        self.db_id = db_id
        self.filter = TaskSearchConditions()

    def find_all(self) -> List[ScheduledTask]:
        '''全ての予定を取得する'''
        filter = TaskSearchConditions().and_(
            TaskSearchConditions().where_scheduled_flag(
                operator=CheckboxOperator.EQUALS,
                is_scheduled=True
            ),
        ).build()
        
        response_data = self.client.databases.query(
            **{
                'database_id': self.db_id,
                'filter': filter
            }
        )

        # response_dataをScheduledTaskのリストに変換する
        scheduled_tasks = []
        for data in response_data['results']:
            try:
                scheduled_tasks.append(ScheduledTask.from_response_data(data))
            except Exception as e:
                # 名前が空のときにもスキップされる
                print(f"スキップ: {e}")
        return scheduled_tasks

    def find_by_condition(self, condition: TaskSearchConditions) -> List[ScheduledTask]:
        '''タスクDBの指定タグの予定を全て取得する'''

        filter = TaskSearchConditions().and_(
            TaskSearchConditions().where_scheduled_flag(
                operator=CheckboxOperator.EQUALS,
                is_scheduled=True
            ),
            condition
        ).build()
        
        response_data = self.client.databases.query(
            **{
                'database_id': self.db_id,
                'filter': filter
            }
        )

        # response_dataをScheduledTaskのリストに変換する
        scheduled_tasks = []
        for data in response_data['results']:
            try:
                scheduled_tasks.append(ScheduledTask.from_response_data(data))
            except Exception as e:
                # 名前が空のときにもスキップされる
                print(f"スキップ: {e}")

        return scheduled_tasks

    def update(self, scheduled_task: ScheduledTask):
        '''予定タスクを更新する'''

        properties = TaskUpdateProperties() \
            .set_name(scheduled_task.name.get_display_str()) \
            .set_excuted_man_days(scheduled_task.excuted_man_days) \
            .build()

        self.client.pages.update(
            **{
                'page_id': scheduled_task.page_id,
                'properties': properties
            }
        )