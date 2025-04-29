from dataclasses import dataclass

from domain.value_objects.notion_date import NotionDate
from util.calculator import get_hours_diff
from util.converter import man_hour_to_man_days


@dataclass
class ManDays:
    value: float
    
    def __init__(self, value: float):
        # 値がNoneでないことを確認
        if value is None:
            raise ValueError(f"ManDaysは必須です。")
        # 値が負の数でないことを確認
        if value < 0:
            raise ValueError(f"ManDays`{value}`は負の数であってはいけません。")

        self.value = value

    @classmethod
    def from_notion_date(cls, date: NotionDate):
        return cls(
            value=man_hour_to_man_days(get_hours_diff(
                    start_date=date.start,
                    end_date=date.end,
                ))
        )
        