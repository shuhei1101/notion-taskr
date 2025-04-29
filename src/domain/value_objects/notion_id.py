from dataclasses import dataclass


@dataclass
class NotionId:
    prefix: str = None
    number: str = None
    def __init__(self, prefix: str, number: str):
        if not number:
            raise ValueError(f"IDのnumberは必須です。")
        self.prefix = prefix
        self.number = number

    def __eq__(self, other):
        if isinstance(other, NotionId):
            return self.number == other.number
        return False