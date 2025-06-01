from dataclasses import dataclass


@dataclass
class PageId:
    value: str = ""

    def __init__(self, value: str):
        if not value:
            raise ValueError(f"Page IDは必須です。")
        self.value = str(value)

    @classmethod
    def from_response_data_for_scheduled_task(cls, data: dict) -> "PageId":
        """レスポンスデータからPageIdを生成する

        :param data: レスポンスデータ
        :return: PageIdオブジェクト
        """
        try:
            return cls(value=data["id"])
        except (KeyError, TypeError):
            raise ValueError("Page IDの生成に失敗。レスポンスデータ構造が不正です。")

    def __hash__(self):
        return hash(self.value)

    def __str__(self):
        return self.value

    def __eq__(self, other: "object"):
        if not isinstance(other, PageId):
            return False
        return self.value == other.value
