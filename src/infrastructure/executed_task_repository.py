from typing import Callable, List
from notion_client import Client

from domain.executed_task import ExecutedTask
from infrastructure.operator import CheckboxOperator
from infrastructure.task_search_condition import TaskSearchConditions
from infrastructure.task_update_properties import TaskUpdateProperties


class ExecutedTaskRepository:
    def __init__(self, token, db_id):
        self.client = Client(
            auth=token,
        )
        self.db_id = db_id
        self.filter = TaskSearchConditions()

    def find_all(self,
                 on_error: Callable[[Exception, dict[str]], None]
                 ) -> List[ExecutedTask]:
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
        executed_tasks = []
        for data in response_data['results']:
            try:
                executed_tasks.append(ExecutedTask.from_response_data(data))
            except Exception as e:
                on_error(e, data)
        return executed_tasks

    def find_by_condition(self, condition: TaskSearchConditions,
                          on_error: Callable[[Exception, dict[str]], None]
                          ) -> List[ExecutedTask]:
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
        executed_tasks = []
        for data in response_data['results']:
            try:
                executed_tasks.append(ExecutedTask.from_response_data(data))
            except Exception as e:
                on_error(e, data)

        return executed_tasks
    
    def update(self, executed_task: ExecutedTask):
        '''実績タスクを更新する'''

        properties = TaskUpdateProperties() \
            .set_name(executed_task.get_display_name()) \
            .build()
        
        self.client.pages.update(
            **{
                'page_id': executed_task.page_id.value,
                'properties': properties
            }
        )





