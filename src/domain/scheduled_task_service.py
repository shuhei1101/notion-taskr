import copy
from domain.excuted_task import ExcutedTask
from domain.scheduled_task import ScheduledTask
from domain.name_labels.man_days_label import ManDaysLabel

class ScheduledTaskService():
    '''BudegetTaskのドメインサービスクラス'''
    
    def add_excuted_tasks_to_scheduled(self, scheduled_tasks: list[ScheduledTask], excuted_tasks: list[ExcutedTask]):
        '''予定タスクに実績タスクを追加する'''
        for scheduled_task in scheduled_tasks:
            # 予定タスクのIDを持つ実績タスクをフィルタリング
            scheduled_task.excuted_tasks = list(filter(
                lambda excuted_task: scheduled_task.name.id_label.value == excuted_task.scheduled_task_id,
                excuted_tasks
            ))

        return scheduled_tasks

    def aggregate_excuted_man_days(self, scheduled_tasks: list[ScheduledTask], excuted_tasks: list[ExcutedTask]):
        '''予定タスクごとに実績工数を集計する'''

        updated_scheduled_tasks = []

        for scheduled_task in scheduled_tasks:
            excuted_man_days = sum(map(
                # もし予定タスクのIDを持つ実績タスクがあれば、その工数の合計を算出
                lambda excuted_task: excuted_task.man_days if str(excuted_task.scheduled_task_id) == str(scheduled_task.id) else 0,
                excuted_tasks
            ))
            
            # コピーの作成
            updated_scheduled_task = copy.deepcopy(scheduled_task)

            # 予定タスクの実績工数を更新
            updated_scheduled_task.update_excuted_man_days(excuted_man_days)
            
            # 実績工数タグの追加
            updated_scheduled_task.update_man_days_label(ManDaysLabel.from_man_days(
                excuted_man_days=excuted_man_days,
                scheduled_man_days=scheduled_task.scheduled_man_days,
            ))

            updated_scheduled_tasks.append(updated_scheduled_task)

        return updated_scheduled_tasks
