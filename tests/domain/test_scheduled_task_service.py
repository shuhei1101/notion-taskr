from unittest.mock import Mock

from notiontaskr.domain.value_objects.notion_id import NotionId

from notiontaskr.domain.scheduled_task_service import ScheduledTaskService


class TestScheduledTaskService:
    class Test_get_tasks_upserted_executed_tasks:
        def test_予定タスクIDが一致する実績タスクを追加できること(self):
            scheduled_task = Mock()
            scheduled_task.id = NotionId("scheduled_id_1")
            scheduled_task.executed_tasks = []
            executed_task = Mock()
            executed_task.scheduled_task_id = NotionId("scheduled_id_1")
            executed_task.name.task_name = "タスク1"
            executed_task.name.id_label = None
            scheduled_tasks_by_id = {scheduled_task.id: scheduled_task}
            executed_tasks = [executed_task]

            updated_tasks = ScheduledTaskService.get_tasks_upserted_executed_tasks(
                scheduled_tasks_by_id, executed_tasks, lambda e, t: None  # type: ignore
            )

            assert len(updated_tasks) == 1
            assert updated_tasks[0].id == NotionId("scheduled_id_1")

        def test_対象の予定タスクが存在しない場合は何も追加されないこと(self):
            scheduled_task = Mock()
            scheduled_task.id = NotionId("scheduled_id_1")
            scheduled_task.executed_tasks = []
            executed_task = Mock()
            executed_task.scheduled_task_id = NotionId("scheduled_id_2")
            executed_task.name.task_name = "タスク1"
            executed_task.name.id_label = None
            scheduled_tasks_by_id = {scheduled_task.id: scheduled_task}
            executed_tasks = [executed_task]

            updated_tasks = ScheduledTaskService.get_tasks_upserted_executed_tasks(
                scheduled_tasks_by_id, executed_tasks, lambda e, t: None  # type: ignore
            )

            assert len(updated_tasks) == 0

    class Test_get_tasks_appended_sub_tasks:
        def test_親タスクIDが一致するサブタスクを追加できること(self):
            parent_task = Mock()
            parent_task.page_id = NotionId("parent_id_1")
            parent_task.sub_tasks = []
            sub_task = Mock()
            sub_task.parent_task_page_id = NotionId("parent_id_1")
            sub_task.name.task_name = "サブタスク1"
            sub_tasks = [sub_task]
            parent_tasks_by_page_id = {parent_task.page_id: parent_task}

            updated_tasks = ScheduledTaskService.get_tasks_appended_sub_tasks(
                sub_tasks, parent_tasks_by_page_id, lambda e, t: None  # type: ignore
            )

            assert len(updated_tasks) == 1
            assert updated_tasks[0].page_id == NotionId("parent_id_1")

        def test_対象の親タスクが存在しない場合は何も追加されないこと(self):
            parent_task = Mock()
            parent_task.page_id = NotionId("parent_id_1")
            parent_task.sub_tasks = []
            sub_task = Mock()
            sub_task.parent_task_page_id = NotionId("parent_id_2")
            sub_task.name.task_name = "サブタスク1"
            sub_tasks = [sub_task]
            parent_tasks_by_page_id = {parent_task.page_id: parent_task}

            updated_tasks = ScheduledTaskService.get_tasks_appended_sub_tasks(
                sub_tasks, parent_tasks_by_page_id, lambda e, t: None  # type: ignore
            )

            assert len(updated_tasks) == 0

    class Test_merge_scheduled_tasks:
        def test_キャッシュと取得した予定タスクをマージできること(self):
            scheduled_task = Mock()
            scheduled_task.id = NotionId("scheduled_id_1")
            scheduled_task.name.task_name = "タスク1"
            scheduled_tasks_by_id = {scheduled_task.id: scheduled_task}
            sources = [scheduled_task]

            merged_tasks = ScheduledTaskService.merge_scheduled_tasks(
                scheduled_tasks_by_id, sources  # type: ignore
            )

            assert len(merged_tasks) == 1
            assert merged_tasks[scheduled_task.id].name.task_name == "タスク1"

        def test_既存の実績タスクが存在しない場合は新たに追加されること(self):
            scheduled_task = Mock()
            scheduled_task.id = NotionId("scheduled_id_1")
            scheduled_task.name.task_name = "タスク1"
            scheduled_tasks_by_id = {}
            sources = [scheduled_task]

            merged_tasks = ScheduledTaskService.merge_scheduled_tasks(
                scheduled_tasks_by_id, sources  # type: ignore
            )

            assert len(merged_tasks) == 1
            assert merged_tasks[scheduled_task.id].name.task_name == "タスク1"
