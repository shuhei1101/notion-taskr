from notiontaskr.domain.value_objects.man_hours import ManHours


class ExecutedManHours(ManHours):
    """スケジュールされたタスクの人時を表すクラス。

    ManHoursクラスを継承し、スケジュールされたタスクに特化した人時の機能を提供します。
    """

    @classmethod
    def from_response_data(cls, data: dict) -> "ExecutedManHours":
        """レスポンスデータからExecutedManHoursのインスタンスを生成します。

        Args:
            data (dict): レスポンスデータ。

        Returns:
            ExecutedManHours: レスポンスデータから生成されたExecutedManHoursインスタンス。
        """
        try:
            return cls(value=data["properties"]["人時(実)"]["number"])
        except KeyError:
            raise ValueError("レスポンスデータに人時(実)が含まれていません。")
