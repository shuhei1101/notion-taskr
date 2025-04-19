from domain.actual_task import ActualTask
from domain.budget_task import BudgetTask

class BudgetTaskService():
    '''BudegetTaskのドメインサービスクラス'''
    
    def add_actual_tasks_to_budget(self, budget_tasks: list[BudgetTask], actual_tasks: list[ActualTask]):
        '''予定タスクに実績タスクを追加する'''
        for budget_task in budget_tasks:
            # 予定タスクのIDを持つ実績タスクをフィルタリング
            budget_task.actual_tasks = list(filter(
                lambda actual_task: budget_task.name.id_label.value == actual_task.budget_task_id,
                actual_tasks
            ))

        return budget_tasks
