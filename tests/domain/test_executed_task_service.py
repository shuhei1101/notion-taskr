from unittest.mock import Mock

from notiontaskr.domain.executed_task_service import ExecutedTaskService


class TestExecutedTaskService:
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

    class Test_get_total_man_hours:
        def test_実績タスクの工数を合計できること(self):
            from notiontaskr.domain.value_objects.man_hours import ManHours

            executed_task1 = Mock(man_hours=ManHours(5))
            executed_tasks = [executed_task1]
            result = ExecutedTaskService.get_total_man_hours(executed_tasks)  # type: ignore
            # 実績タスクの工数を合計できることを確認
            assert result == 5.0
