from datetime import datetime

from notiontaskr.util.calculator import get_hours_diff


class Test_get_hours_diff:
    def test_日付の差分を計算できること(self):
        start_date = datetime(2023, 10, 1, 12, 0, 0)
        end_date = datetime(2023, 10, 2, 12, 0, 0)
        result = get_hours_diff(start_date, end_date)
        assert result == 24.0
