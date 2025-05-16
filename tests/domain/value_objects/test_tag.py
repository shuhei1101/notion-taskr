import pytest
from notiontaskr.domain.value_objects.tag import Tag


class TestTag:
    class Test_init:
        def test_空文字を渡すとValueErrorが発生すること(self):
            with pytest.raises(ValueError) as excinfo:
                Tag("")
            assert str(excinfo.value) == "タグは必須です。"

        def test_有効な値を渡すとインスタンスが作成されること(self):
            tag = Tag("重要")
            assert tag.value == "重要"
