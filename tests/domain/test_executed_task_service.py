from unittest.mock import Mock

from notiontaskr.domain.executed_task_service import ExecutedTaskService


class TestExecutedTaskService:
    class Test_add_id_tag:
        def test_予定タスクと同じ名前を持つ実績タスクが存在する場合IDを付与すること(
            self,
        ):
            executed_task = Mock()
            executed_task.name.id_label = None
            executed_task.name.task_name = "タスク1"
            scheduled_task = Mock()
            scheduled_task.name.task_name = "タスク1"
            scheduled_task.name.id_label = "ID1"
            scheduled_task.id = "scheduled_id_1"
            to = [executed_task]
            source = [scheduled_task]

            ExecutedTaskService.add_id_tag(to, source)  # type: ignore

            # `IDを付与するメソッド`と`予定タスクIDを更新するメソッド`が呼び出されることを確認
            executed_task.update_id_label.assert_called_once_with("ID1")
            executed_task.update_scheduled_task_id.assert_called_once_with(
                "scheduled_id_1"
            )

        def test_実績タスクに既にIDが付与されている場合はスキップされること(self):
            executed_task = Mock()
            executed_task.name.id_label = "既存のID"
            scheduled_task = Mock()
            to = [executed_task]
            source = [scheduled_task]

            ExecutedTaskService.add_id_tag(to, source)  # type: ignore

            # 内部のメソッドが呼び出されないことを確認
            executed_task.update_id_label.assert_not_called()
            executed_task.update_scheduled_task_id.assert_not_called()

        class Test_get_tasks_add_id_tag:
            def test_予定タスクと同じ名前を持つ実績タスクが存在する場合IDを付与すること(
                self,
            ):
                executed_task = Mock()
                executed_task.name.id_label = None
                executed_task.name.task_name = "タスク1"
                scheduled_task = Mock()
                scheduled_task.name.task_name = "タスク1"
                scheduled_task.name.id_label = "ID1"
                scheduled_task.id = "scheduled_id_1"
                to = [executed_task]
                source = [scheduled_task]

                _ = ExecutedTaskService.get_tasks_add_id_tag(to, source)  # type: ignore
                # `IDを付与するメソッド`と`予定タスクIDを更新するメソッド`が呼び出されることを確認
                executed_task.update_id_label.assert_called_once_with("ID1")
                executed_task.update_scheduled_task_id.assert_called_once_with(
                    "scheduled_id_1"
                )

            def test_新たにIDが付与された予定タスクのみを返却すること(self):
                executed_task = Mock()
                executed_task.name.id_label = None
                executed_task.name.task_name = "タスク1"
                scheduled_task = Mock()
                scheduled_task.name.task_name = "タスク1"
                scheduled_task.name.id_label = "ID1"
                scheduled_task.id = "scheduled_id_1"
                to = [executed_task]
                source = [scheduled_task]

                updated_tasks = ExecutedTaskService.get_tasks_add_id_tag(to, source)  # type: ignore

                assert scheduled_task.id == updated_tasks[0].id

            def test_実績タスクに既にIDが付与されている場合はスキップされること(self):
                executed_task = Mock()
                executed_task.name.id_label = "既存のID"
                scheduled_task = Mock()
                to = [executed_task]
                source = [scheduled_task]

                updated_tasks = ExecutedTaskService.get_tasks_add_id_tag(to, source)  # type: ignore
                # 内部のメソッドが呼び出されないことを確認
                executed_task.update_id_label.assert_not_called()
                executed_task.update_scheduled_task_id.assert_not_called()

            def test_新たにIDが付与された予定タスクがない場合は空のリストを返すこと(
                self,
            ):
                executed_task = Mock()
                executed_task.name.id_label = "既存のID"
                scheduled_task = Mock()
                scheduled_task.name.task_name = "タスク1"
                scheduled_task.name.id_label = "ID1"
                scheduled_task.id = "scheduled_id_1"
                to = [executed_task]
                source = [scheduled_task]

                updated_tasks = ExecutedTaskService.get_tasks_add_id_tag(to, source)  # type: ignore
                # 新たにIDが付与された予定タスクがない場合は空のリストを返すことを確認
                assert updated_tasks == []
