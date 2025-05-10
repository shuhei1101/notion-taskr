from dataclasses import dataclass


@dataclass
class Status:
    value: str
    def __init__(self, value: str):
        if not value:
            raise ValueError(f"Statusは必須です。")
        self.value = str(value)

    def __str__(self):
        return self.value

    def __eq__(self, other: 'Status'):
        if not isinstance(other, Status):
            return False
        return self.value == other.value