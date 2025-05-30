from datetime import datetime, timedelta
from unittest.mock import Mock
from pytest import fixture

from notiontaskr.domain.executed_task import ExecutedTask
from notiontaskr.domain.task import Task
from notiontaskr.notifier.notifiable import Notifiable
from notiontaskr.notifier.remind_datetime import RemindDateTime
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
            def notify(self, message: str):
                pass

        return NotifiableMock()

    @fixture
    def mock_executed_task(self) -> ExecutedTask:
        return ExecutedTask(
            page_id=Mock(),
            name=Mock(),
            tags=Mock(),
            id=Mock(),
            status=Mock(),
            remind_info=TaskRemindInfo(),
        )

    def test_コンストラクタでNotifiableを受け取ること(self, mock_notifier):

        task_reminder = TaskReminder(notifier=mock_notifier)

        assert task_reminder is not None

    class Test_Remind:
        def test_開始前通知がある場合に現在時刻と比較して通知すること(
            self, mock_notifier: Notifiable, mock_executed_task: Task
        ):
            task_reminder = TaskReminder(notifier=mock_notifier)

            # モックの現在時刻を設定
            mock_executed_task.remind_info = TaskRemindInfo.from_raw_values(
                has_before_start=True,
                before_start_minutes=30,  # 30分前に通知
            )

            mock_executed_task.get_remind_dt = Mock(
                return_value=RemindDateTime(
                    before_start=datetime.now(),  # 現在時刻
                    before_end=None,  # 終了後の通知はなし
                )
            )

            # notifyメソッドをモック化
            mock_notifier.notify = Mock()

            # リマインドを実行
            task_reminder.remind(mock_executed_task)

            # モックのnotifyメソッドが呼び出されたことを確認
            mock_notifier.notify.assert_called()
