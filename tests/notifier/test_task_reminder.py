import asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, Mock
from pytest import fixture
import pytest

from notiontaskr.domain.task import Task
from notiontaskr.domain.tasks import Tasks
from notiontaskr.domain.value_objects.notion_date import NotionDate
from notiontaskr.notifier.notifiable import Notifiable
from notiontaskr.notifier.remind_minutes import RemindMinutes
from notiontaskr.notifier.task_remind_info import TaskRemindInfo
from notiontaskr.notifier.task_reminder import TaskReminder


class TestTaskReminder:
    """TaskReminderクラスでは、Taskクラスのリマインドを行うドメインサービスです

    このクラスでは、Notifiableインターフェースを準拠したクラスを利用し、
    タスクのリマインドを行います。
    """

    @fixture
    def mock_notifier(self) -> Notifiable:
        """Notifiableインターフェースをモックしたクラス"""

        class NotifiableMock(Notifiable):
            async def notify(self, message: str):
                pass

        return NotifiableMock()

    def test_コンストラクタでNotifiableを受け取ること(self, mock_notifier):
        task_reminder = TaskReminder(notifier=mock_notifier)

        assert task_reminder is not None

    class Test_リマインドを実行:
        @fixture
        def mock_tasks(self):
            mock_tasks = Mock()
            remind_info = TaskRemindInfo(
                before_start_minutes=RemindMinutes(30),
                before_end_minutes=RemindMinutes(30),
            )
            mock_task = Mock(remind_info=remind_info)

            mock_tasks.get_remind_tasks = Mock(
                return_value=[
                    mock_task,
                    mock_task,
                ]
            )

            return mock_tasks

        def test_タスクが開始前リマインド時刻のときリマインドを送ること(
            self, mock_notifier: Notifiable, mock_tasks: Tasks
        ):
            mock_notifier.notify = AsyncMock()
            reminder = TaskReminder(notifier=mock_notifier)
            reminder.is_remind_time_before_start = Mock(return_value=True)
            asyncio.run(reminder.remind(mock_tasks, on_success=Mock(), on_error=Mock()))
            mock_notifier.notify.assert_called()

        def test_タスクが終了前リマインド時刻のときリマインドを送ること(
            self, mock_notifier: Notifiable, mock_tasks: Tasks
        ):
            mock_notifier.notify = AsyncMock()
            reminder = TaskReminder(notifier=mock_notifier)
            reminder.is_remind_time_before_end = Mock(return_value=True)
            asyncio.run(reminder.remind(mock_tasks, on_success=Mock(), on_error=Mock()))
            mock_notifier.notify.assert_called()

        def test_タスクがリマインド時刻でないとき例外を送ること(
            self, mock_notifier: Notifiable, mock_tasks: Tasks
        ):
            mock_notifier.notify = AsyncMock()
            reminder = TaskReminder(notifier=mock_notifier)
            reminder.is_remind_time_before_start = Mock(return_value=False)
            reminder.is_remind_time_before_end = Mock(return_value=False)

            on_error = Mock()
            asyncio.run(reminder.remind(mock_tasks, on_error=on_error))

            on_error.assert_called()

    class Test_リマインド時刻を取得:
        def test_開始前リマインド日時を取得すること(self):
            task = Task(
                page_id=Mock(),
                name=Mock(),
                tags=Mock(),
                id=Mock(),
                status=Mock(),
                remind_info=Mock(
                    has_before_start=True,
                    before_start_minutes=timedelta(minutes=30),
                ),
            )
            task.date = NotionDate(start=datetime(2023, 10, 1, 12, 0), end=None)
            assert TaskReminder.get_before_start_dt(task) == datetime(
                2023, 10, 1, 11, 30, tzinfo=timezone.utc
            )

        def test_終了前リマインド日時を取得すること(self):
            task = Task(
                page_id=Mock(),
                name=Mock(),
                tags=Mock(),
                id=Mock(),
                status=Mock(),
                remind_info=Mock(
                    has_before_end=True,
                    before_end_minutes=timedelta(minutes=30),
                ),
            )
            task.date = NotionDate(
                start=datetime(2023, 10, 1, 12, 0), end=datetime(2023, 10, 1, 12, 0)
            )
            assert TaskReminder.get_before_end_dt(task) == datetime(
                2023, 10, 1, 11, 30, tzinfo=timezone.utc
            )

    class Test_リマインド時刻の判定:
        def test_開始前リマインド時刻が現在のときTrueを返す(self):
            task = Task(
                page_id=Mock(),
                name=Mock(),
                tags=Mock(),
                id=Mock(),
                status=Mock(),
                remind_info=TaskRemindInfo(
                    has_before_start=True,
                    before_start_minutes=RemindMinutes(minutes=0),
                ),
            )
            task.date = NotionDate(start=datetime.now(timezone.utc), end=None)

            assert TaskReminder.is_remind_time_before_start(task) is True

        def test_終了前リマインド時刻が現在のときTrueを返す(self):
            task = Task(
                page_id=Mock(),
                name=Mock(),
                tags=Mock(),
                id=Mock(),
                status=Mock(),
                remind_info=TaskRemindInfo(
                    has_before_end=True,
                    before_end_minutes=RemindMinutes(minutes=0),
                ),
            )
            task.date = NotionDate(
                start=datetime.now(timezone.utc), end=datetime.now(timezone.utc)
            )

            assert TaskReminder.is_remind_time_before_end(task) is True
