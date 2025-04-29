from typing import Callable
from domain.executed_task import ExecutedTask
from domain.scheduled_task import ScheduledTask

class ScheduledTaskService():
    '''BudegetTaskのドメインサービスクラス'''
    
    def add_executed_tasks_to_scheduled(self, to: list[ScheduledTask], source: list[ExecutedTask], 
                                       on_error: Callable[[Exception, ScheduledTask], None],
                                       ) -> None: 
        '''予定タスクに実績タスクを追加する'''
        for scheduled_task in to:
            try:
                # 予定タスクのIDを持つ実績タスクをフィルタリング
                scheduled_task.update_executed_tasks(list(filter(
                    lambda executed_task: scheduled_task.name.id_label.value == executed_task.scheduled_task_id,
                    source
                )))

            except Exception as e:
                on_error(e, scheduled_task)

