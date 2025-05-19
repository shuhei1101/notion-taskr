from unittest.mock import Mock

from notiontaskr.domain.task import Task
import pytest


class TestTask:
    @pytest.fixture
    def empty_task(self):
        return Task(
            page_id=Mock(),
            name=Mock(),
            tags=Mock(),
            id=Mock(),
            status=Mock(),
        )

    class Test___init__:

        def test_どんな値でも例外が発生せず初期化可能なこと(self):
            task = Task(
                page_id=Mock(),
                name=Mock(),
                tags=Mock(),
                id=Mock(),
                status=Mock(),
            )
            assert task.page_id is not None
            assert task.name is not None
            assert task.tags is not None
            assert task.id is not None
            assert task.status is not None

    class Test__toggle_is_updated:
        def test_実行するとis_updatedがTrueになること(self, empty_task: Task):
            empty_task.is_updated = False
            empty_task._toggle_is_updated("test")
            assert empty_task.is_updated is True

    class Test_update_man_hours_label:
        def test_工数ラベルが異なる場合にis_updatedがTrueになること(
            self, empty_task: Task
        ):
            empty_task.name.man_hours_label = Mock(__eq__=Mock(return_value=False))
            mock_man_hours_label = Mock()
            empty_task._toggle_is_updated = Mock()

            empty_task.update_man_hours_label(mock_man_hours_label)

            empty_task._toggle_is_updated.assert_called_once()

    class Test_update_id_label:
        def test_工数ラベルが異なる場合にis_updatedがTrueになること(
            self, empty_task: Task
        ):
            empty_task.name.id_label = Mock(__eq__=Mock(return_value=False))
            mock_id_label = Mock()
            empty_task._toggle_is_updated = Mock()

            empty_task.update_id_label(mock_id_label)

            empty_task._toggle_is_updated.assert_called_once()

    class Test_update_parent_id_label:
        def test_工数ラベルが異なる場合にis_updatedがTrueになること(
            self, empty_task: Task
        ):
            empty_task.name.parent_id_label = Mock(__eq__=Mock(return_value=False))
            mock_parent_id_label = Mock()
            empty_task._toggle_is_updated = Mock()

            empty_task.update_parent_id_label(mock_parent_id_label)

            empty_task._toggle_is_updated.assert_called_once()

    class Test_update_name:
        def test_工数ラベルが異なる場合にis_updatedがTrueになること(
            self, empty_task: Task
        ):
            empty_task.name = Mock(__eq__=Mock(return_value=False))
            mock_name = Mock()
            empty_task._toggle_is_updated = Mock()

            empty_task.update_name(mock_name)

            empty_task._toggle_is_updated.assert_called_once()

    class Test_update_parent_task_page_id:
        def test_工数ラベルが異なる場合にis_updatedがTrueになること(
            self, empty_task: Task
        ):
            empty_task.parent_task_page_id = Mock(__eq__=Mock(return_value=False))
            mock_parent_task_page_id = Mock()
            empty_task._toggle_is_updated = Mock()

            empty_task.update_parent_task_page_id(mock_parent_task_page_id)

            empty_task._toggle_is_updated.assert_called_once()

    class Test_update_scheduled_task_page_id:
        def test_工数ラベルが異なる場合にis_updatedがTrueになること(
            self, empty_task: Task
        ):
            empty_task.scheduled_task_page_id = Mock(__eq__=Mock(return_value=False))
            mock_scheduled_task_page_id = Mock()
            empty_task._toggle_is_updated = Mock()

            empty_task.update_scheduled_task_page_id(mock_scheduled_task_page_id)

            empty_task._toggle_is_updated.assert_called_once()

    class Test_update_status:
        def test_工数ラベルが異なる場合にis_updatedがTrueになること(
            self, empty_task: Task
        ):
            empty_task.status = Mock(__eq__=Mock(return_value=False))
            mock_status = Mock()
            empty_task._toggle_is_updated = Mock()

            empty_task.update_status(mock_status)

            empty_task._toggle_is_updated.assert_called_once()

    class Test_get_display_name:
        def test_タスク名を取得すること(self, empty_task: Task):
            empty_task.name = Mock(__str__=Mock(return_value="タスク名"))
            assert empty_task.get_display_name() == "タスク名"
