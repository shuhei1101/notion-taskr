from unittest.mock import Mock

from notiontaskr.domain.task_service import TaskService


class TestTaskService:
    class Test_get_tasks_add_id_tag:
        def test_変更されたタスクのみを返すこと(self):
            task = Mock(is_updated=True)
            task2 = Mock(is_updated=True)
            task3 = Mock(is_updated=False)
            tasks = [task, task2, task3]
            updated_tasks = TaskService.get_updated_tasks(tasks)
            assert len(updated_tasks) == 2

    class Test_upsert_tasks:
        def test_タスクが存在する場合は上書きされること(self):
            task = Mock(id="task_id")
            task2 = Mock(id="task_id")
            tasks = [task]
            TaskService.upsert_tasks(tasks, task2)
            assert len(tasks) == 1
            assert tasks[0] == task2

        def test_タスクが存在しない場合は追加されること(self):
            task = Mock(id="task_id")
            tasks = []
            TaskService.upsert_tasks(tasks, task)
            assert len(tasks) == 1
            assert tasks[0] == task
