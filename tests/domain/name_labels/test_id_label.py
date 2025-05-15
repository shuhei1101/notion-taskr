import pytest
from unittest.mock import Mock

from notiontaskr.domain.name_labels.id_label import IdLabel
from notiontaskr.domain.name_labels.label_registerable import LabelRegisterable
from notiontaskr.domain.value_objects.notion_id import NotionId
from notiontaskr.domain.value_objects.status import Status


class TestIdLabel:

    class Test_Taskプロパティから初期化できる:
        def test_from_propertyメソッドに未着手ステータス(self):
            notion_id = NotionId(number="123")
            status = Status.NOT_STARTED

            label = IdLabel.from_property(notion_id, status)

            assert label.key == ""
            assert label.value == "123"

        def test_from_propertyメソッドに完了ステータス(self):
            notion_id = NotionId(number="123")
            status = Status.COMPLETED

            label = IdLabel.from_property(notion_id, status)

            assert label.key == "✓"
            assert label.value == "123"

        def test_from_property_keyメソッドに進行中ステータス(self):
            notion_id = NotionId(number="123")
            status = Status.IN_PROGRESS

            label = IdLabel.from_property(notion_id, status)

            assert label.key == "→"
            assert label.value == "123"

        def test_from_property_keyメソッドに遅延ステータス(self):
            notion_id = NotionId(number="123")
            status = Status.DELAYED

            label = IdLabel.from_property(notion_id, status)

            assert label.key == "!"
            assert label.value == "123"

        def test_from_property_keyメソッドに中止ステータス(self):
            notion_id = NotionId(number="123")
            status = Status.CANCELED

            label = IdLabel.from_property(notion_id, status)

            assert label.key == "×"
            assert label.value == "123"

    class Test_parse_and_registerメソッドのオーバーライド:
        def test_parse_and_registerメソッドに数字のみのラベル(self):
            key = "1"
            value = "23"
            mock_delegate = Mock(spec=LabelRegisterable)

            IdLabel.parse_and_register(key, value, mock_delegate)

            mock_delegate.register_id_label.assert_called_once()
            registered_label = mock_delegate.register_id_label.call_args[0][0]
            assert registered_label.key == ""
            assert registered_label.value == "123"

        def test_parse_and_registerメソッドに進行中シンボル(self):
            key = "→"
            value = "123"
            mock_delegate = Mock(spec=LabelRegisterable)

            IdLabel.parse_and_register(key, value, mock_delegate)

            mock_delegate.register_id_label.assert_called_once()
            registered_label = mock_delegate.register_id_label.call_args[0][0]
            assert registered_label.key == "→"
            assert registered_label.value == "123"

        def test_parse_and_registerメソッドに遅延シンボル(self):
            key = "!"
            value = "123"
            mock_delegate = Mock(spec=LabelRegisterable)

            IdLabel.parse_and_register(key, value, mock_delegate)

            mock_delegate.register_id_label.assert_called_once()
            registered_label = mock_delegate.register_id_label.call_args[0][0]
            assert registered_label.key == "!"
            assert registered_label.value == "123"

        def test_parse_and_registerメソッドに完了シンボル(self):
            key = "✓"
            value = "123"
            mock_delegate = Mock(spec=LabelRegisterable)

            IdLabel.parse_and_register(key, value, mock_delegate)

            mock_delegate.register_id_label.assert_called_once()
            registered_label = mock_delegate.register_id_label.call_args[0][0]
            assert registered_label.key == "✓"
            assert registered_label.value == "123"

        def test_parse_and_registerメソッドに中止シンボル(self):
            key = "×"
            value = "123"
            mock_delegate = Mock(spec=LabelRegisterable)

            IdLabel.parse_and_register(key, value, mock_delegate)

            mock_delegate.register_id_label.assert_called_once()
            registered_label = mock_delegate.register_id_label.call_args[0][0]
            assert registered_label.key == "×"
            assert registered_label.value == "123"

        def test_parse_and_registerメソッドに未知のキー(self):
            key = "?"  # 未知のキー
            value = "123"
            mock_delegate = Mock(spec=LabelRegisterable)

            with pytest.raises(ValueError, match="Unknown key: \\?"):
                IdLabel.parse_and_register(key, value, mock_delegate)
