import pytest
from notiontaskr.domain.value_objects.status import Status


class TestStatus:
    class Test_from_strメソッド:
        def test_有効なステータス文字列を渡すと正しいStatusを返すこと(self):
            assert Status.from_str("未着手") == Status.NOT_STARTED
            assert Status.from_str("中止") == Status.CANCELED
            assert Status.from_str("進行中") == Status.IN_PROGRESS
            assert Status.from_str("遅延") == Status.DELAYED
            assert Status.from_str("完了") == Status.COMPLETED

        def test_無効なステータス文字列を渡すとValueErrorを発生させること(self):
            with pytest.raises(ValueError) as excinfo:
                Status.from_str("無効なステータス")

    class Test_strメソッド:
        def test_ステータスを文字列に変換できること(self):
            assert str(Status.NOT_STARTED) == "未着手"
            assert str(Status.CANCELED) == "中止"
            assert str(Status.IN_PROGRESS) == "進行中"
            assert str(Status.DELAYED) == "遅延"
            assert str(Status.COMPLETED) == "完了"

    class Test_notionのresponse_dataからのインスタンス生成:
        """例:

        status_str = data["properties"]["ステータス"]["status"]["name"]
        status = Status.from_str(status_str)
        """

        def test_ステータスの文字列からインスタンスを生成できること(self):
            response_data = {
                "properties": {"ステータス": {"status": {"name": "進行中"}}}
            }
            status = Status.from_response_data(response_data)
            assert status == Status.IN_PROGRESS

        def test_無効なステータス文字列が含まれる場合はValueErrorを発生させること(self):
            response_data = {
                "properties": {"ステータス": {"status": {"name": "無効なステータス"}}}
            }
            with pytest.raises(ValueError):
                Status.from_response_data(response_data)
