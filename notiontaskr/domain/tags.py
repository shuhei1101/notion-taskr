from dataclasses import dataclass
from typing import List

from notiontaskr.domain.value_objects.tag import Tag


@dataclass
class Tags:
    tags: List[Tag]

    @classmethod
    def from_empty(cls):
        return cls(tags=[])

    @classmethod
    def from_tags(cls, tags: List[Tag]):
        return cls(
            tags=tags,
        )

    @classmethod
    def from_response_data(cls, data: dict) -> "Tags":
        """レスポンスデータからTagsを生成する

        :param data: レスポンスデータ
        :return: Tagsオブジェクト
        """
        try:
            tags = [
                Tag(tag["name"]) for tag in data["properties"]["タグ"]["multi_select"]
            ]
            return cls.from_tags(tags)
        except (KeyError, IndexError, TypeError):
            raise ValueError("タグの生成に失敗。レスポンスデータ構造が不正です。")

    def append(self, tag: Tag):
        self.tags.append(tag)

    def extend(self, tags: "Tags"):
        self.tags.extend(tags.tags)

    def __len__(self):
        return len(self.tags)

    def __iter__(self):
        return iter(self.tags)
