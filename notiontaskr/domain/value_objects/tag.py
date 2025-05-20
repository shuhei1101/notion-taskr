from dataclasses import dataclass


@dataclass
class Tag:
    value: str

    def __init__(self, value: str):
        if not value:
            raise ValueError(f"タグは必須です。")
        self.value = str(value)

    def __str__(self) -> str:
        return self.value
