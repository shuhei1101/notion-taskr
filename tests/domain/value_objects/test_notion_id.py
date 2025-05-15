import pytest
from notiontaskr.domain.value_objects.notion_id import NotionId


class TestNotionId:
    class Test_initメソッド:
        def test_引数idが文字列のとき正常に初期化されること(self):
            notion_id = NotionId("1234567890")
            assert notion_id.number == "1234567890"

        def test_引数idがNoneのときTypeErrorが発生すること(self):
            with pytest.raises(TypeError):
                NotionId(None)  # type: ignore

    class Test_hashメソッド:
        def test_同じ値のNotionIdのハッシュ値が同じになること(self):
            notion_id1 = NotionId("1234567890")
            notion_id2 = NotionId("1234567890")
            assert hash(notion_id1) == hash(notion_id2)

    class Test_eqメソッド:
        def test_同じ値のNotionIdのときTrueを返すこと(self):
            notion_id1 = NotionId("1234567890")
            notion_id2 = NotionId("1234567890")
            assert notion_id1 == notion_id2

        def test_異なる値のNotionIdのときFalseを返すこと(self):
            notion_id1 = NotionId("1234567890")
            notion_id2 = NotionId("0987654321")
            assert notion_id1 != notion_id2
