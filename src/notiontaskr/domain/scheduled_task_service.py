from typing import Callable
from notiontaskr.domain.executed_task import ExecutedTask
from notiontaskr.domain.scheduled_task import ScheduledTask
from notiontaskr.domain.task_service import TaskService
from notiontaskr.domain.value_objects.notion_id import NotionId
from notiontaskr.domain.value_objects.page_id import PageId


class ScheduledTaskService:
    """ScheduledTaskのドメインサービスクラス"""

    @staticmethod
    def get_tasks_upserted_executed_tasks(
        scheduled_tasks_by_id: dict[NotionId, ScheduledTask],
        executed_tasks: list[ExecutedTask],
        on_error: Callable[[Exception, ScheduledTask], None],
    ) -> list[ScheduledTask]:
        """新たに実績タスクが付与された予定タスクのみを取得する

        - **注意**: 本メソッドは予定タスクが直接変更される。
        """
        updated_tasks = []
        for executed_task in executed_tasks:
            try:
                target_task = scheduled_tasks_by_id.get(executed_task.scheduled_task_id)
                if target_task is None:
                    continue
                TaskService.upsert_tasks(target_task.executed_tasks, executed_task)
                TaskService.upsert_tasks(updated_tasks, target_task)

            except Exception as e:
                on_error(e, executed_task)

        return updated_tasks

    @staticmethod
    def get_tasks_appended_child_tasks(
        child_tasks: list[ScheduledTask],
        parent_tasks_by_page_id: dict[PageId, ScheduledTask],
        on_error: Callable[[Exception, ScheduledTask], None],
    ) -> list[ScheduledTask]:
        """新たにサブアイテムが付与された予定タスクのみを取得する

        - **注意**: 本メソッドは予定タスクが直接変更される。
        """
        updated_tasks = []
        for child_task in child_tasks:
            try:
                target_task = parent_tasks_by_page_id.get(
                    child_task.parent_task_page_id
                )
                if target_task is None:
                    continue
                TaskService.upsert_tasks(target_task.child_tasks, child_task)
                TaskService.upsert_tasks(updated_tasks, target_task)

            except Exception as e:
                on_error(e, child_task)

        return updated_tasks
