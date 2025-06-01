from dataclasses import dataclass, field

from notiontaskr.domain.value_objects.page_id import PageId


@dataclass
class SubTaskPageIds:
    """サブタスクのページIDを管理するクラス"""

    _list: list[PageId] = field(default_factory=list)

    @classmethod
    def from_response_data(cls, data: dict) -> "SubTaskPageIds":
        """レスポンスデータからSubTaskPageIdsのインスタンスを生成します"""
        try:
            sub_items = data["properties"]["サブアイテム"]["relation"]
            page_ids = [PageId(item["id"]) for item in sub_items]
        except (KeyError, IndexError, TypeError):
            raise ValueError("レスポンスデータにサブアイテムが含まれていません。")

        return cls(page_ids)

    def __iter__(self):
        return iter(self._list)

    def __len__(self):
        return len(self._list)

    def __getitem__(self, index):
        return self._list[index]
