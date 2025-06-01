from notiontaskr.domain.value_objects.page_id import PageId
from notiontaskr.domain.value_objects.scheduled_task_page_id import ScheduledTaskPageId


class TestScheduledTaskPageId:
    def test_PageIdクラスを継承していること(self):

        assert issubclass(ScheduledTaskPageId, PageId)

    class Test_dataからインスタンスを生成可能:
        """例: data["properties"]["予定タスク"]["relation"][0]["id"]"""

        def test_レスポンスデータからインスタンスを生成できること(self):
            response_data = {
                "properties": {"予定タスク": {"relation": [{"id": "parent_id_123"}]}}
            }
            parent_task_page_id = (
                ScheduledTaskPageId.from_response_data_for_scheduled_task(response_data)
            )
            assert parent_task_page_id is not None
            assert parent_task_page_id.value == "parent_id_123"

        def test_レスポンスデータに親アイテムがない場合はNoneをを返すこと(self):
            response_data = {"properties": {}}
            assert (
                ScheduledTaskPageId.from_response_data_for_scheduled_task(response_data)
                is None
            )
