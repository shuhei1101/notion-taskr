from typing import Callable
from domain.executed_task import ExecutedTask
from domain.scheduled_task import ScheduledTask
from domain.task_service import TaskService

class ScheduledTaskService():
    '''ScheduledTaskのドメインサービスクラス'''
    
    @staticmethod
    def add_executed_tasks(scheduled_tasks: list[ScheduledTask], executed_tasks: list[ExecutedTask], 
                                       on_error: Callable[[Exception, ScheduledTask], None],
                                       ) -> None: 
        '''予定タスクに実績タスクを追加する
        
        - **注意**: 本メソッドは予定タスクが直接変更される。
        '''
        for executed_task in executed_tasks:
            try:
                for scheduled_task in scheduled_tasks:
                    # 実績タスクのIDと予定タスクのIDが一致する場合
                    if executed_task.scheduled_task_id == scheduled_task.id:
                        # 予定タスクに実績タスクを追加
                        TaskService.upsert_tasks(scheduled_task.executed_tasks, executed_task)
                        break

            except Exception as e:
                on_error(e, executed_task)
         
    @staticmethod
    def add_child_tasks(child_tasks: list[ScheduledTask], parent_tasks: list[ScheduledTask],
                                on_error: Callable[[Exception, ScheduledTask], None],
                                ) -> None:
        '''予定タスクにサブアイテムを追加する
        
        - **注意**: 本メソッドは予定タスクが直接変更される。
        '''
        for parent_task in parent_tasks:
            try:
                # 親タスクのchild_task_page_idsに含まれるIDを持つ子タスクをフィルタリング
                matched_tasks = list(filter(
                    lambda child_task: child_task.page_id in parent_task.child_task_page_ids,
                    child_tasks
                ))
                parent_task.update_child_tasks(matched_tasks)

            except Exception as e:
                on_error(e, parent_task)

    @staticmethod
    def get_tasks_appended_child_tasks(child_tasks: list[ScheduledTask], 
                             parent_tasks: list[ScheduledTask],
                             on_error: Callable[[Exception, ScheduledTask], None],
                             ) -> list[ScheduledTask]:
        '''新たにサブアイテムが付与された予定タスクのみを取得する
        
        - **注意**: 本メソッドは予定タスクが直接変更される。
        '''
        updated_tasks = []
        for child_task in child_tasks:
            try:
                for parent_task in parent_tasks:
                    # サブアイテムの親IDと親タスクのIDが一致する場合
                    if child_task.parent_task_page_id == parent_task.page_id:
                        # 親タスクにサブアイテムを追加
                        TaskService.upsert_tasks(parent_task.child_tasks, child_task)
                        TaskService.upsert_tasks(updated_tasks, parent_task)
                        break
                    
            except Exception as e:
                on_error(e, child_task)
                
        return updated_tasks
