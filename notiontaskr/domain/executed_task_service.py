from notiontaskr.domain.executed_task import ExecutedTask
from notiontaskr.domain.scheduled_task import ScheduledTask
from notiontaskr.domain.task_service import TaskService

from notiontaskr.domain.value_objects.man_hours import ManHours


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

    @staticmethod
    def get_executed_tasks_by_tag(
        executed_tasks: list[ExecutedTask], tags: list[str]
    ) -> dict[str, list[ExecutedTask]]:
        """指定したタグを持つ実績タスクを取得する"""
        executed_tasks_by_tags = {}
        for task in executed_tasks:
            for tag in task.tags:
                if tag in tags:
                    if tag not in executed_tasks_by_tags:
                        executed_tasks_by_tags[tag] = []
                    executed_tasks_by_tags[tag].append(task)
        return executed_tasks_by_tags

    @staticmethod
    def get_total_man_hours(executed_tasks: list[ExecutedTask]) -> float:
        """実績タスクの工数を合計する"""
        total_man_hours = ManHours(0)
        for task in executed_tasks:
            total_man_hours += task.man_hours

        return float(total_man_hours)
