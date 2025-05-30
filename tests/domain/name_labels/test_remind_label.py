import emoji

from notiontaskr.domain.name_labels.remind_label import RemindLabel
from notiontaskr.notifier.task_remind_info import TaskRemindInfo


class TestRemindLabel:
    def test_開始前時間のみ存在する場合に初期化できること(self):

        label = RemindLabel.from_property(
            remind_info=TaskRemindInfo.from_raw_values(
                has_before_start=True,
                raw_before_start_minutes=5,
                has_before_end=False,
            )
        )

        assert label is not None

        assert label.key == emoji.emojize(":bell:")
        assert label.value == "5m|"

    def test_開始後時間のみ存在する場合に初期化できること(self):
        label = RemindLabel.from_property(
            remind_info=TaskRemindInfo.from_raw_values(
                has_before_start=False,
                has_before_end=True,
                raw_before_end_minutes=10,
            )
        )

        assert label is not None

        assert label.key == emoji.emojize(":bell:")
        assert label.value == "|10m"

    def test_開始前後時間が両方存在する場合に初期化できること(self):
        label = RemindLabel.from_property(
            remind_info=TaskRemindInfo.from_raw_values(
                has_before_start=True,
                raw_before_start_minutes=5,
                has_before_end=True,
                raw_before_end_minutes=10,
            )
        )

        assert label is not None

        assert label.key == emoji.emojize(":bell:")
        assert label.value == "5m|10m"
