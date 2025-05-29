from dataclasses import dataclass
from notiontaskr.domain.value_objects.notion_date import NotionDate
from notiontaskr.util.calculator import get_hours_diff


@dataclass
class ManHours:
    value: float

    def __init__(self, value: float):
        if value is None:
            # raise ValueError("ManHoursは必須です。")
            value = 0  # デフォルト値を0に設定
        if value < 0:
            raise ValueError(f"ManHours`{value}`は負の数であってはいけません。")

        self.value = float(value)

    def __add__(self, other):
        if not isinstance(other, ManHours):
            raise NotImplementedError(f"ManHours同士の加算のみサポートしています。")
        return ManHours(self.value + other.value)

    def __radd__(self, other):
        if other == 0:
            return self
        return self.__add__(other)

    def __float__(self):
        return self.value

    @classmethod
    def from_notion_date(cls, date: NotionDate):
        return cls(
            value=get_hours_diff(
                start_date=date.start,
                end_date=date.end,
            )
        )

    def __eq__(self, other):
        if not isinstance(other, ManHours):
            return False
        return self.value == other.value

    def __truediv__(self, other):
        if not isinstance(other, ManHours):
            raise NotImplementedError(f"ManHours同士の割り算のみサポートしています。")
        if other.value == 0:
            raise ZeroDivisionError("ManHoursの値で0で割ることはできません。")
        return ManHours(self.value / other.value)
