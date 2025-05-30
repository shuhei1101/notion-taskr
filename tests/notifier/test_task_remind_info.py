import datetime

from notiontaskr.notifier.task_remind_info import TaskRemindInfo


class TestTaskRemindInfo:
    def test_正常な値で初期化できること(self):
        remind_info = TaskRemindInfo.from_raw_values(
            # 開始前通知
            has_before_start=True,
            # 開始前通知の時間
            raw_before_start_minutes=5,
            # 開始後通知
            has_before_end=True,
            # 開始後通知の時間
            raw_before_end_minutes=10,
        )

        assert remind_info.has_before_start is True
        assert remind_info.before_start_minutes == datetime.timedelta(minutes=5)
        assert remind_info.has_before_end is True
        assert remind_info.before_end_minutes == datetime.timedelta(minutes=10)

    def test_デフォルト値で初期化できること(self):
        remind_info = TaskRemindInfo()

        assert remind_info.has_before_start is False
        assert remind_info.before_start_minutes == datetime.timedelta(minutes=5)
        assert remind_info.has_before_end is False
        assert remind_info.before_end_minutes == datetime.timedelta(minutes=5)

    def test_start_minutesを設定しない場合のデフォルト値が適用されること(self):
        remind_info = TaskRemindInfo.from_raw_values(
            has_before_start=True,
            has_before_end=True,
        )

        # 5分が設定されていること
        assert remind_info.before_start_minutes == datetime.timedelta(minutes=5)
        assert remind_info.before_end_minutes == datetime.timedelta(minutes=5)
