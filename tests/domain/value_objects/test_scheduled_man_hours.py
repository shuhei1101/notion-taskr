import pytest
from notiontaskr.domain.value_objects.man_hours import ManHours
from notiontaskr.domain.value_objects.scheduled_man_hours import ScheduledManHours


class TestScheduledManHours:
    def test_ManHoursクラスを継承していること(self):
        assert issubclass(ScheduledManHours, ManHours)

    class Test_response_dataからのインスタンス生成:
        """例:

        data["properties"]["人時(予)"]["number"]
        """

        def test_レスポンスデータからインスタンスを生成できること(self):
            response_data = {"properties": {"人時(予)": {"number": 5.0}}}

            scheduled_man_hours = ScheduledManHours.from_response_data(response_data)
            assert scheduled_man_hours.value == 5.0

        def test_レスポンスデータに人時_予_がない場合はValueErrorを発生させること(self):
            response_data = {"properties": {}}
            with pytest.raises(ValueError):
                ScheduledManHours.from_response_data(response_data)
