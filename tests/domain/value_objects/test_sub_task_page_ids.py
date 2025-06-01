import pytest

from notiontaskr.domain.value_objects.page_id import PageId
from notiontaskr.domain.value_objects.sub_task_page_ids import SubTaskPageIds


class TestSubTaskPageIds:
    """サブタスクページIDの値オブジェクトのテストクラス

    PageIdのリストを保持する
    """

    class Test_response_dataからのインスタンス生成:
        """例:

        data["properties"]["サブアイテム"]["relation"]の中の["id"]を配列に持つ
        """

        def test_レスポンスデータからインスタンスを生成できること(self):
            response_data = {
                "properties": {
                    "サブアイテム": {
                        "relation": [{"id": "subtask1"}, {"id": "subtask2"}]
                    }
                }
            }

            sub_task_page_ids = SubTaskPageIds.from_response_data(response_data)
            assert len(sub_task_page_ids) == 2

        def test_レスポンスデータに特定のキーがない場合はValueErrorを発生させること(
            self,
        ):
            response_data = {"properties": {"サブアイテム": {}}}
            with pytest.raises(ValueError):
                SubTaskPageIds.from_response_data(response_data)

    class Test_リストのメソッド関連:
        def test_イテレータが使えること(self):
            sub_task_page_ids = SubTaskPageIds.from_response_data(
                {
                    "properties": {
                        "サブアイテム": {
                            "relation": [{"id": "subtask1"}, {"id": "subtask2"}]
                        }
                    }
                }
            )
            for page_id in sub_task_page_ids:
                assert page_id in [PageId("subtask1"), PageId("subtask2")]

        def test_lenが使えること(self):
            sub_task_page_ids = SubTaskPageIds.from_response_data(
                {
                    "properties": {
                        "サブアイテム": {
                            "relation": [{"id": "subtask1"}, {"id": "subtask2"}]
                        }
                    }
                }
            )
            assert len(sub_task_page_ids) == 2

        def test_直接要素にアクセスできること(self):
            sub_task_page_ids = SubTaskPageIds.from_response_data(
                {
                    "properties": {
                        "サブアイテム": {
                            "relation": [{"id": "subtask1"}, {"id": "subtask2"}]
                        }
                    }
                }
            )
            assert sub_task_page_ids[0] == PageId("subtask1")
            assert sub_task_page_ids[1] == PageId("subtask2")
