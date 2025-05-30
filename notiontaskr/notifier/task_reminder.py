from datetime import datetime
from notiontaskr.domain.task import Task
from notiontaskr.notifier.notifiable import Notifiable


class TaskReminder:
    def __init__(self, notifier: Notifiable):
        """コンストラクタでNotifiableインターフェースを受け取る"""
        self.notifier = notifier

    def remind(self, task: Task):
        remind_dt = task.get_remind_dt()
        if remind_dt is None:
            raise ValueError("Task must have a remind date time set.")

        now_hm = datetime.now().replace(second=0, microsecond=0)
        if remind_dt.before_start:
            # 現在時刻とリマインド日時の日付、時分を比較して、リマインド通知を行う
            before_start_hm = remind_dt.before_start.replace(second=0, microsecond=0)
            if now_hm == before_start_hm:
                self.notifier.notify(f"開始{task.remind_info.before_start_minutes}分前")

        if remind_dt.before_end:
            # 現在時刻とリマインド日時の日付、時分を比較して、リマインド通知を行う
            before_end_hm = remind_dt.before_end.replace(second=0, microsecond=0)
            if now_hm == before_end_hm:
                self.notifier.notify(f"終了{task.remind_info.before_end_minutes}分後")
