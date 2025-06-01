from notiontaskr.domain.value_objects.man_hours import ManHours


class ScheduledManHours(ManHours):
    """スケジュールされたタスクの人時を表すクラス。

    ManHoursクラスを継承し、スケジュールされたタスクに特化した人時の機能を提供します。
    """

    @classmethod
    def from_response_data(cls, data: dict) -> "ScheduledManHours":
        """レスポンスデータからScheduledManHoursのインスタンスを生成します。

        Args:
            data (dict): レスポンスデータ。

        Returns:
            ScheduledManHours: レスポンスデータから生成されたScheduledManHoursインスタンス。
        """
        try:
            return cls(value=data["properties"]["人時(予)"]["number"])
        except KeyError:
            raise ValueError("レスポンスデータに人時(予)が含まれていません。")
