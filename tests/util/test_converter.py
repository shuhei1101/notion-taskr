from datetime import datetime

from notiontaskr.util.converter import (
    dt_to_month_start_end,
    remove_variant_selectors,
    timedelta_to_minutes,
    to_isoformat,
    truncate_decimal,
)
import pytest


class Test_to_isoformat:
    def test_datetimeをISO8601形式に変換できること(self):
        dt = datetime(2023, 10, 1, 12, 0, 0)
        result = to_isoformat(dt)
        assert result == "2023-10-01T12:00:00.000Z"

    def test_datetime型以外の値を渡すとValueErrorが発生すること(self):
        dt = "2023-10-01"
        with pytest.raises(ValueError):
            to_isoformat(dt)  # type: ignore


class Test_truncate_decimal:
    def test_小数点以下を1桁に切り捨てること(self):
        num = 3.14159
        result = truncate_decimal(num)
        assert result == "3.1"

    def test_float以外の値を渡すとValueErrorが発生すること(self):
        num = "3.14"
        with pytest.raises(ValueError):
            truncate_decimal(num)  # type: ignore


class Test_remove_variant_selectors:
    def test_絵文字のバリアントセレクタを削除すること(self):
        text = "⏲️"
        result = remove_variant_selectors(text)
        assert result == "⏲"


class Test_dt_to_month_start_end:
    def test_引数で年月を指定すると月初と月末を取得できること(self):
        dt = datetime(2023, 10, 1, 12, 0, 0)
        start, end = dt_to_month_start_end(dt)
        assert start == datetime(2023, 10, 1, 0, 0)
        assert end == datetime(2023, 10, 31, 23, 59)

    def test_引数に1日以外を渡しても月初と月末を取得できること(self):
        dt = datetime(2023, 10, 15, 12, 12, 12)
        start, end = dt_to_month_start_end(dt)
        assert start == datetime(2023, 10, 1, 0, 0)
        assert end == datetime(2023, 10, 31, 23, 59)


class Test_timedelta_to_minutes:
    def test_timedeltaを分に変換できること(self):
        td = datetime(2023, 10, 1, 12, 0, 0) - datetime(2023, 10, 1, 11, 30, 0)
        result = timedelta_to_minutes(td)
        assert result == 30

    def test_timedelta以外の値を渡すとValueErrorが発生すること(self):
        td = "30 minutes"
        with pytest.raises(ValueError):
            timedelta_to_minutes(td)  # type: ignore
