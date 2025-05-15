import pytest
from notiontaskr.domain.value_objects.man_hours import ManHours
from notiontaskr.domain.value_objects.notion_date import NotionDate
from datetime import datetime


class TestManHours:
    class Test_initメソッド:
        def test_引数valueが0以上のとき正常に初期化されること(self):
            assert ManHours(0).value == 0

        def test_引数valueが負のときValueErrorが発生すること(self):
            with pytest.raises(ValueError):
                ManHours(-1)

        def test_引数valueがNoneのときデフォルト値0で初期化されること(self):
            assert ManHours(None).value == 0  # type: ignore

    class Test_addメソッド:
        def test_引数がManHoursのとき正常に加算されること(self):
            assert ManHours(1) + ManHours(2) == ManHours(3)

        def test_引数がManHoursでないときNotImplementedErrorが発生すること(self):
            with pytest.raises(NotImplementedError):
                ManHours(1) + 1  # type: ignore

    class Test_floatメソッド:
        def test_ManHoursをfloatに変換できること(self):
            assert float(ManHours(1)) == 1.0
            assert float(ManHours(1.5)) == 1.5

    class Test_from_notion_dateメソッド:
        def test_引数がNotionDateのとき正常に初期化されること(self):
            date = NotionDate(datetime(2023, 1, 1), datetime(2023, 1, 2))
            assert ManHours.from_notion_date(date).value == 24.0

    class Test_eqメソッド:
        def test_引数が異なる型のときFalseを返すこと(self):
            assert ManHours(1) != 1
            assert ManHours(1) != "1"

        def test_引数が同じ型でvalueが同じときTrueを返すこと(self):
            assert ManHours(1) == ManHours(1)
            assert ManHours(1.0) == ManHours(1)
