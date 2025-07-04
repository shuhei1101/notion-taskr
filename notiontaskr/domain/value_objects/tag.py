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

    def __hash__(self) -> int:
        return hash(self.value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Tag):
            return NotImplemented
        return self.value == other.value
