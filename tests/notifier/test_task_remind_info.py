import datetime

from notiontaskr.notifier.task_remind_info import TaskRemindInfo


class TestTaskRemindInfo:
    def test_正常な値で初期化できること(self):
        notification = TaskRemindInfo.from_raw_values(
            # 開始前通知
            has_before_start=True,
            # 開始前通知の時間
            before_start_minutes=5,
            # 開始後通知
            has_after_start=True,
            # 開始後通知の時間
            after_start_minutes=10,
        )

        assert notification.has_before_start is True
        assert notification.before_start_minutes == datetime.timedelta(minutes=5)
        assert notification.has_after_start is True
        assert notification.after_start_minutes == datetime.timedelta(minutes=10)

    def test_デフォルト値で初期化できること(self):
        notification = TaskRemindInfo()

        assert notification.has_before_start is False
        assert notification.before_start_minutes == datetime.timedelta(minutes=5)
        assert notification.has_after_start is False
        assert notification.after_start_minutes == datetime.timedelta(minutes=5)

    def test_start_minutesを設定しない場合のデフォルト値が適用されること(self):
        notification = TaskRemindInfo.from_raw_values(
            has_before_start=True,
            has_after_start=True,
        )

        # 5分が設定されていること
        assert notification.before_start_minutes == datetime.timedelta(minutes=5)
        assert notification.after_start_minutes == datetime.timedelta(minutes=5)
