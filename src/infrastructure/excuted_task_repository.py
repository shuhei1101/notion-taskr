from typing import List
from notion_client import Client

from domain.excuted_task import ExcutedTask
from infrastructure.operator import CheckboxOperator
from infrastructure.task_search_condition import TaskSearchConditions
from infrastructure.task_update_properties import TaskUpdateProperties


class ExcutedTaskRepository:
    def __init__(self, token, db_id):
        self.client = Client(
            auth=token,
        )
        self.db_id = db_id
        self.filter = TaskSearchConditions()

    def find_all(self) -> List[ExcutedTask]:
        '''全ての実績を取得する'''
        filter = TaskSearchConditions().and_(
            TaskSearchConditions().where_scheduled_flag(
                operator=CheckboxOperator.EQUALS, 
                is_scheduled=False
            ),
        ).build()
        
        response_data = self.client.databases.query(
            **{
                'database_id': self.db_id,
                'filter': filter
            }
        )

        # response_dataをScheduledTaskのリストに変換する
        excuted_tasks = []
        for data in response_data['results']:
            try:
                excuted_tasks.append(ExcutedTask.from_response_data(data))
            except Exception as e:
                print(f"スキップ: {e}")
        return excuted_tasks

    def find_by_condition(self, condition: TaskSearchConditions) -> List[ExcutedTask]:
        '''指定した実績を全て取得する'''

        filter = TaskSearchConditions().and_(
            TaskSearchConditions().where_scheduled_flag(
                operator=CheckboxOperator.EQUALS, 
                is_scheduled=False
            ),
            condition,
        ).build()

        response_data = self.client.databases.query(
            **{
                'database_id': self.db_id,
                'filter': filter
            }
        )

        # response_dataをScheduledTaskのリストに変換する
        excuted_tasks = []
        for data in response_data['results']:
            try:
                excuted_tasks.append(ExcutedTask.from_response_data(data))
            except Exception as e:
                print(f"スキップ: {e}")

        return excuted_tasks
    
    def update(self, excuted_task: ExcutedTask):
        '''実績タスクを更新する'''

        properties = TaskUpdateProperties() \
            .set_name(excuted_task.name.get_display_str()) \
            .build()
        
        self.client.pages.update(
            **{
                'page_id': excuted_task.page_id,
                'properties': properties
            }
        )





