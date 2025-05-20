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

    class Test_指定タグ配列別に実績タスクを辞書型に振り分ける:
        def test_予定タスク配列とタグ配列を渡し指定タグに一致する予定タスクを辞書型で取得できること(
            self,
        ):
            executed_tasks = [
                Mock(
                    tags=["tag1", "tag2"],
                ),
                Mock(
                    tags=["tag3", "tag4"],
                ),
                Mock(
                    tags=["tag4"],
                ),
            ]
            target_tags = ["tag1", "tag3"]
            expected_result = {
                "tag1": executed_tasks[0],
                "tag3": executed_tasks[1],
            }
            result = ExecutedTaskService.get_executed_tasks_by_tag(
                executed_tasks=executed_tasks, tags=target_tags  # type: ignore
            )
            # 指定したタグに一致する予定タスクを取得できること
            assert result["tag1"] == expected_result["tag1"]
            assert result["tag3"] == expected_result["tag3"]
            assert len(result) == len(expected_result)
