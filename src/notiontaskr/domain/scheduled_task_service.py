from typing import Callable
from notiontaskr.domain.executed_task import ExecutedTask
from notiontaskr.domain.scheduled_task import ScheduledTask
from notiontaskr.domain.task_service import TaskService
from notiontaskr.domain.value_objects.notion_id import NotionId


class ScheduledTaskService:
    """ScheduledTaskのドメインサービスクラス"""

    @staticmethod
    def upsert_executed_tasks(
        scheduled_tasks_by_id: dict[NotionId, ScheduledTask],
        executed_tasks: list[ExecutedTask],
        on_error: Callable[[Exception, ScheduledTask], None],
    ) -> None:
        """予定タスクに実績タスクを追加する

        - **注意**: 本メソッドは予定タスクが直接変更される。
        """
        for executed_task in executed_tasks:
            try:
                target_task = scheduled_tasks_by_id.get(executed_task.scheduled_task_id)
                if target_task is None:
                    continue
                TaskService.upsert_tasks(target_task.executed_tasks, executed_task)

            except Exception as e:
                on_error(e, executed_task)

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
    def append_child_tasks(
        child_tasks: list[ScheduledTask],
        parent_tasks: list[ScheduledTask],
        on_error: Callable[[Exception, ScheduledTask], None],
    ) -> None:
        """予定タスクにサブアイテムを追加する

        - **注意**: 本メソッドは予定タスクが直接変更される。
        """
        for parent_task in parent_tasks:
            try:
                # 親タスクのchild_task_page_idsに含まれるIDを持つ子タスクをフィルタリング
                matched_tasks = list(
                    filter(
                        lambda child_task: child_task.page_id
                        in parent_task.child_task_page_ids,
                        child_tasks,
                    )
                )
                parent_task.update_child_tasks(matched_tasks)

            except Exception as e:
                on_error(e, parent_task)

    @staticmethod
    def get_tasks_appended_child_tasks(
        child_tasks: list[ScheduledTask],
        parent_tasks_by_id: dict[NotionId, ScheduledTask],
        on_error: Callable[[Exception, ScheduledTask], None],
    ) -> list[ScheduledTask]:
        """新たにサブアイテムが付与された予定タスクのみを取得する

        - **注意**: 本メソッドは予定タスクが直接変更される。
        """
        updated_tasks = []
        for child_task in child_tasks:
            try:
                target_task = parent_tasks_by_id.get(child_task.parent_task_page_id)
                if target_task is None:
                    continue
                TaskService.upsert_tasks(target_task.child_tasks, child_task)
                TaskService.upsert_tasks(updated_tasks, target_task)

            except Exception as e:
                on_error(e, child_task)

        return updated_tasks
