from datetime import datetime, timezone
from typing import TYPE_CHECKING, Callable, Optional
from notiontaskr.notifier.notifiable import Notifiable

if TYPE_CHECKING:
    from notiontaskr.domain.task import Task
    from notiontaskr.domain.tasks import Tasks


class TaskReminder:
    def __init__(self, notifier: "Notifiable"):
        """コンストラクタでNotifiableインターフェースを受け取る"""
        self.notifier = notifier

    async def remind(
        self,
        tasks: "Tasks",
        on_success=Callable[["Task"], None],
        on_error=Callable[[Exception, "Task"], None],
    ) -> None:
        for task in tasks.get_remind_tasks():
            try:
                if self.is_remind_time_before_start(task):
                    message = f"{str(task.remind_info.before_start_minutes)}分後開始: {task.name.get_remind_message()}"

                elif self.is_remind_time_before_end(task):
                    message = f"{str(task.remind_info.before_end_minutes)}分後終了: {task.name.get_remind_message()}"

                elif self.is_remind_time_equal_start(task):
                    message = f"開始: {task.name.get_remind_message()}"
                elif self.is_remind_time_equal_end(task):
                    message = f"終了: {task.name.get_remind_message()}"

                else:
                    raise ValueError(f"リマインド時刻が現在ではありません: {task.name}")

                await self.notifier.notify(
                    message=message,
                )
                on_success(task)

            except Exception as e:
                on_error(e, task)

    @staticmethod
    def get_before_start_dt(task: "Task") -> Optional["datetime"]:
        """開始前リマインド日時を取得する"""
        if task.date is None:
            return None

        before_start_dt = None

        if (
            task.remind_info.has_before_start
            and task.remind_info.before_start_minutes is not None
        ):
            before_start_dt = task.date.start - task.remind_info.before_start_minutes

        return before_start_dt

    @staticmethod
    def get_before_end_dt(task: "Task") -> Optional["datetime"]:
        """終了前リマインド日時を取得する"""
        if task.date is None:
            return None

        before_end_dt = None

        if (
            task.remind_info.has_before_end
            and task.remind_info.before_end_minutes is not None
        ):
            before_end_dt = task.date.end - task.remind_info.before_end_minutes

        return before_end_dt

    @staticmethod
    def is_remind_time_before_start(task: "Task") -> bool:
        """開始前のリマインド時刻が現在かどうかを判定する"""
        before_start_dt = TaskReminder.get_before_start_dt(task)
        if before_start_dt is None:
            return False

        now_hm = datetime.now(timezone.utc).replace(second=0, microsecond=0)
        before_start_hm = before_start_dt.replace(second=0, microsecond=0)

        return now_hm == before_start_hm

    @staticmethod
    def is_remind_time_before_end(task: "Task") -> bool:
        """終了前のリマインド時刻が現在かどうかを判定する"""
        before_end_dt = TaskReminder.get_before_end_dt(task)
        if before_end_dt is None:
            return False

        now_hm = datetime.now(timezone.utc).replace(second=0, microsecond=0)
        before_end_hm = before_end_dt.replace(second=0, microsecond=0)

        return now_hm == before_end_hm

    @staticmethod
    def is_remind_time_equal_start(task: "Task") -> bool:
        """開始時刻が現在かどうかを判定する"""
        if task.date is None or not task.remind_info.has_start:
            return False

        now_hm = datetime.now(timezone.utc).replace(second=0, microsecond=0)
        start_hm = task.date.start.replace(second=0, microsecond=0)

        return now_hm == start_hm

    @staticmethod
    def is_remind_time_equal_end(task: "Task") -> bool:
        """終了時刻が現在かどうかを判定する"""
        if task.date is None or not task.remind_info.has_end:
            return False

        now_hm = datetime.now(timezone.utc).replace(second=0, microsecond=0)
        end_hm = task.date.end.replace(second=0, microsecond=0)

        return now_hm == end_hm
