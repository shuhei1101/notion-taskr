from typing import Callable
from notiontaskr.domain.value_objects.page_id import PageId
from notiontaskr.infrastructure.scheduled_task_update_properties import (
    ScheduledTaskUpdateProperties,
)
from notion_client import Client
from notiontaskr.domain.scheduled_task import ScheduledTask
from notiontaskr.infrastructure.operator import CheckboxOperator
from notiontaskr.infrastructure.task_search_condition import TaskSearchCondition
from notiontaskr.domain.scheduled_tasks import ScheduledTasks


class ScheduledTaskRepository:
    def __init__(self, token, db_id):
        self.client = Client(
            auth=token,
        )
        self.db_id = db_id
        self.filter = TaskSearchCondition()

    async def find_all(
        self, on_error: Callable[[Exception, dict], None]
    ) -> ScheduledTasks:
        """全ての予定を取得する"""
        filter = (
            TaskSearchCondition()
            .and_(
                TaskSearchCondition().where_scheduled_flag(
                    operator=CheckboxOperator.EQUALS, is_scheduled=True
                ),
            )
            .build()
        )

        response_data = self.client.databases.query(
            **{"database_id": self.db_id, "filter": filter}
        )

        # response_dataをScheduledTaskのリストに変換する
        scheduled_tasks = ScheduledTasks.from_empty()
        for data in response_data["results"]:  # type: ignore
            try:
                scheduled_tasks.append(ScheduledTask.from_response_data(data))
            except Exception as e:
                # 名前が空のときにもスキップされる
                on_error(e, data)

        return scheduled_tasks

    async def find_by_condition(
        self,
        condition: TaskSearchCondition,
        on_error: Callable[[Exception, dict], None],
    ) -> ScheduledTasks:
        """タスクDBの指定タグの予定を全て取得する"""
        filter = (
            TaskSearchCondition()
            .and_(
                TaskSearchCondition().where_scheduled_flag(
                    operator=CheckboxOperator.EQUALS, is_scheduled=True
                ),
                condition,
            )
            .build()
        )

        response_data = self.client.databases.query(
            **{"database_id": self.db_id, "filter": filter}
        )

        # response_dataをScheduledTaskのリストに変換する
        scheduled_tasks = ScheduledTasks.from_empty()
        for data in response_data["results"]:  # type: ignore
            try:
                scheduled_tasks.append(ScheduledTask.from_response_data(data))
            except Exception as e:
                # 名前が空のときにもスキップされる
                on_error(e, data)

        return scheduled_tasks

    async def find_all_by_condition(
        self,
        condition: TaskSearchCondition,
        on_error: Callable[[Exception, dict], None],
    ) -> ScheduledTasks:
        """指定した条件に一致する全ての予定タスクをページネーションを考慮して取得する"""
        all_tasks = ScheduledTasks.from_empty()
        start_cursor = None
        has_more = True
        while has_more:
            tasks, next_cursor, has_more = await self._find_by_condition_with_cursor(
                condition=condition,
                on_error=on_error,
                start_cursor=start_cursor,  # type: ignore
            )
            all_tasks.extend(tasks)
            start_cursor = next_cursor
        return all_tasks

    async def _find_by_condition_with_cursor(
        self,
        condition: TaskSearchCondition,
        on_error: Callable[[Exception, dict], None],
        start_cursor: str = None,  # type: ignore
    ) -> tuple[ScheduledTasks, str, bool]:
        """タスクDBの指定タグの予定を全て取得する（ページネーション対応）"""
        filter = (
            TaskSearchCondition()
            .and_(
                TaskSearchCondition().where_scheduled_flag(
                    operator=CheckboxOperator.EQUALS, is_scheduled=True
                ),
                condition,
            )
            .build()
        )
        query_params = {"database_id": self.db_id, "filter": filter}
        if start_cursor:
            query_params["start_cursor"] = start_cursor

        response_data = self.client.databases.query(**query_params)
        scheduled_tasks = ScheduledTasks.from_empty()
        for data in response_data["results"]:  # type: ignore
            try:
                scheduled_tasks.append(ScheduledTask.from_response_data(data))
            except Exception as e:
                on_error(e, data)
        next_cursor = response_data.get("next_cursor")  # type: ignore
        has_more = response_data.get("has_more", False)  # type: ignore
        return scheduled_tasks, next_cursor, has_more

    async def find_by_page_id(self, page_id: PageId) -> ScheduledTask:
        """ページIDから1件のページ情報を取得する"""
        try:
            response_data = self.client.pages.retrieve(page_id=str(page_id))
            task = ScheduledTask.from_response_data(response_data)  # type: ignore
            return task

        except Exception as e:
            raise RuntimeError(f"ページ取得失敗: {e}")

    async def update(
        self,
        scheduled_task: ScheduledTask,
        on_success: Callable[[ScheduledTask], None],
        on_error: Callable[[Exception, ScheduledTask], None],
    ):
        """予定タスクを更新する"""

        try:
            properties = (
                ScheduledTaskUpdateProperties(task=scheduled_task)
                .set_name()
                .set_status()
                .set_scheduled_man_hours()
                .set_executed_man_hours()
                .set_progress_rate()
                .build()
            )

            self.client.pages.update(
                **{"page_id": str(scheduled_task.page_id), "properties": properties}
            )
            on_success(scheduled_task)
        except Exception as e:
            on_error(e, scheduled_task)
