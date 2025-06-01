import pytest
from notiontaskr.domain.value_objects.page_id import PageId
from notiontaskr.domain.value_objects.parent_task_page_id import ParentTaskPageId


class TestParentTaskPageId:
    def test_PageIdクラスを継承していること(self):

        assert issubclass(ParentTaskPageId, PageId)

    class Test_dataからインスタンスを生成可能:
        """例: data["properties"]["親アイテム"]["relation"][0]["id"]"""

        def test_レスポンスデータからインスタンスを生成できること(self):
            response_data = {
                "properties": {"親アイテム": {"relation": [{"id": "parent_id_123"}]}}
            }
            parent_task_page_id = (
                ParentTaskPageId.from_response_data_for_scheduled_task(response_data)
            )
            assert parent_task_page_id is not None
            assert parent_task_page_id.value == "parent_id_123"

        def test_レスポンスデータに親アイテムがない場合はNoneをを返すこと(self):
            response_data = {"properties": {}}
            assert (
                ParentTaskPageId.from_response_data_for_scheduled_task(response_data)
                is None
            )

    class Test_実績タスクのレスポンスデータからインスタンスを生成可能:
        """例: data["properties"]["親アイテム(予)"]["relation"][0]["id"]"""

        def test_実績タスクのレスポンスデータからインスタンスを生成できること(self):
            response_data = {
                "properties": {
                    "親アイテム(予)": {"relation": [{"id": "executed_parent_id_456"}]}
                }
            }
            parent_task_page_id = ParentTaskPageId.from_response_data_for_executed_task(
                response_data
            )
            assert parent_task_page_id is not None
            assert parent_task_page_id.value == "executed_parent_id_456"

        def test_実績タスクのレスポンスデータに親アイテムがない場合はNoneを返すこと(
            self,
        ):
            response_data = {"properties": {}}
            assert (
                ParentTaskPageId.from_response_data_for_executed_task(response_data)
                is None
            )
