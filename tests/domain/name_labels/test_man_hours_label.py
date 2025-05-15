from unittest.mock import Mock
import emoji
import pytest
from notiontaskr.domain.name_labels.label_registerable import LabelRegisterable
from notiontaskr.domain.name_labels.man_hours_label import ManHoursLabel
from notiontaskr.domain.value_objects.man_hours import ManHours


class TestManHoursLabel:
    class Test_from_man_hoursメソッド:
        def test_引数ManHoursの値がどちらも整数で初期化できること(self):

            label = ManHoursLabel.from_man_hours(
                scheduled_man_hours=ManHours(2),
                executed_man_hours=ManHours(1),
            )

            assert label.key == emoji.emojize(":stopwatch:")
            assert label.value == "1/2"

        def test_引数ManHoursの値がどちらも小数で初期化できること(self):

            label = ManHoursLabel.from_man_hours(
                scheduled_man_hours=ManHours(2.5),
                executed_man_hours=ManHours(1.5),
            )

            assert label.key == emoji.emojize(":stopwatch:")
            assert label.value == "1.5/2.5"

        def test_引数ManHoursの値が少数0で終わる場合に少数0が省略されること(self):

            label = ManHoursLabel.from_man_hours(
                scheduled_man_hours=ManHours(2.0),
                executed_man_hours=ManHours(1.0),
            )

            assert label.key == emoji.emojize(":stopwatch:")
            assert label.value == "1/2"

    class Test_parse_and_registerメソッド:
        def test_引数keyが工数の絵文字のときdelegateに値が登録されること(self):
            key = emoji.emojize(":stopwatch:")
            value = "1/2"
            mock_delegate = Mock(spec=LabelRegisterable)

            ManHoursLabel.parse_and_register(key, value, mock_delegate)

            mock_delegate.register_man_hours_label.assert_called_once()  # register_man_hours_labelが1回呼ばれること
            registered_label = mock_delegate.register_man_hours_label.call_args[0][0]
            assert registered_label.key == emoji.emojize(":stopwatch:")
            assert registered_label.value == "1/2"

        def test_引数keyが工数の絵文字でないときValueErrorが発生すること(self):
            key = "1"
            value = "2"
            mock_delegate = Mock(spec=LabelRegisterable)

            with pytest.raises(ValueError):
                ManHoursLabel.parse_and_register(key, value, mock_delegate)

        def test_引数keyが工数の絵文字でないときdelegateに値が登録されないこと(self):
            key = "1"
            value = "2"
            mock_delegate = Mock(spec=LabelRegisterable)

            with pytest.raises(ValueError):
                ManHoursLabel.parse_and_register(key, value, mock_delegate)

            mock_delegate.register_man_hours_label.assert_not_called()  # register_man_hours_labelが呼ばれないこと

    class Test_eqメソッド:
        def test_同じ値のインスタンスは等しいこと(self):
            label1 = ManHoursLabel(key="1", value="2")
            label2 = ManHoursLabel(key="1", value="2")

            assert label1 == label2

        def test_異なる値のインスタンスは等しくないこと(self):
            label1 = ManHoursLabel(key="1", value="2")
            label2 = ManHoursLabel(key="3", value="4")

            assert label1 != label2

        def test_異なるクラスのインスタンスは等しくないこと(self):
            label1 = ManHoursLabel(key="1", value="2")
            label2 = Mock()

            label2.key = "1"
            label2.value = "2"
            assert label1 != label2
