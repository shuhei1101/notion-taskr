from datetime import datetime

from notiontaskr.util.calculator import get_hours_diff

class TestCalculator():
    def test_get_hours_diff(self):
        start_date = datetime(2020, 1, 1, 0, 0, 0)
        end_date = datetime(2020, 1, 1, 1, 0, 0)
        assert get_hours_diff(start_date, end_date) == 1.0

    def test_get_hours_diff_when_same_date(self):
        start_date = datetime(2020, 1, 1, 0, 0, 0)
        end_date = datetime(2020, 1, 1, 0, 30, 0)
        assert get_hours_diff(start_date, end_date) == 0.5

    def test_get_hours_diff_when_start_date_is_future(self):
        start_date = datetime(2020, 1, 2, 0, 0, 0)
        end_date = datetime(2020, 1, 1, 0, 0, 0)
        assert get_hours_diff(start_date, end_date) == -24.0
