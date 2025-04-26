import copy
from domain.excuted_task import ExcutedTask
from domain.scheduled_task import ScheduledTask

class ScheduledTaskService():
    '''BudegetTaskのドメインサービスクラス'''
    
    def add_excuted_tasks_to_scheduled(self, scheduled_tasks: list[ScheduledTask], excuted_tasks: list[ExcutedTask]) -> None:
        '''予定タスクに実績タスクを追加する'''
        for scheduled_task in scheduled_tasks:
            # 予定タスクのIDを持つ実績タスクをフィルタリング
            scheduled_task.update_excuted_tasks(list(filter(
                lambda excuted_task: scheduled_task.name.id_label.value == excuted_task.scheduled_task_id,
                excuted_tasks
            )))
