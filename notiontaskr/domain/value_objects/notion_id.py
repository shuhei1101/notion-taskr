from dataclasses import dataclass


@dataclass
class NotionId:
    number: str = ""
    prefix: str = ""

    def __init__(self, number: str, prefix: str = ""):
        if not number:
            raise ValueError(f"IDのnumberは必須です。")
        self.number = str(number)
        self.prefix = str(prefix)

    def __hash__(self):
        return hash(self.number)

    def __eq__(self, other: "object"):
        if not isinstance(other, NotionId):
            return False
        return self.number == other.number
