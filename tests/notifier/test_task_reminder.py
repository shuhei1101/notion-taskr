import asyncio
from unittest.mock import AsyncMock, Mock
from pytest import fixture
import pytest

from notiontaskr.notifier.notifiable import Notifiable
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
        def test_タスクが開始前リマインド時刻のときリマインドを送ること(
            self, mock_notifier: Notifiable
        ):
            task = Mock(is_remind_time_before_start=Mock(return_value=True))
            mock_notifier.notify = AsyncMock()
            reminder = TaskReminder(notifier=mock_notifier)
            asyncio.run(reminder.remind(task))
            mock_notifier.notify.assert_called()

        def test_タスクが終了前リマインド時刻のときリマインドを送ること(
            self, mock_notifier: Notifiable
        ):
            task = Mock(is_remind_time_before_end=Mock(return_value=True))
            mock_notifier.notify = AsyncMock()
            reminder = TaskReminder(notifier=mock_notifier)
            asyncio.run(reminder.remind(task))
            mock_notifier.notify.assert_called()

        def test_タスクがリマインド時刻でないとき例外を送ること(
            self, mock_notifier: Notifiable
        ):
            task = Mock(
                is_remind_time_before_start=Mock(return_value=False),
                is_remind_time_before_end=Mock(return_value=False),
            )
            mock_notifier.notify = AsyncMock()
            reminder = TaskReminder(notifier=mock_notifier)

            with pytest.raises(ValueError):
                asyncio.run(reminder.remind(task))
