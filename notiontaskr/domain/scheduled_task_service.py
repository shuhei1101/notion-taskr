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
        on_error: Callable[[Exception, ExecutedTask], None],
    ) -> list[ScheduledTask]:
        """新たに実績タスクが付与された予定タスクのみを取得する

        - **注意**: 本メソッドは予定タスクが直接変更される。
        """
        updated_tasks = []
        for executed_task in executed_tasks:
            try:
                target_task = scheduled_tasks_by_id.get(executed_task.scheduled_task_id)  # type: ignore (既にエラーハンドルしているため)
                if target_task is None:
                    continue
                TaskService.upsert_tasks(target_task.executed_tasks, executed_task)
                TaskService.upsert_tasks(updated_tasks, target_task)

            except Exception as e:
                on_error(e, executed_task)

        return updated_tasks

    @staticmethod
    def get_tasks_appended_sub_tasks(
        sub_tasks: list[ScheduledTask],
        parent_tasks_by_page_id: dict[PageId, ScheduledTask],
        on_error: Callable[[Exception, ScheduledTask], None],
    ) -> list[ScheduledTask]:
        """新たにサブアイテムが付与された予定タスクのみを取得する

        - **注意**: 本メソッドは予定タスクが直接変更される。
        """
        updated_tasks = []
        for sub_task in sub_tasks:
            try:
                target_task = parent_tasks_by_page_id.get(sub_task.parent_task_page_id)  # type: ignore (既にエラーハンドルしているため)
                if target_task is None:
                    continue
                TaskService.upsert_tasks(target_task.sub_tasks, sub_task)
                TaskService.upsert_tasks(updated_tasks, target_task)

            except Exception as e:
                on_error(e, sub_task)

        return updated_tasks

    @staticmethod
    def merge_scheduled_tasks(
        scheduled_tasks_by_id: dict[NotionId, ScheduledTask],
        sources: list[ScheduledTask],
        on_error: Callable[[Exception, ScheduledTask], None] = lambda e, t: None,
    ) -> dict[NotionId, ScheduledTask]:
        """キャッシュと取得した予定タスクをマージする

        マージする際、task.executed_tasksはマージ先に引き継ぐ
        """
        for source in sources:
            try:
                if source.id in scheduled_tasks_by_id:
                    # 既存のタスクに実績タスクをマージする
                    source.update_executed_tasks(
                        scheduled_tasks_by_id[source.id].executed_tasks
                    )
                    source.update_sub_tasks(scheduled_tasks_by_id[source.id].sub_tasks)
                    scheduled_tasks_by_id[source.id] = source
                else:
                    # 新しいタスクを追加する
                    scheduled_tasks_by_id[source.id] = source
            except Exception as e:
                on_error(e, source)

        return scheduled_tasks_by_id

    @staticmethod
    def get_scheduled_tasks_by_tags(
        scheduled_tasks: list[ScheduledTask], tags: list[str]
    ) -> dict[str, ScheduledTask]:
        """指定したタグを持つ予定タスクを取得する"""
        scheduled_tasks_by_tags = {}
        for task in scheduled_tasks:
            for tag in task.tags:
                if tag in tags:
                    scheduled_tasks_by_tags[tag] = task
        return scheduled_tasks_by_tags
