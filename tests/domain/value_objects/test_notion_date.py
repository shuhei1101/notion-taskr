from datetime import datetime

import pytest
from notiontaskr.domain.value_objects.notion_date import NotionDate


class TestNotionDate:
    class Test_initメソッド:
        def test_引数dateがdatetimeのとき正常に初期化されること(self):
            date = NotionDate(datetime(2023, 1, 1), datetime(2023, 1, 2))
            assert date.start == datetime(2023, 1, 1)
            assert date.end == datetime(2023, 1, 2)

        def test_引数startがNoneのときTypeErrorが発生すること(self):
            with pytest.raises(TypeError):
                NotionDate(None, datetime(2023, 1, 2))  # type: ignore

        def test_引数endがNoneのときendにstartが代入されること(self):
            date = NotionDate(datetime(2023, 1, 1), None)  # type: ignore
            assert date.start == datetime(2023, 1, 1)
            assert date.end == datetime(2023, 1, 1)

        def test_引数startがendよりも後のときValueErrorが発生すること(self):
            with pytest.raises(ValueError):
                NotionDate(datetime(2023, 1, 2), datetime(2023, 1, 1))
