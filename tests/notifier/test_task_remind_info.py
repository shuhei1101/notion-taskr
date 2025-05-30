import datetime

from notiontaskr.domain.value_objects.notion_date import NotionDate
from notiontaskr.notifier.task_remind_info import TaskRemindInfo


class TestTaskRemindInfo:
    def test_正常な値で初期化できること(self):
        remind_info = TaskRemindInfo.from_raw_values(
            task_date=NotionDate(
                start=datetime.datetime(2023, 10, 1, 10, 0),
                end=datetime.datetime(2023, 10, 1, 12, 0),
            ),
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
        assert remind_info.before_start_dt == datetime.datetime(
            2023, 10, 1, 9, 55, tzinfo=datetime.timezone.utc
        )
        assert remind_info.before_end_dt == datetime.datetime(
            2023, 10, 1, 11, 50, tzinfo=datetime.timezone.utc
        )

    def test_デフォルト値で初期化できること(self):
        remind_info = TaskRemindInfo()

        assert remind_info.has_before_start is False
        assert remind_info.before_start_minutes == datetime.timedelta(minutes=5)
        assert remind_info.has_before_end is False
        assert remind_info.before_end_minutes == datetime.timedelta(minutes=5)

    def test_start_minutesを設定しない場合のデフォルト値が適用されること(self):
        remind_info = TaskRemindInfo.from_raw_values(
            task_date=NotionDate(
                start=datetime.datetime(2023, 10, 1, 10, 0),
                end=datetime.datetime(2023, 10, 1, 12, 0),
            ),
            has_before_start=True,
            has_before_end=True,
        )

        # 5分が設定されていること
        assert remind_info.before_start_minutes == datetime.timedelta(minutes=5)
        assert remind_info.before_end_minutes == datetime.timedelta(minutes=5)

    class Test_リマインド時刻が現在か判定する:
        def test_開始前リマインド時刻が現在のときTrueを返す(self):
            remind_info = TaskRemindInfo(
                before_start_dt=datetime.datetime.now(datetime.timezone.utc),
                before_end_dt=None,
            )
            assert remind_info.is_remind_time_before_start()

        def test_開始前リマインド時刻が現在でないときFalseを返す(self):
            remind_info = TaskRemindInfo(
                before_start_dt=datetime.datetime.now(datetime.timezone.utc)
                + datetime.timedelta(minutes=1),
                before_end_dt=None,
            )
            assert not remind_info.is_remind_time_before_start()

        def test_終了前リマインド時刻が現在のときTrueを返す(self):
            remind_info = TaskRemindInfo(
                before_start_dt=None,
                before_end_dt=datetime.datetime.now(datetime.timezone.utc),
            )
            assert remind_info.is_remind_time_before_end()

        def test_終了前リマインド時刻が現在でないときFalseを返す(self):
            remind_info = TaskRemindInfo(
                before_start_dt=None,
                before_end_dt=datetime.datetime.now(datetime.timezone.utc)
                + datetime.timedelta(minutes=1),
            )
            assert not remind_info.is_remind_time_before_end()

    class Test_空で初期化:
        def test_空のリマインド情報を生成できること(self):
            remind_info = TaskRemindInfo.from_empty()

            assert remind_info.has_before_start is False
            assert remind_info.has_before_end is False
            assert remind_info.before_start_minutes == datetime.timedelta(minutes=5)
            assert remind_info.before_end_minutes == datetime.timedelta(minutes=5)
            assert remind_info.before_start_dt is None
            assert remind_info.before_end_dt is None
