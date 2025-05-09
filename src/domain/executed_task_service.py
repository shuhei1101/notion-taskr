from domain.executed_task import ExecutedTask
from domain.scheduled_task import ScheduledTask


class ExecutedTaskService:
    def __init__(self):
        pass

    # 予定タスク名配列を回し、一致する実績タスクの名前にIDをタグとして付与する
    def add_id_tag(self, to: list[ExecutedTask], source: list[ScheduledTask]) -> None:
        '''予定タスクのIDを持つ実績タスクにIDを付与する'''
        for scheduled_task in source:
            # 予定タスクの名前と一致するID未付与実績タスクをフィルタリング
            filtered_executed_tasks = list(filter(
                lambda executed_task: executed_task.name.task_name == scheduled_task.name.task_name,
                [executed_task for executed_task in to if executed_task.name.id_label is None]
            ))

            # 一致する実績タスクにIDを付与する
            for executed_task in filtered_executed_tasks:
                executed_task.update_id_label(scheduled_task.name.id_label)


