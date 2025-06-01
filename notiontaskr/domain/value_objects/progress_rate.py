from dataclasses import dataclass

from notiontaskr.domain.value_objects.man_hours import ManHours


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

    @classmethod
    def from_man_hours(
        cls, dividends: "ManHours", divisors: "ManHours"
    ) -> "ProgressRate":
        """ManHoursから進捗率を初期化する"""
        if divisors == ManHours(0):
            return cls(0.0)
        return cls(float(dividends / divisors))

    @classmethod
    def from_response_data(cls, data: dict) -> "ProgressRate":
        """レスポンスデータからProgressRateのインスタンスを生成します。

        Args:
            data (dict): レスポンスデータ。

        Returns:
            ProgressRate: レスポンスデータから生成されたProgressRateインスタンス。
        """
        try:
            return cls(value=data["properties"]["進捗率"]["number"])
        except KeyError:
            raise ValueError("レスポンスデータに進捗率が含まれていません。")

    def __float__(self) -> float:
        return self.value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ProgressRate):
            return False
        return self.value == other.value
