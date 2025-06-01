from dataclasses import dataclass


@dataclass
class NotionId:
    number: str = ""
    prefix: str = ""

    def __init__(self, number: str, prefix: str = ""):
        if not number:
            raise TypeError(f"NotionIdはstr型でなければなりません。")
        self.number = str(number)
        self.prefix = str(prefix)

    @classmethod
    def from_response_data(cls, data: dict) -> "NotionId":
        """レスポンスデータからインスタンスを生成する"""
        try:
            prefix = data["properties"]["ID"]["unique_id"]["prefix"]
            number = data["properties"]["ID"]["unique_id"]["number"]
            return cls(number=number, prefix=prefix)
        except KeyError as e:
            raise ValueError(f"レスポンスデータに必要なキーが存在しません: {e}")

    def __hash__(self):
        return hash(self.number)

    def __eq__(self, other: "object"):
        if not isinstance(other, NotionId):
            return False
        return self.number == other.number
