from dataclasses import dataclass


@dataclass
class ProgressRate:
    """進捗率"""

    value: float

    def __init__(self, value: float):
        if value is None:
            value = 0.0
        if value < 0.0:
            value = 0.0
        if value > 1.0:
            value = 1.0

        self.value = value

    def __float__(self) -> float:
        return self.value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ProgressRate):
            raise NotImplementedError(f"ProgressRateは{type(other)}と比較できません。")
        return self.value == other.value
