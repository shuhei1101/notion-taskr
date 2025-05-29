import copy
from typing import Callable
from notiontaskr.domain.executed_task import ExecutedTask
from notiontaskr.domain.scheduled_task import ScheduledTask
from notiontaskr.domain.value_objects.notion_id import NotionId
from notiontaskr.domain.scheduled_tasks import ScheduledTasks
from notiontaskr.domain.executed_tasks import ExecutedTasks


class ScheduledTaskService:
    """ScheduledTaskのドメインサービスクラス"""

    def get_tasks_upserted_executed_tasks(
        self,
        to: ScheduledTasks,
        source: ExecutedTasks,
        on_error: Callable[[Exception, ExecutedTask], None],
    ) -> "ScheduledTasks":
        """予定タスクに実績タスクを付与し、更新された予定タスクを取得する

        :return ScheduledTasks: 新たに実績タスクが付与された予定タスク配列
        :return ScheduledTasks: 更新された予定タスク
        """
        scheduled_tasks_upserted_executed = ScheduledTasks.from_empty()
        scheduled_tasks_by_id = to.get_tasks_by_id()
        for executed_task in source:
            try:
                target_scheduled_task = scheduled_tasks_by_id.get((executed_task.scheduled_task_id))  # type: ignore (既にエラーハンドルしているため)
                if target_scheduled_task is None:
                    continue
                target_scheduled_task.executed_tasks.upsert_by_id(
                    ExecutedTasks.from_tasks([executed_task])
                )

                scheduled_tasks_upserted_executed.upsert_by_id(
                    ScheduledTasks.from_tasks([target_scheduled_task])
                )

            except Exception as e:
                on_error(e, executed_task)
                continue

        return scheduled_tasks_upserted_executed

    def get_parent_tasks_appended_sub_tasks(
        self,
        parent_tasks: ScheduledTasks,
        sub_tasks: ScheduledTasks,
        on_error: Callable[[Exception, ScheduledTask], None],
    ) -> ScheduledTasks:
        """新たにサブアイテムが付与された予定タスクのみを取得する"""
        parent_tasks_by_page_id = parent_tasks.get_tasks_by_page_id()
        parent_tasks_appended_sub = ScheduledTasks.from_empty()
        for sub_task in sub_tasks:
            try:
                target_parent_task = parent_tasks_by_page_id.get(sub_task.parent_task_page_id)  # type: ignore (既にエラーハンドルしているため)
                if target_parent_task is None:
                    continue
                target_parent_task.sub_tasks.upsert_by_id(
                    ScheduledTasks.from_tasks([sub_task])
                )
                parent_tasks_appended_sub.upsert_by_id(
                    ScheduledTasks.from_tasks([target_parent_task])
                )

            except Exception as e:
                on_error(e, sub_task)

        return parent_tasks_appended_sub
