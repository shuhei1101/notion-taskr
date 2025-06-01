import pytest

from notiontaskr.domain.value_objects.page_id import PageId


class Test_PageId:
    class Test_初期化メソッド:
        def test_空の値を渡すと例外が発生すること(self):
            with pytest.raises(ValueError) as excinfo:
                PageId("")

        def test_有効な値を渡すとインスタンスが作成されること(self):
            page_id = PageId("123")
            assert page_id.value == "123"

    class Test__hashメソッド:
        def test_同じ値のインスタンスは同じハッシュ値を持つこと(self):
            page_id1 = PageId("123")
            page_id2 = PageId("123")
            assert hash(page_id1) == hash(page_id2)

        def test_異なる値のインスタンスは異なるハッシュ値を持つこと(self):
            page_id1 = PageId("123")
            page_id2 = PageId("456")
            assert hash(page_id1) != hash(page_id2)

    class Test_strメソッド:
        def test_インスタンスを文字列に変換できること(self):
            page_id = PageId("123")
            assert str(page_id) == "123"

    class Test_notionのresponse_dataからのインスタンス生成:
        """
        例: data["id"]
        """

        def test_レスポンスデータからインスタンスを生成できること(self):
            response_data = {"id": "123"}
            page_id = PageId.from_response_data_for_scheduled_task(response_data)
            assert page_id.value == "123"

        def test_レスポンスデータにidがない場合はValueErrorを発生させること(self):
            response_data = {}
            with pytest.raises(ValueError):
                PageId.from_response_data_for_scheduled_task(response_data)
