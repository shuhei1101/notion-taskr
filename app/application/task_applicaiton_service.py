from typing import List

import config
from domain.budget_task_service import BudgetTaskService
from domain.actual_task import ActualTask
from domain.budget_task import BudgetTask
from infrastructure.actual_task_repository import ActualTaskRepository
from infrastructure.budget_task_repository import BudgetTaskRepository
from util.converter import man_hour_to_man_days

class TaskApplicationService:
    def __init__(self):
        self.actual_task_repository = ActualTaskRepository(
            config.NOTION_TOKEN, 
            config.TASK_DB_ID
        )
        self.budget_task_repository = BudgetTaskRepository(
            config.NOTION_TOKEN, 
            config.TASK_DB_ID
        )
        self.service = BudgetTaskService()
        
    def update_actual_task(self, tags: List[str] = None):
        '''タスクの実績を更新する
        
        :param str tag: タグ
        '''
        # タスクの実績を取得
        actual_tasks: List[ActualTask] = self.actual_task_repository.find_by_tags(tags=tags)
        # タスクの予定を取得
        budget_tasks: List[BudgetTask] = self.budget_task_repository.find_by_tags(tags=tags)

        # 予定タスクごとに実績工数を集計
        for budget_task in budget_tasks:
            man_hour = sum(map(
                lambda actual_task: actual_task.man_hour if actual_task.budget_task_id == budget_task.id else 0,
                actual_tasks
            ))
            
            # 実績工数を人日に変換
            actual_man_days = man_hour_to_man_days(man_hour)
            # copy
            updated_budget_task = budget_task.copy()

            if actual_man_days != 0 and actual_man_days != budget_task.actual_man_hour:
                # 予定タスクの実績工数を更新
                self.repository.update_man_hour(
                    page_id=budget_task.page_id,
                    actual_man_days=actual_man_days,
                    name=self.service.get_name_with_man_days_tag(budget_task, actual_man_days)
                )
        
if __name__ == '__main__':
    service = TaskApplicationService()
    service.update_actual_task(tags=["お小遣いクエストボード"])


        