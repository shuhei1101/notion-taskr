from unittest.mock import Mock

import pytest
from notiontaskr.domain.name_labels.label_registerable import LabelRegisterable
from notiontaskr.domain.name_labels.parent_id_label import ParentIdLabel
from notiontaskr.domain.value_objects.notion_id import NotionId


class TestParentIdLabel:
    class Test_from_propertyメソッド:
        def test_引数parent_idの値がNotionId型で初期化できること(self):
            parent_id = NotionId("123")
            label = ParentIdLabel.from_property(parent_id)

            assert label.key == "親"
            assert label.value == "123"

    class Test_parse_and_registerメソッド:
        def test_引数keyが親のときdelegateに値が登録されること(self):
            key = "親"
            value = "123"
            mock_delegate = Mock(spec=LabelRegisterable)

            ParentIdLabel.parse_and_register(key, value, mock_delegate)

            mock_delegate.register_parent_id_label.assert_called_once()
            registered_label = mock_delegate.register_parent_id_label.call_args[0][0]
            assert registered_label.key == "親"
            assert registered_label.value == "123"

        def test_引数keyが親でないときValueErrorが発生すること(self):
            key = "1"
            value = "2"
            mock_delegate = Mock(spec=LabelRegisterable)

            with pytest.raises(ValueError):
                ParentIdLabel.parse_and_register(key, value, mock_delegate)

        def test_引数keyが親でないときdelegateに値が登録されないこと(self):
            key = "1"
            value = "2"
            mock_delegate = Mock(spec=LabelRegisterable)

            with pytest.raises(ValueError):
                ParentIdLabel.parse_and_register(key, value, mock_delegate)

            mock_delegate.register_parent_id_label.assert_not_called()

    class Test_eqメソッド:
        def test_引数が異なる型のときNotImplementedを返すこと(self):
            label = ParentIdLabel(key="親", value="123")
            assert label.__eq__(1) is NotImplemented

        def test_引数が同じ型でvalueが同じときTrueを返すこと(self):
            label1 = ParentIdLabel(key="親", value="123")
            label2 = ParentIdLabel(key="親", value="123")
            assert label1 == label2

        def test_引数が同じ型でvalueが異なるときFalseを返すこと(self):
            label1 = ParentIdLabel(key="親", value="123")
            label2 = ParentIdLabel(key="親", value="456")
            assert not label1 == label2
