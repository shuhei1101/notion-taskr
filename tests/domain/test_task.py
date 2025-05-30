from datetime import datetime, timezone
from unittest.mock import Mock

from notiontaskr.domain.task import Task
import pytest

from notiontaskr.domain.value_objects.notion_date import NotionDate
from notiontaskr.notifier.remind_datetime import RemindDateTime
from notiontaskr.notifier.task_remind_info import TaskRemindInfo


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

    class Test_コンストラクタ:

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

    class Test_Remind関連:
        def test_リマインド開始時刻を計算できること(self, empty_task: Task):
            empty_task.remind_info = TaskRemindInfo.from_raw_values(
                has_before_start=True,
                has_before_end=False,
                before_start_minutes=30,
                before_end_minutes=None,
            )
            empty_task.date = NotionDate(
                start=datetime(2023, 10, 1, 9, 30),
                end=None,
            )
            remind_dt = empty_task.get_remind_dt()
            if remind_dt is None:
                raise AssertionError("RemindDateTime should not be None")
            assert remind_dt.before_start == datetime(
                2023, 10, 1, 9, 0, tzinfo=timezone.utc
            )

        def test_リマインド終了時刻を計算できること(self, empty_task: Task):
            empty_task.remind_info = TaskRemindInfo.from_raw_values(
                has_before_start=False,
                has_before_end=True,
                before_start_minutes=None,
                before_end_minutes=30,
            )
            empty_task.date = NotionDate(
                start=datetime(2023, 10, 1, 9, 30),
                end=datetime(2023, 10, 1, 10, 30),
            )
            remind_dt = empty_task.get_remind_dt()
            if remind_dt is None:
                raise AssertionError("RemindDateTime should not be None")
            assert remind_dt.before_end == datetime(
                2023, 10, 1, 10, 0, tzinfo=timezone.utc
            )

        def test_リマインド日時がNoneの場合はNoneを返すこと(self, empty_task: Task):
            empty_task.remind_info = TaskRemindInfo.from_raw_values(
                has_before_start=False,
                has_before_end=False,
                before_start_minutes=None,
                before_end_minutes=None,
            )
            empty_task.date = None
            assert empty_task.get_remind_dt() is None

        def test_リマインド日時が開始前と終了後の両方がNoneの場合はNoneを返すこと(
            self, empty_task: Task
        ):
            empty_task.remind_info = TaskRemindInfo.from_raw_values(
                has_before_start=False,
                has_before_end=False,
                before_start_minutes=None,
                before_end_minutes=None,
            )
            empty_task.date = NotionDate(
                start=datetime(2023, 10, 1, 9, 30),
                end=datetime(2023, 10, 1, 10, 30),
            )
            assert empty_task.get_remind_dt() is None
