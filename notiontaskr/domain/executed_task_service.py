from notiontaskr.domain.executed_task import ExecutedTask
from notiontaskr.domain.executed_tasks import ExecutedTasks

from notiontaskr.domain.value_objects.man_hours import ManHours

from notiontaskr.domain.scheduled_tasks import ScheduledTasks


class ExecutedTaskService:

    def get_scheduled_tasks_added_executed_id(
        self, to: ExecutedTasks, source: ScheduledTasks
    ) -> ScheduledTasks:
        """予定タスクと同じ名前を持つ実績タスクに同じIDを付与し、
        新たにIDが付与された予定タスクのみを返却する"""
        updated_tasks = ScheduledTasks.from_empty()
        for executed_task in to:
            if executed_task.name.id_label is not None:
                continue
            for scheduled_task in source:
                if executed_task.name.task_name == scheduled_task.name.task_name:
                    executed_task.update_id_label(scheduled_task.name.id_label)  # type: ignore (予定タスクのIDがNoneになることはない)
                    executed_task.update_scheduled_task_id(scheduled_task.id)
                    updated_tasks.append(scheduled_task)
                    break

        # 更新した予定タスクを取得する(重複除去)
        return updated_tasks.get_unique_tasks_by_id()
