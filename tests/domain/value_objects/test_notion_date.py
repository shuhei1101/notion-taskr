from datetime import datetime, timezone

import pytest
from notiontaskr.domain.value_objects.notion_date import NotionDate


class TestNotionDate:
    class Test_initメソッド:
        def test_引数dateがdatetimeのとき正常に初期化されること(self):
            date = NotionDate(datetime(2023, 1, 1), datetime(2023, 1, 2))
            assert date.start == datetime(2023, 1, 1, tzinfo=timezone.utc)
            assert date.end == datetime(2023, 1, 2, tzinfo=timezone.utc)

        def test_引数startがNoneのときTypeErrorが発生すること(self):
            with pytest.raises(TypeError):
                NotionDate(None, datetime(2023, 1, 2))  # type: ignore

        def test_引数endがNoneのときendにstartが代入されること(self):
            date = NotionDate(datetime(2023, 1, 1), None)  # type: ignore
            assert date.start == datetime(2023, 1, 1, tzinfo=timezone.utc)
            assert date.end == datetime(2023, 1, 1, tzinfo=timezone.utc)

        def test_引数startがendよりも後のときValueErrorが発生すること(self):
            with pytest.raises(ValueError):
                NotionDate(datetime(2023, 1, 2), datetime(2023, 1, 1))

    class Test_from_raw_dateメソッド:
        def test_引数startがNoneのときValueErrorが発生すること(self):
            with pytest.raises(ValueError):
                NotionDate.from_raw_date(None, "2023-01-02")  # type: ignore

        def test_引数endがNoneのときendにstartが代入されること(self):
            date = NotionDate.from_raw_date("2023-01-01", None)  # type: ignore
            assert date.start == datetime(2023, 1, 1, tzinfo=timezone.utc)
            assert date.end == datetime(2023, 1, 1, tzinfo=timezone.utc)

        def test_引数startがISOフォーマットの文字列のとき正常に初期化されること(self):
            date = NotionDate.from_raw_date("2023-01-01", "2023-01-02")
            assert date.start == datetime(2023, 1, 1, tzinfo=timezone.utc)
            assert date.end == datetime(2023, 1, 2, tzinfo=timezone.utc)

        def test_引数startがISOフォーマットでない文字列のときValueErrorが発生すること(
            self,
        ):
            with pytest.raises(ValueError):
                NotionDate.from_raw_date("2023/01/01", "2023/01/02")
