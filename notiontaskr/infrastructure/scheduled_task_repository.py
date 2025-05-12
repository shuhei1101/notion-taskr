from typing import Callable, List
from notiontaskr.domain.value_objects.page_id import PageId
from notiontaskr.infrastructure.scheduled_task_update_properties import (
    ScheduledTaskUpdateProperties,
)
from notion_client import Client

from notiontaskr import config
from notiontaskr.domain.scheduled_task import ScheduledTask
from notiontaskr.infrastructure.operator import CheckboxOperator
from notiontaskr.infrastructure.task_search_condition import TaskSearchCondition


class ScheduledTaskRepository:
    def __init__(self, token, db_id):
        self.client = Client(
            auth=token,
        )
        self.db_id = db_id
        self.filter = TaskSearchCondition()

    async def find_all(
        self, on_error: Callable[[Exception, dict[str]], None]
    ) -> List[ScheduledTask]:
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
        scheduled_tasks = []
        for data in response_data["results"]:
            try:
                scheduled_tasks.append(ScheduledTask.from_response_data(data))
            except Exception as e:
                # 名前が空のときにもスキップされる
                on_error(e, data)

        return scheduled_tasks

    async def find_by_condition(
        self,
        condition: TaskSearchCondition,
        on_error: Callable[[Exception, dict[str]], None],
    ) -> List[ScheduledTask]:
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
        scheduled_tasks = []
        for data in response_data["results"]:
            try:
                scheduled_tasks.append(ScheduledTask.from_response_data(data))
            except Exception as e:
                # 名前が空のときにもスキップされる
                on_error(e, data)

        return scheduled_tasks

    async def find_all_by_condition(
        self,
        condition: TaskSearchCondition,
        on_error: Callable[[Exception, dict[str]], None],
    ) -> List[ScheduledTask]:
        """指定した条件に一致する全ての予定タスクをページネーションを考慮して取得する"""
        all_tasks = []
        start_cursor = None
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
        on_error: Callable[[Exception, dict[str]], None],
        start_cursor: str = None,
    ) -> tuple[list[ScheduledTask], str, bool]:
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
        scheduled_tasks = []
        for data in response_data["results"]:
            try:
                scheduled_tasks.append(ScheduledTask.from_response_data(data))
            except Exception as e:
                on_error(e, data)
        next_cursor = response_data.get("next_cursor")
        has_more = response_data.get("has_more", False)
        return scheduled_tasks, next_cursor, has_more

    async def find_by_page_id(self, page_id: PageId) -> ScheduledTask:
        """ページIDから1件のページ情報を取得する"""
        try:
            response_data = self.client.pages.retrieve(page_id=str(page_id))
            task = ScheduledTask.from_response_data(response_data)
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


# 動作確認用
if __name__ == "__main__":
    token = config.NOTION_TOKEN
    db_id = config.TASK_DB_ID

    scheduled_task_repo = ScheduledTaskRepository(token, db_id)
    # scheduled_task = scheduled_task_repo.find_by_page_id(
    #     page_id='1875ffa1-def1-4c34-8875-e559eb6e5853'
    # )
    import asyncio

    scheduled_task = asyncio.run(
        scheduled_task_repo.find_all(
            on_error=lambda e, data: print(f"Error: {e}, Data: {data}")
        )
    )
    print(scheduled_task)
