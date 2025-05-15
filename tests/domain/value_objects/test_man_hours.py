import pytest
from notiontaskr.domain.value_objects.man_hours import ManHours


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
