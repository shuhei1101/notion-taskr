from dataclasses import dataclass


@dataclass
class PageId:
    value: str
    def __init__(self, value: str):
        if not value:
            raise ValueError(f"Page IDは必須です。")
        self.value = value