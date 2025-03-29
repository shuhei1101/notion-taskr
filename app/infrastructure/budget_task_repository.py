from typing import List
from notion_client import Client

from app.domain.budget_task import BudgetTask
from app.infrastructure.operator import CheckboxOperator
from app.infrastructure.task_search_condition import TaskSearchConditions
from app.infrastructure.task_update_properties import TaskUpdateProperties

class BudgetTaskRepository:
    def __init__(self, token, db_id):
        self.client = Client(
            auth=token,
        )
        self.db_id = db_id
        self.filter = TaskSearchConditions()

    def find_all(self) -> List[BudgetTask]:
        '''全ての予定を取得する'''
        filter = TaskSearchConditions().and_(
            TaskSearchConditions().where_budget_flag(
                operator=CheckboxOperator.EQUALS,
                is_budget=True
            ),
        ).build()
        
        response_data = self.client.databases.query(
            **{
                'database_id': self.db_id,
                'filter': filter
            }
        )

        # response_dataをBudgetTaskのリストに変換する
        budget_tasks = []
        for data in response_data['results']:
            try:
                budget_tasks.append(BudgetTask.from_response_data(data))
            except Exception as e:
                # 名前が空のときにもスキップされる
                print(f"スキップ: {e}")
        return budget_tasks

    def find_by_condition(self, condition: TaskSearchConditions) -> List[BudgetTask]:
        '''タスクDBの指定タグの予定を全て取得する'''

        filter = TaskSearchConditions().and_(
            TaskSearchConditions().where_budget_flag(
                operator=CheckboxOperator.EQUALS,
                is_budget=True
            ),
            condition
        ).build()
        
        response_data = self.client.databases.query(
            **{
                'database_id': self.db_id,
                'filter': filter
            }
        )

        # response_dataをBudgetTaskのリストに変換する
        budget_tasks = []
        for data in response_data['results']:
            try:
                budget_tasks.append(BudgetTask.from_response_data(data))
            except Exception as e:
                # 名前が空のときにもスキップされる
                print(f"スキップ: {e}")

        return budget_tasks

    def update(self, budget_task: BudgetTask):
        '''予定タスクを更新する'''

        properties = TaskUpdateProperties() \
            .set_name(budget_task.name.get_display_str()) \
            .set_actual_man_days(budget_task.actual_man_days) \
            .build()

        self.client.pages.update(
            **{
                'page_id': budget_task.page_id,
                'properties': properties
            }
        )