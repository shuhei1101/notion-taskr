from datetime import datetime
from notiontaskr.domain.task import Task
from notiontaskr.notifier.notifiable import Notifiable


class TaskReminder:
    def __init__(self, notifier: Notifiable):
        """コンストラクタでNotifiableインターフェースを受け取る"""
        self.notifier = notifier

    async def remind(self, task: Task):
        if task.is_remind_time_before_start():
            await self.notifier.notify(
                f"開始{task.remind_info.before_start_minutes}分前"
            )

        elif task.is_remind_time_before_end():
            # 現在時刻とリマインド日時の日付、時分を比較して、リマインド通知を行う
            await self.notifier.notify(f"終了{task.remind_info.before_end_minutes}分後")

        else:
            raise ValueError(
                f"リマインド日時が現在時刻と一致しません: {datetime.now()}"
            )
