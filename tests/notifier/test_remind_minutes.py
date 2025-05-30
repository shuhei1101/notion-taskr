from notiontaskr.notifier.remind_minutes import RemindMinutes


class TestRemindMinutes:
    def test___str__を呼び出すと分単位の文字列を返すこと(self):
        remind_minutes = RemindMinutes(minutes=30)
        assert str(remind_minutes) == "30"
