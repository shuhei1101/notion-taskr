from domain.executed_task import ExecutedTask
from domain.scheduled_task import ScheduledTask
from domain.task_service import TaskService


class ExecutedTaskService:
    @staticmethod
    def add_id_tag(to: list[ExecutedTask], source: list[ScheduledTask]) -> None:
        '''予定タスクのIDを持つ実績タスクにIDを付与する'''
        for executed_task in to:
            if executed_task.name.id_label is not None: continue  # IDが付与されている場合はスキップ
            for scheduled_task in source:
                if executed_task.name.task_name == scheduled_task.name.task_name:
                    executed_task.update_id_label(scheduled_task.name.id_label)
                    executed_task.update_scheduled_task_id(scheduled_task.id)
                    break

    @staticmethod
    def get_tasks_add_id_tag(to: list[ExecutedTask], source: list[ScheduledTask]) -> list[ExecutedTask]:
        '''新たにIDが付与された予定タスクのみを返却する'''
        updated_tasks = []
        for executed_task in to:
            if executed_task.name.id_label is not None: continue
            for scheduled_task in source:
                if executed_task.name.task_name == scheduled_task.name.task_name:
                    executed_task.update_id_label(scheduled_task.name.id_label)
                    executed_task.update_scheduled_task_id(scheduled_task.id)
                    TaskService.upsert_tasks(to=updated_tasks, source=scheduled_task)
                    break
        return updated_tasks



