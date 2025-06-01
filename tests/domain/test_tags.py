import pytest
from notiontaskr.domain.value_objects.tag import Tag

from notiontaskr.domain.tags import Tags


class TestTags:

    def test_空の状態で初期化できること(self):
        tags = Tags.from_empty()
        assert tags is not None

    def test_タグ配列から初期化できること(self):
        tags = Tags.from_tags([Tag("tag1"), Tag("tag2")])
        assert tags is not None
        assert len(tags) == 2
        assert tags.tags[0] == Tag("tag1")
        assert tags.tags[1] == Tag("tag2")

    def test_tagを一つずつappendできること(self):
        tags = Tags.from_empty()
        tags.append(Tag("tag1"))
        assert len(tags) == 1
        assert tags.tags[0] == Tag("tag1")

    def test_tagをextendできること(self):
        tags = Tags.from_empty()
        tags.extend(Tags.from_tags([Tag("tag1"), Tag("tag2")]))
        assert len(tags) == 2
        assert tags.tags[0] == Tag("tag1")
        assert tags.tags[1] == Tag("tag2")

    def test_拡張for文が使えること(self):
        tags = Tags.from_tags([Tag("tag1"), Tag("tag2")])
        tag_names = [str(tag) for tag in tags]
        assert tag_names == ["tag1", "tag2"]

    class Test_notionのresponse_dataからのインスタンス生成:
        """例:

        tags = Tags.from_response_data(data["properties"]["タグ"]["multi_select"])
        """

        def test_レスポンスデータからTagsを生成できること(self):
            response_data = {
                "properties": {
                    "タグ": {
                        "multi_select": [
                            {"name": "tag1"},
                            {"name": "tag2"},
                        ]
                    }
                }
            }
            tags = Tags.from_response_data(response_data)
            assert len(tags) == 2
            assert tags.tags[0] == Tag("tag1")
            assert tags.tags[1] == Tag("tag2")

        def test_レスポンスデータに対象のキーがない場合はValueErrorを発生させること(
            self,
        ):
            response_data = {"properties": {}}
            with pytest.raises(ValueError):
                Tags.from_response_data(response_data)
