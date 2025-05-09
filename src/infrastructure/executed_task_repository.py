from typing import Callable, List
from infrastructure.executed_task_update_properties import ExecutedTaskUpdateProperties
from notion_client import Client

from domain.executed_task import ExecutedTask
from infrastructure.operator import CheckboxOperator
from infrastructure.task_search_condition import TaskSearchCondition

class ExecutedTaskRepository:
    def __init__(self, token, db_id):
        self.client = Client(
            auth=token,
        )
        self.db_id = db_id
        self.filter = TaskSearchCondition()

    async def find_all(self,
                 on_error: Callable[[Exception, dict[str]], None]
                 ) -> List[ExecutedTask]:
        '''全ての実績を取得する'''
        filter = TaskSearchCondition().and_(
            TaskSearchCondition().where_scheduled_flag(
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

    async def find_by_condition(self, condition: TaskSearchCondition,
                          on_error: Callable[[Exception, dict[str]], None]
                          ) -> List[ExecutedTask]:
        '''指定した実績を全て取得する'''

        filter = TaskSearchCondition().and_(
            TaskSearchCondition().where_scheduled_flag(
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
    
    async def update(self, executed_task: ExecutedTask,
               on_success: Callable[[ExecutedTask], None],
               on_error: Callable[[Exception, ExecutedTask], None]
               ) -> None:
        '''実績タスクを更新する'''

        try:
            properties = ExecutedTaskUpdateProperties(task=executed_task) \
                .set_name() \
                .set_status() \
                .build()
            
            self.client.pages.update(
                **{
                    'page_id': str(executed_task.page_id),
                    'properties': properties
                }
            )
            on_success(executed_task)
        except Exception as e:
            on_error(e, executed_task)
            return





