from dataclasses import dataclass


@dataclass
class PageId:
    value: str = ""

    def __init__(self, value: str):
        if not value:
            raise ValueError(f"Page IDは必須です。")
        self.value = str(value)

    def __hash__(self):
        return hash(self.value)

    def __str__(self):
        return self.value
