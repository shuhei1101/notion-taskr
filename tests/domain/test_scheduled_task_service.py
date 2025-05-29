from unittest.mock import Mock

from notiontaskr.domain.value_objects.notion_id import NotionId
from notiontaskr.domain.scheduled_task_service import ScheduledTaskService
from notiontaskr.domain.scheduled_tasks import ScheduledTasks
from notiontaskr.domain.executed_tasks import ExecutedTasks
from notiontaskr.domain.scheduled_task import ScheduledTask
from notiontaskr.domain.executed_task import ExecutedTask

from notiontaskr.domain.value_objects.page_id import PageId


class TestScheduledTaskService:
    class Test_get_tasks_upserted_executed_tasks:
        def test_予定タスクIDが一致する実績タスクを追加できること(self):
            scheduled_tasks = ScheduledTasks.from_tasks(
                [
                    ScheduledTask(
                        id=NotionId("scheduled_id_1"),
                        name=Mock(),
                        tags=Mock(),
                        page_id=Mock(),
                        status=Mock(),
                    )
                ]
            )
            executed_tasks = ExecutedTasks.from_tasks(
                [
                    ExecutedTask(
                        page_id=Mock(),
                        name=Mock(),
                        tags=Mock(),
                        id=Mock(),
                        status=Mock(),
                        scheduled_task_id=NotionId("scheduled_id_1"),
                    )
                ]
            )

            scheduled_tasks_upserted_executed = (
                ScheduledTaskService().get_tasks_upserted_executed_tasks(
                    to=scheduled_tasks,
                    source=executed_tasks,
                    on_error=lambda e, t: None,
                )
            )

            assert len(scheduled_tasks_upserted_executed) == 1
            assert scheduled_tasks_upserted_executed[0].id == NotionId("scheduled_id_1")

        def test_対象の予定タスクが存在しない場合は何も追加されないこと(self):
            scheduled_tasks = ScheduledTasks.from_tasks(
                [
                    ScheduledTask(
                        id=NotionId("scheduled_id_1"),
                        name=Mock(),
                        tags=Mock(),
                        page_id=Mock(),
                        status=Mock(),
                    )
                ]
            )
            executed_tasks = ExecutedTasks.from_tasks(
                [
                    ExecutedTask(
                        page_id=Mock(),
                        name=Mock(),
                        tags=Mock(),
                        id=Mock(),
                        status=Mock(),
                        scheduled_task_id=NotionId("scheduled_id_2"),
                    )
                ]
            )

            scheduled_tasks_upserted_executed = ScheduledTaskService().get_tasks_upserted_executed_tasks(
                scheduled_tasks, executed_tasks, lambda e, t: None  # type: ignore
            )

            assert len(scheduled_tasks_upserted_executed) == 0

    class Test_get_tasks_appended_sub_tasks:
        def test_親タスクIDが一致するサブタスクを追加できること(self):
            parent_tasks = ScheduledTasks.from_tasks(
                [
                    ScheduledTask(
                        id=NotionId("parent_id_1"),
                        name=Mock(),
                        tags=Mock(),
                        page_id=PageId("parent_id_1"),
                        status=Mock(),
                    )
                ]
            )
            sub_tasks = ScheduledTasks.from_tasks(
                [
                    ScheduledTask(
                        id=Mock(),
                        name=Mock(),
                        tags=Mock(),
                        page_id=Mock(),
                        status=Mock(),
                        parent_task_page_id=PageId("parent_id_1"),
                    )
                ]
            )

            parent_tasks_appended_sub = (
                ScheduledTaskService().get_parent_tasks_appended_sub_tasks(
                    parent_tasks=parent_tasks,
                    sub_tasks=sub_tasks,
                    on_error=lambda e, t: None,  # type: ignore
                )
            )

            assert len(parent_tasks_appended_sub) == 1
            assert parent_tasks_appended_sub[0].id == NotionId("parent_id_1")

        def test_対象の親タスクが存在しない場合は何も追加されないこと(self):
            parent_tasks = ScheduledTasks.from_tasks(
                [
                    ScheduledTask(
                        id=NotionId("parent_id_1"),
                        name=Mock(),
                        tags=Mock(),
                        page_id=PageId("parent_id_1"),
                        status=Mock(),
                    )
                ]
            )
            sub_tasks = ScheduledTasks.from_tasks(
                [
                    ScheduledTask(
                        id=Mock(),
                        name=Mock(),
                        tags=Mock(),
                        page_id=Mock(),
                        status=Mock(),
                        parent_task_page_id=PageId(
                            "parent_id_2"
                        ),  # 親タスクIDが一致しない
                    )
                ]
            )

            parent_tasks_appended_sub = (
                ScheduledTaskService().get_parent_tasks_appended_sub_tasks(
                    parent_tasks=parent_tasks,
                    sub_tasks=sub_tasks,
                    on_error=lambda e, t: None,  # type: ignore
                )
            )
            assert len(parent_tasks_appended_sub) == 0
