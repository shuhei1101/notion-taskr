from enum import Enum


class Status(Enum):
    NOT_STARTED = "未着手"
    CANCELED = "中止"
    IN_PROGRESS = "進行中"
    DELAYED = "遅延"
    COMPLETED = "完了"

    @staticmethod
    def from_str(label: str) -> "Status":
        for status in Status:
            if status.value == label:
                return status
        raise ValueError(f"無効なステータスです: {label}")

    def __str__(self):
        return self.value
