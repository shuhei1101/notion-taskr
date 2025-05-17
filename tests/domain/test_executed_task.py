from unittest.mock import Mock
import pytest
from notiontaskr.domain.executed_task import ExecutedTask
from notiontaskr.domain.value_objects.notion_id import NotionId


class TestExecutedTask:
    class Test_from_response_data:
        def test_正常なレスポンスデータを渡したときに正常に初期化されること(self):
            data = {
                "id": "123",
                "properties": {
                    "ID": {"unique_id": {"number": "1", "prefix": "T"}},
                    "名前": {"title": [{"plain_text": "タスク名"}]},
                    "日付": {"date": {"start": "2023-10-01", "end": None}},
                    "タグ": {"multi_select": [{"name": "タグ1"}, {"name": "タグ2"}]},
                    "ステータス": {"status": {"name": "完了"}},
                    "予定タスク": {
                        "relation": [
                            {"id": "scheduled_task_id"},
                        ]
                    },
                    "親アイテム(予)": {
                        "relation": [
                            {"id": "parent_id"},
                        ]
                    },
                    # 他のプロパティも必要に応じて追加
                },
            }

            task = ExecutedTask.from_response_data(data)

            assert task.page_id.value == data["id"]
            assert (
                task.name.task_name
                == data["properties"]["名前"]["title"][0]["plain_text"]
            )
            assert task.tags == ["タグ1", "タグ2"]
            assert task.id.number == data["properties"]["ID"]["unique_id"]["number"]
            assert (
                task.status.value == data["properties"]["ステータス"]["status"]["name"]
            )

        def test_レスポンスデータに必要なキーが存在しない場合にExceptionでキャッチできること(
            self,
        ):
            data = {
                "id": "123",
                "properties": {
                    # 必要なキーが欠けている
                    "名前": {"title": [{"plain_text": "タスク名"}]},
                    # 他のプロパティも必要に応じて追加
                },
            }

            with pytest.raises(Exception):
                ExecutedTask.from_response_data(data)

    class Test_update_scheduled_task_id:
        def test_自身のscheduled_task_idと異なる値を渡したときに更新されること(self):
            task = ExecutedTask(
                page_id=Mock(),
                name=Mock(),
                tags=Mock(),
                id=Mock(),
                status=Mock(),
                scheduled_task_id=None,
            )
            task.update_scheduled_task_id(NotionId(number="123"))

            assert task.scheduled_task_id == NotionId(number="123")

        def test_自身のscheduled_task_idと同じ値を渡したときに更新されないこと(self):
            task = ExecutedTask(
                page_id=Mock(),
                name=Mock(),
                tags=Mock(),
                id=Mock(),
                status=Mock(),
                scheduled_task_id=NotionId(number="123"),
            )
            task.update_scheduled_task_id(NotionId(number="123"))

            assert task.scheduled_task_id == NotionId(number="123")
