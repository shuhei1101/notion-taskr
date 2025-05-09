from typing import Callable
from domain.executed_task import ExecutedTask
from domain.scheduled_task import ScheduledTask

class ScheduledTaskService():
    '''ScheduledTaskのドメインサービスクラス'''
    
    def add_executed_tasks(self, scheduled_tasks: list[ScheduledTask], executed_tasks: list[ExecutedTask], 
                                       on_error: Callable[[Exception, ScheduledTask], None],
                                       ) -> None: 
        '''予定タスクに実績タスクを追加する
        
        - **注意**: 本メソッドは予定タスクが直接変更される。
        '''
        for scheduled_task in scheduled_tasks:
            try:
                # 予定タスクのIDを持つ実績タスクをフィルタリング
                scheduled_task.update_executed_tasks(list(filter(
                    lambda executed_task: scheduled_task.id == executed_task.scheduled_task_id,
                    executed_tasks
                )))

            except Exception as e:
                on_error(e, scheduled_task)

    def add_child_tasks(self, child_tasks: list[ScheduledTask], parent_tasks: list[ScheduledTask],
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

    def get_tasks_appended_child_tasks(self, child_tasks: list[ScheduledTask], 
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
                        parent_task.child_tasks.append(child_task)
                        updated_tasks.append(parent_task)
                        break
                    
            except Exception as e:
                on_error(e, child_task)
                
        return updated_tasks
