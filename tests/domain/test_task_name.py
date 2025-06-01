import copy
from unittest.mock import Mock, patch
from notiontaskr.domain.task_name import TaskName
from notiontaskr.domain.name_labels.name_label import NameLabel
import pytest


class TestTaskName:
    class Test_from_raw_task_name:
        class Test_タスク名にラベルが含まれている場合:
            def test_タスク名からラベルや前後の空白を除去できること(self):
                raw_task_name = " [ID1] タスク名 [親タスクID1] "
                task_name = TaskName.from_raw_task_name(raw_task_name)
                assert task_name.task_name == "タスク名"

            @patch.object(NameLabel, "parse_labels")
            def test_含まれてるラベルのに応じてNameLabelのparse_labelsが呼び出されること(
                self,
                mock_parse_labels: Mock,
            ):
                raw_task_name = " [ID1] タスク名 [親タスクID1] "
                task_name = TaskName.from_raw_task_name(raw_task_name)
                mock_parse_labels.assert_any_call("ID1", task_name)
                mock_parse_labels.assert_any_call("親タスクID1", task_name)

        class Test_タスク名にラベルが含まれていない場合:
            @patch.object(NameLabel, "parse_labels")
            def test_ラベルが含まれていない場合はparse_labelsが呼び出されないこと(
                self,
                mock_parse_labels: Mock,
            ):
                raw_task_name = "タスク名"
                task_name = TaskName.from_raw_task_name(raw_task_name)
                mock_parse_labels.assert_not_called()

    class Test___str__:
        def test_タスク名を順番どおりに結合して表示すること(self):
            task_name = TaskName(
                task_name="タスク名",
                id_label=Mock(__str__=Mock(return_value="[ID1]")),
                man_hours_label=Mock(__str__=Mock(return_value="[人時]")),
                parent_id_label=Mock(__str__=Mock(return_value="[親ID]")),
            )

            assert str(task_name) == "[ID1] タスク名 [人時][親ID]"

        def test_IDラベルがない場合はタスク名と人時ラベルを結合して表示すること(
            self,
        ):
            task_name = TaskName(
                task_name="タスク名",
                id_label=None,
                man_hours_label=Mock(__str__=Mock(return_value="[人時]")),
                parent_id_label=Mock(__str__=Mock(return_value="[親ID]")),
            )
            assert str(task_name) == "タスク名 [人時][親ID]"

        def test_ラベルがない場合は前後の空白がないタスク名のみを表示すること(self):
            task_name = TaskName(
                task_name="タスク名",
                id_label=None,
                man_hours_label=None,
                parent_id_label=None,
            )
            assert str(task_name) == "タスク名"

    class Test___eq__:
        def test_すべてのプロパティで比較を行うこと(self):
            mock_task_name = Mock(__eq__=Mock(return_value=True))
            mock_id_label = Mock(__eq__=Mock(return_value=True))
            mock_man_hours_label = Mock(__eq__=Mock(return_value=True))
            mock_parent_id_label = Mock(__eq__=Mock(return_value=True))

            task_name1 = TaskName(
                task_name=mock_task_name,
                id_label=mock_id_label,
                man_hours_label=mock_man_hours_label,
                parent_id_label=mock_parent_id_label,
            )
            task_name2 = copy.deepcopy(task_name1)

            assert task_name1 == task_name2

            mock_task_name.__eq__.assert_called_once_with(task_name2.task_name)  # type: ignore
            mock_id_label.__eq__.assert_called_once_with(task_name2.id_label)  # type: ignore
            mock_man_hours_label.__eq__.assert_called_once_with(task_name2.man_hours_label)  # type: ignore
            mock_parent_id_label.__eq__.assert_called_once_with(task_name2.parent_id_label)  # type: ignore

        def test_比較対象のオブジェクトがTaskNameでない場合はFalseを返すこと(self):
            task_name = TaskName(
                task_name="タスク名",
                id_label=None,
                man_hours_label=None,
                parent_id_label=None,
            )
            assert task_name != "タスク名"

    class TestRegister:

        @pytest.fixture
        def task_name(self) -> TaskName:
            """TaskNameのインスタンスを返すフィクスチャ"""
            return TaskName(
                task_name="タスク名",
                id_label=None,
                man_hours_label=None,
                parent_id_label=None,
            )

        class Test_register_id_label:
            def test_ラベルを登録できること(self, task_name: TaskName):
                mock_label = Mock()
                task_name.register_id_label(mock_label)
                assert task_name.id_label == mock_label

        class Test_register_man_hours_label:
            def test_ラベルを登録できること(self, task_name: TaskName):
                mock_label = Mock()
                task_name.register_man_hours_label(mock_label)
                assert task_name.man_hours_label == mock_label

        class Test_register_parent_id_label:
            def test_ラベルを登録できること(self, task_name: TaskName):
                mock_label = Mock()
                task_name.register_parent_id_label(mock_label)
                assert task_name.parent_id_label == mock_label

    class Test_notionのresponse_dataからのインスタンス生成:
        """

        例: data["properties"]["名前"]["title"][0]["plain_text"]
        """

        def test_タスク名を正しく設定できること(self):
            response_data = {
                "properties": {
                    "名前": {"title": [{"plain_text": "[1234] タスク名 [親1324]"}]}
                }
            }
            task_name = TaskName.from_response_data(response_data)
            assert task_name.task_name == "タスク名"
            assert task_name.id_label is not None
            assert task_name.id_label.value == "1234"
            assert task_name.parent_id_label is not None
            assert task_name.parent_id_label.value == "1324"

        def test_response_dataに異常がある場合はValueErrorを発生させること(
            self,
        ):
            response_data = {"properties": "例外データ"}
            with pytest.raises(ValueError):
                TaskName.from_response_data(response_data)
