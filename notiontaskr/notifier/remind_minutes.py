from datetime import timedelta


class RemindMinutes(timedelta):
    """リマインドの分を表すクラス
    timedeltaを継承して、分単位での表現を提供
    """

    def __str__(self) -> str:
        return f"{self.total_seconds() / 60:.0f}"

    def __int__(self) -> int:
        """分単位での整数値を返す"""
        return int(self.total_seconds() / 60)
