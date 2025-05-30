from datetime import datetime
from notiontaskr.notifier.remind_datetime import RemindDateTime


class TestRemindDateTime:
    def test_datetimeの値で初期化できること(self):
        remind_dt = RemindDateTime(
            before_start=datetime(2023, 10, 1, 12, 0, 0),
            before_end=datetime(2023, 10, 1, 14, 0, 0),
        )

    def test_datetimeの値がNoneで初期化できること(self):
        remind_dt = RemindDateTime()
        assert remind_dt.before_start is None
        assert remind_dt.before_end is None
