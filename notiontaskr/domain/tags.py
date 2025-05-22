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

    def append(self, tag: Tag):
        self.tags.append(tag)

    def extend(self, tags: "Tags"):
        self.tags.extend(tags.tags)

    def __len__(self):
        return len(self.tags)
