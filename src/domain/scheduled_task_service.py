from typing import Callable
from domain.executed_task import ExecutedTask
from domain.name_labels.parent_id_label import ParentIdLabel
from domain.scheduled_task import ScheduledTask
from infrastructure.id_findable import IdFindable
from infrastructure.scheduled_task_repository import ScheduledTaskRepository

class ScheduledTaskService():
    '''ScheduledTaskのドメインサービスクラス'''
    
    def add_executed_tasks_to_scheduled(self, to: list[ScheduledTask], source: list[ExecutedTask], 
                                       on_error: Callable[[Exception, ScheduledTask], None],
                                       ) -> None: 
        '''予定タスクに実績タスクを追加する'''
        for scheduled_task in to:
            try:
                # 予定タスクのIDを持つ実績タスクをフィルタリング
                scheduled_task.update_executed_tasks(list(filter(
                    lambda executed_task: scheduled_task.id == executed_task.scheduled_task_id,
                    source
                )))

            except Exception as e:
                on_error(e, scheduled_task)

    async def update_parent_id(self, scheduled_task: ScheduledTask,
                                scheduled_tasks: list[ScheduledTask],
                                scheduled_task_repo: IdFindable,
                                on_error: Callable[[Exception, ScheduledTask], None],
                                ):
        '''予定タスクの親アイテムのIDを更新するメソッド'''
        try:
            # 現在取得している予定タスクに親アイテムのページIDがあれば取得する
            scheduled_task.parent_task = next(
                filter(
                    lambda task: task.page_id == scheduled_task.parent_task_page_id,
                    scheduled_tasks
                ),
                None
            )

            # 上の処理で取得出来なかった場合、リポジトリから親アイテムのページIDを取得する
            if scheduled_task.parent_task is None:
                scheduled_task.parent_task = await scheduled_task_repo.find_by_page_id(
                    page_id=scheduled_task.parent_task_page_id,
                )
        
            # 親アイテムラベルを更新する
            scheduled_task.update_parent_id_label(
                parent_id_label=ParentIdLabel.from_property(
                    parent_id=scheduled_task.parent_task.id,
                )
                )
        except Exception as e:
            on_error(e, scheduled_task)
            return
