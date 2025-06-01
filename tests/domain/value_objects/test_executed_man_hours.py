import pytest
from notiontaskr.domain.value_objects.man_hours import ManHours
from notiontaskr.domain.value_objects.executed_man_hours import ExecutedManHours


class TestExecutedManHours:
    def test_ManHoursクラスを継承していること(self):
        assert issubclass(ExecutedManHours, ManHours)

    class Test_response_dataからのインスタンス生成:
        """例:

        data["properties"]["人時(実)"]["number"]
        """

        def test_レスポンスデータからインスタンスを生成できること(self):
            response_data = {"properties": {"人時(実)": {"number": 5.0}}}

            executed_man_hours = ExecutedManHours.from_response_data(response_data)
            assert executed_man_hours.value == 5.0

        def test_レスポンスデータに人時_実_がない場合はValueErrorを発生させること(self):
            response_data = {"properties": {}}
            with pytest.raises(ValueError):
                ExecutedManHours.from_response_data(response_data)
