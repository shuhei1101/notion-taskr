import pytest
from unittest.mock import Mock

from notiontaskr.domain.name_labels.id_label import IdLabel
from notiontaskr.domain.name_labels.label_registerable import LabelRegisterable
from notiontaskr.domain.value_objects.notion_id import NotionId
from notiontaskr.domain.value_objects.status import Status


class Test_IdLabel:

    class Test_from_propertyメソッド:
        def test_未着手ステータスで初期化できること(self):
            notion_id = NotionId(number="123")
            status = Status.NOT_STARTED

            label = IdLabel.from_property(notion_id, status)

            assert label.key == ""
            assert label.value == "123"

        def test_完了ステータスで初期化できること(self):
            notion_id = NotionId(number="123")
            status = Status.COMPLETED

            label = IdLabel.from_property(notion_id, status)

            assert label.key == "✓"
            assert label.value == "123"

        def test_進行中ステータスで初期化できること(self):
            notion_id = NotionId(number="123")
            status = Status.IN_PROGRESS

            label = IdLabel.from_property(notion_id, status)

            assert label.key == "→"
            assert label.value == "123"

        def test_遅延ステータスで初期化できること(self):
            notion_id = NotionId(number="123")
            status = Status.DELAYED

            label = IdLabel.from_property(notion_id, status)

            assert label.key == "!"
            assert label.value == "123"

        def test_中止ステータスで初期化できること(self):
            notion_id = NotionId(number="123")
            status = Status.CANCELED

            label = IdLabel.from_property(notion_id, status)

            assert label.key == "×"
            assert label.value == "123"

    class Test_parse_and_registerメソッド:
        def test_数字のみのラベルでdelegateに登録ができること(self):
            key = "1"
            value = "23"
            mock_delegate = Mock(spec=LabelRegisterable)

            IdLabel.parse_and_register(key, value, mock_delegate)

            mock_delegate.register_id_label.assert_called_once()
            registered_label = mock_delegate.register_id_label.call_args[0][0]
            assert registered_label.key == ""
            assert registered_label.value == "123"

        def test_進行中シンボルでdelegateに登録ができること(self):
            key = "→"
            value = "123"
            mock_delegate = Mock(spec=LabelRegisterable)

            IdLabel.parse_and_register(key, value, mock_delegate)

            mock_delegate.register_id_label.assert_called_once()
            registered_label = mock_delegate.register_id_label.call_args[0][0]
            assert registered_label.key == "→"
            assert registered_label.value == "123"

        def test_遅延シンボルでdelegateに登録ができること(self):
            key = "!"
            value = "123"
            mock_delegate = Mock(spec=LabelRegisterable)

            IdLabel.parse_and_register(key, value, mock_delegate)

            mock_delegate.register_id_label.assert_called_once()
            registered_label = mock_delegate.register_id_label.call_args[0][0]
            assert registered_label.key == "!"
            assert registered_label.value == "123"

        def test_完了シンボルでdelegateに登録ができること(self):
            key = "✓"
            value = "123"
            mock_delegate = Mock(spec=LabelRegisterable)

            IdLabel.parse_and_register(key, value, mock_delegate)

            mock_delegate.register_id_label.assert_called_once()
            registered_label = mock_delegate.register_id_label.call_args[0][0]
            assert registered_label.key == "✓"
            assert registered_label.value == "123"

        def test_中止シンボルでdelegateに登録ができること(self):
            key = "×"
            value = "123"
            mock_delegate = Mock(spec=LabelRegisterable)

            IdLabel.parse_and_register(key, value, mock_delegate)

            mock_delegate.register_id_label.assert_called_once()
            registered_label = mock_delegate.register_id_label.call_args[0][0]
            assert registered_label.key == "×"
            assert registered_label.value == "123"

        def test_未知のキーでdelegateに登録ができないこと(self):
            key = "?"  # 未知のキー
            value = "123"
            mock_delegate = Mock(spec=LabelRegisterable)

            with pytest.raises(ValueError, match="Unknown key: \\?"):
                IdLabel.parse_and_register(key, value, mock_delegate)
