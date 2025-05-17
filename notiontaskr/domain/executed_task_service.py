from notiontaskr.domain.executed_task import ExecutedTask
from notiontaskr.domain.scheduled_task import ScheduledTask
from notiontaskr.domain.task_service import TaskService


class ExecutedTaskService:

    @staticmethod
    def get_tasks_add_id_tag(
        to: list[ExecutedTask], source: list[ScheduledTask]
    ) -> list[ScheduledTask]:
        """予定タスクと同じ名前を持つ実績タスクに同じIDを付与し、
        新たにIDが付与された予定タスクのみを返却する"""
        updated_tasks = []
        for executed_task in to:
            if executed_task.name.id_label is not None:
                continue
            for scheduled_task in source:
                if executed_task.name.task_name == scheduled_task.name.task_name:
                    executed_task.update_id_label(scheduled_task.name.id_label)  # type: ignore (予定タスクのIDがNoneになることはない)
                    executed_task.update_scheduled_task_id(scheduled_task.id)
                    TaskService.upsert_tasks(to=updated_tasks, source=scheduled_task)
                    break
        return updated_tasks
