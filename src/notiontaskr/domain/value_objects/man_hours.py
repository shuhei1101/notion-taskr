from notiontaskr.domain.value_objects.notion_date import NotionDate
from notiontaskr.util.calculator import get_hours_diff


class ManHours:
    value: float

    def __init__(self, value: float):
        if value is None:
            # raise ValueError("ManHoursは必須です。")
            value = 0  # デフォルト値を0に設定
        if value < 0:
            raise ValueError(f"ManHours`{value}`は負の数であってはいけません。")

        self.value = float(value)

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
