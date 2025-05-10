from dataclasses import dataclass


@dataclass
class NotionId:
    number: str = None
    prefix: str = None
    def __init__(self, number: str, prefix: str = None):
        if not number:
            raise ValueError(f"IDのnumberは必須です。")
        self.number = str(number)
        self.prefix = str(prefix)

    def __eq__(self, other: 'NotionId'):
        if not isinstance(other, NotionId):
            return False
        return self.number == other.number