import datetime

import pytest

from notiontaskr import config
from notiontaskr.notifier.remind_minutes import RemindMinutes
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

    class Test_notionのresponse_dataからのインスタンス生成:
        """例:
        has_before_start = data["properties"]["開始前通知"]["checkbox"]
        has_before_end = data["properties"]["終了前通知"]["checkbox"]
        before_start_minutes = data["properties"]["開始前通知時間(分)"].get(
            "number"
        )
        before_end_minutes = data["properties"]["終了前通知時間(分)"].get("number")
        remind_info = TaskRemindInfo.from_raw_values(
            has_before_start=has_before_start,
            has_before_end=has_before_end,
            raw_before_start_minutes=before_start_minutes,
            raw_before_end_minutes=before_end_minutes,
        )
        """

        def test_正常な値で初期化できること(self):
            response_data = {
                "properties": {
                    "開始前通知": {"checkbox": True},
                    "終了前通知": {"checkbox": True},
                    "開始前通知時間(分)": {"number": 5},
                    "終了前通知時間(分)": {"number": 10},
                }
            }
            remind_info = TaskRemindInfo.from_response_data(response_data)
            assert remind_info.has_before_start is True
            assert remind_info.before_start_minutes == datetime.timedelta(minutes=5)
            assert remind_info.has_before_end is True
            assert remind_info.before_end_minutes == datetime.timedelta(minutes=10)

        def test_不正なキーがある場合は例外が発生すること(self):
            response_data = {
                "properties": {
                    "開始前通知": {"checkbox": True},
                    "終了前通知": {"checkbox": True},
                    "開始前通知時間(分)": {"number": 5},
                    # "終了前通知時間(分)"キーがない
                }
            }
            with pytest.raises(ValueError):
                TaskRemindInfo.from_response_data(response_data)

    class Test_値が存在するか調べる:
        def test_値が存在する場合はTrueを返す(self):
            remind_info = TaskRemindInfo.from_raw_values(
                has_before_start=True,
                raw_before_start_minutes=5,
                has_before_end=True,
                raw_before_end_minutes=10,
            )
            assert remind_info.has_value() is True

        def test_値が存在しない場合はFalseを返す(self):
            remind_info = TaskRemindInfo.from_empty()
            assert remind_info.has_value() is False

    class Test_デフォルト値で初期化:
        def test_デフォルト値で初期化できること(self):
            info = TaskRemindInfo.from_empty()
            default_info = info.get_default_self()
            assert default_info.has_before_start is False
            assert default_info.before_start_minutes == RemindMinutes(
                minutes=config.DEFAULT_BEFORE_START_MINUTES
            )
            assert default_info.has_before_end is False
            assert default_info.before_end_minutes == RemindMinutes(
                minutes=config.DEFAULT_BEFORE_END_MINUTES
            )
