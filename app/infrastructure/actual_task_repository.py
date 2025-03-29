from typing import List
from notion_client import Client

from app.domain.actual_task import ActualTask
from app.infrastructure.operator import CheckboxOperator
from app.infrastructure.task_search_condition import TaskSearchConditions
from app.infrastructure.task_update_properties import TaskUpdateProperties


class ActualTaskRepository:
    def __init__(self, token, db_id):
        self.client = Client(
            auth=token,
        )
        self.db_id = db_id
        self.filter = TaskSearchConditions()

    def find_all(self) -> List[ActualTask]:
        '''全ての実績を取得する'''
        filter = TaskSearchConditions().and_(
            TaskSearchConditions().where_budget_flag(
                operator=CheckboxOperator.EQUALS, 
                is_budget=False
            ),
        ).build()
        
        response_data = self.client.databases.query(
            **{
                'database_id': self.db_id,
                'filter': filter
            }
        )

        # response_dataをBudgetTaskのリストに変換する
        actual_tasks = []
        for data in response_data['results']:
            try:
                actual_tasks.append(ActualTask.from_response_data(data))
            except Exception as e:
                print(f"スキップ: {e}")
        return actual_tasks

    def find_by_condition(self, condition: TaskSearchConditions) -> List[ActualTask]:
        '''指定した実績を全て取得する'''

        filter = TaskSearchConditions().and_(
            TaskSearchConditions().where_budget_flag(
                operator=CheckboxOperator.EQUALS, 
                is_budget=False
            ),
            condition,
        ).build()

        response_data = self.client.databases.query(
            **{
                'database_id': self.db_id,
                'filter': filter
            }
        )

        # response_dataをBudgetTaskのリストに変換する
        actual_tasks = []
        for data in response_data['results']:
            try:
                actual_tasks.append(ActualTask.from_response_data(data))
            except Exception as e:
                print(f"スキップ: {e}")

        return actual_tasks
    
    def update(self, actual_task: ActualTask):
        '''実績タスクを更新する'''

        properties = TaskUpdateProperties() \
            .set_name(actual_task.name.get_display_str()) \
            .build()
        
        self.client.pages.update(
            **{
                'page_id': actual_task.page_id,
                'properties': properties
            }
        )





