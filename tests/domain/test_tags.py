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
