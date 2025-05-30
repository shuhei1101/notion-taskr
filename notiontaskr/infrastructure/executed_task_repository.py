from typing import Callable, List
from notiontaskr.infrastructure.executed_task_update_properties import (
    ExecutedTaskUpdateProperties,
)
from notion_client import Client

from notiontaskr.domain.executed_task import ExecutedTask
from notiontaskr.infrastructure.operator import CheckboxOperator
from notiontaskr.infrastructure.task_search_condition import TaskSearchCondition

from notiontaskr.domain.executed_tasks import ExecutedTasks


class ExecutedTaskRepository:
    def __init__(self, token, db_id):
        self.client = Client(
            auth=token,
        )
        self.db_id = db_id
        self.filter = TaskSearchCondition()

    async def find_all(
        self, on_error: Callable[[Exception, dict], None]
    ) -> ExecutedTasks:
        """全ての実績を取得する"""
        filter = (
            TaskSearchCondition()
            .and_(
                TaskSearchCondition().where_scheduled_flag(
                    operator=CheckboxOperator.EQUALS, is_scheduled=False
                ),
            )
            .build()
        )

        response_data = self.client.databases.query(
            **{"database_id": self.db_id, "filter": filter}
        )

        # response_dataをScheduledTaskのリストに変換する
        executed_tasks = ExecutedTasks.from_empty()
        for data in response_data["results"]:  # type: ignore
            try:
                executed_tasks.append(ExecutedTask.from_response_data(data))
            except Exception as e:
                on_error(e, data)
        return executed_tasks

    async def find_by_condition(
        self,
        condition: TaskSearchCondition,
        on_error: Callable[[Exception, dict], None],
    ) -> ExecutedTasks:
        """指定した実績を全て取得する"""

        filter = (
            TaskSearchCondition()
            .and_(
                TaskSearchCondition().where_scheduled_flag(
                    operator=CheckboxOperator.EQUALS, is_scheduled=False
                ),
                condition,
            )
            .build()
        )

        response_data = self.client.databases.query(
            **{"database_id": self.db_id, "filter": filter}
        )

        # response_dataをScheduledTaskのリストに変換する
        executed_tasks = ExecutedTasks.from_empty()
        for data in response_data["results"]:  # type: ignore
            try:
                executed_tasks.append(ExecutedTask.from_response_data(data))
            except Exception as e:
                on_error(e, data)

        return executed_tasks

    async def find_all_by_condition(
        self,
        condition: TaskSearchCondition,
        on_error: Callable[[Exception, dict], None],
    ) -> ExecutedTasks:
        """指定した条件に一致する全ての実績タスクをページネーションを考慮して取得する"""
        all_tasks = ExecutedTasks.from_empty()
        start_cursor = ""
        has_more = True
        while has_more:
            tasks, next_cursor, has_more = await self._find_by_condition_with_cursor(
                condition=condition,
                on_error=on_error,
                start_cursor=start_cursor,
            )
            all_tasks.extend(tasks)
            start_cursor = next_cursor
        return all_tasks

    async def _find_by_condition_with_cursor(
        self,
        condition: TaskSearchCondition,
        on_error: Callable[[Exception, dict], None],
        start_cursor: str,
    ) -> tuple[ExecutedTasks, str, bool]:
        """タスクDBの指定タグの実績を全て取得する（ページネーション対応）"""
        filter = (
            TaskSearchCondition()
            .and_(
                TaskSearchCondition().where_scheduled_flag(
                    operator=CheckboxOperator.EQUALS, is_scheduled=False
                ),
                condition,
            )
            .build()
        )
        query_params = {"database_id": self.db_id, "filter": filter}
        if start_cursor:
            query_params["start_cursor"] = start_cursor

        response_data = self.client.databases.query(**query_params)
        executed_tasks = ExecutedTasks.from_empty()
        for data in response_data["results"]:  # type: ignore
            try:
                executed_tasks.append(ExecutedTask.from_response_data(data))
            except Exception as e:
                on_error(e, data)
        next_cursor = response_data.get("next_cursor")  # type: ignore
        has_more = response_data.get("has_more", False)  # type: ignore
        return executed_tasks, next_cursor, has_more

    async def update(
        self,
        executed_task: ExecutedTask,
        on_success: Callable[[ExecutedTask], None],
        on_error: Callable[[Exception, ExecutedTask], None],
    ) -> None:
        """実績タスクを更新する"""

        try:
            properties = (
                ExecutedTaskUpdateProperties(task=executed_task)
                .set_name()
                .set_status()
                .set_parent_task_page_id()
                .set_scheduled_task_page_id()
                .set_has_before_start()
                .set_has_before_end()
                .set_before_start_minutes()
                .set_before_end_minutes()
                .build()
            )

            self.client.pages.update(
                **{"page_id": str(executed_task.page_id), "properties": properties}
            )
            on_success(executed_task)
        except Exception as e:
            on_error(e, executed_task)
            return
