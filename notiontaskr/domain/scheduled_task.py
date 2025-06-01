from dataclasses import dataclass, field
from datetime import datetime, timezone

from notiontaskr.domain.name_labels.id_label import IdLabel
from notiontaskr.domain.task import Task
from notiontaskr.domain.task_name import TaskName
from notiontaskr.domain.update_content import UpdateContent
from notiontaskr.domain.value_objects.executed_man_hours import ExecutedManHours
from notiontaskr.domain.value_objects.man_hours import ManHours
from notiontaskr.domain.value_objects.notion_id import NotionId
from notiontaskr.domain.value_objects.page_id import PageId
from notiontaskr.domain.value_objects.parent_task_page_id import ParentTaskPageId
from notiontaskr.domain.value_objects.progress_rate import ProgressRate
from notiontaskr.domain.value_objects.scheduled_man_hours import ScheduledManHours
from notiontaskr.domain.value_objects.status import Status
from notiontaskr.domain.tags import Tags
from notiontaskr.domain.executed_tasks import ExecutedTasks
from notiontaskr.domain.scheduled_tasks import ScheduledTasks
from notiontaskr.domain.value_objects.notion_date import NotionDate
from notiontaskr.domain.value_objects.sub_task_page_ids import SubTaskPageIds
from notiontaskr.notifier.task_remind_info import TaskRemindInfo


@dataclass
class ScheduledTask(Task):
    """予定タスクモデル"""

    scheduled_man_hours: ScheduledManHours = field(
        default_factory=lambda: ScheduledManHours(0)
    )
    executed_man_hours: ExecutedManHours = field(
        default_factory=lambda: ExecutedManHours(0)
    )
    executed_tasks: ExecutedTasks = field(
        default_factory=lambda: ExecutedTasks.from_empty()
    )  # 紐づいている実績タスク
    sub_task_page_ids: SubTaskPageIds = field(
        default_factory=SubTaskPageIds
    )  # サブアイテムのページID
    sub_tasks: "ScheduledTasks" = field(
        default_factory=lambda: ScheduledTasks(_tasks=[])
    )  # サブアイテム
    progress_rate: ProgressRate = field(
        default_factory=lambda: ProgressRate(0)
    )  # 進捗率

    @classmethod
    def from_response_data(cls, data: dict):
        """レスポンスデータからインスタンスを生成する

        :raise KeyError:
        :raise ValueError: レスポンスデータに必要なキーが存在しない場合
        """

        task_number = data["properties"]["ID"]["unique_id"]["number"]
        try:
            # ========== タスクID ==========
            notion_id = NotionId.from_response_data(data)

            # ========== 日付 ==========
            try:
                notion_date = NotionDate.from_response_data(data)
            except ValueError as e:
                notion_date = None

            # ========== ステータス ==========
            status = Status.from_response_data(data)

            # ========== インスタンス生成 ==========
            instance = cls(
                page_id=PageId.from_response_data_for_scheduled_task(data),
                name=TaskName.from_response_data(data),
                tags=Tags.from_response_data(data),
                id=notion_id,
                status=status,
                parent_task_page_id=ParentTaskPageId.from_response_data_for_scheduled_task(
                    data
                ),
                scheduled_man_hours=ScheduledManHours.from_response_data(data),
                executed_man_hours=ExecutedManHours.from_response_data(data),
                sub_task_page_ids=SubTaskPageIds.from_response_data(data),
                sub_tasks=ScheduledTasks.from_empty(),
                progress_rate=ProgressRate.from_response_data(data),
                date=notion_date,
                remind_info=TaskRemindInfo.from_response_data(data),
            )

            # ========== IDラベルの更新 ==========
            instance.update_id_label(
                IdLabel.from_property(
                    id=notion_id,
                    status=status,
                )
            )

            # ========== リマインド情報の更新 ==========
            if not instance.remind_info.has_value():
                # 開始前通知時間と終了前通知時間が設定されていない場合はデフォルト値で更新
                instance.update_remind_info(instance.remind_info.get_default_self())

            return instance
        except KeyError as e:
            raise ValueError(f"In ScheduledTask[{task_number}] initialize error, {e}")
        except ValueError as e:
            raise ValueError(f"In ScheduledTask[{task_number}] initialize error, {e}")

    def update_executed_tasks_properties(self):
        """実績タスクのプロパティを更新する"""
        for executed_task in self.executed_tasks:
            executed_task.update_name(self.name)
            executed_task.update_status(self.status)
            executed_task.update_parent_task_page_id(self.parent_task_page_id)
            executed_task.update_scheduled_task_page_id(self.page_id)
            executed_task.update_remind_info(self.remind_info)

    def update_sub_tasks_properties(self):
        """サブアイテムのプロパティを更新する"""
        # サブアイテムの親IDラベルを更新する
        self.sub_tasks.update_parent_id_label(parent_id=self.id)

    def _update_status_by_checking_executed_tasks(self):
        """実績タスクの進捗を確認し、ステータスを更新する"""
        # 現在時刻
        now = datetime.now(timezone.utc)
        # もし、自身のステータスが未着手かつ
        # 実績タスクの開始時間が現在時刻よりも前のものが一件でもあれば、進行中にする
        if self.status == Status.NOT_STARTED and any(
            executed_task.date.start < now for executed_task in self.executed_tasks  # type: ignore
        ):
            self.update_status(Status.IN_PROGRESS)
        # もし実績タスクの終了時間が現在時刻よりも前のものが一件もなければ、未着手にする
        elif self.status == Status.IN_PROGRESS and all(
            now < executed_task.date.start for executed_task in self.executed_tasks  # type: ignore
        ):
            self.update_status(Status.NOT_STARTED)

    def _update_status_by_checking_sub_tasks(self):
        # サブアイテムのステータスを更新し、ステータスを集計する
        statuses = []
        for sub_task in self.sub_tasks:
            sub_task.update_status_by_checking_properties()
            statuses.append(sub_task.status)

        if all(status == Status.COMPLETED for status in statuses):
            # 全てのサブアイテムが完了している場合、親タスクは完了にする
            self.update_status(Status.COMPLETED)
        elif any(status == Status.IN_PROGRESS for status in statuses) or any(
            status == Status.COMPLETED for status in statuses
        ):
            # 一つ以上の進行中もしくは完了のサブアイテムがある場合、親タスクは進行中にする
            self.update_status(Status.IN_PROGRESS)
        else:
            # それ以外は未着手にする
            self.update_status(Status.NOT_STARTED)

    def update_status_by_checking_properties(self):
        """タスクのプロパティに応じてステータスを更新する"""

        if self.status == Status.CANCELED:
            # ステータスが中止の場合は、何もしない
            return

        if not self.is_delayed() and self.status == Status.DELAYED:
            # ステータスが遅延していない場合は、未着手に戻す
            self.update_status(Status.NOT_STARTED)

        if self.executed_tasks and len(self.executed_tasks) != 0:
            # 実績タスクの進捗を確認し、ステータスを更新する
            self._update_status_by_checking_executed_tasks()

        if self.sub_tasks and len(self.sub_tasks) != 0:
            # サブアイテムのステータスを確認し、ステータスを更新する
            self._update_status_by_checking_sub_tasks()

        if self.is_delayed():
            # タスクが遅延している場合は、ステータスを遅延にする
            self.update_status(Status.DELAYED)

        self.update_id_label(
            IdLabel.from_property(
                id=self.id,
                status=self.status,
            )
        )

    def calc_progress_rate(self):
        """
        完了済みサブタスクの予定人時合計 / 全サブタスクの予定人時合計 で進捗率を計算する。
        進捗率は 0.0〜1.0 の float で保存する。

        ただし、自身のステータスが完了の場合は、進捗率を 1.0 にする。
        """
        # 自身のステータスが完了の場合は、進捗率を 1.0 にする
        if self.status == Status.COMPLETED:
            self.update_progress_rate(ProgressRate(1.0))
            return
        # サブアイテムがない場合は進捗率を 0.0 にする
        if not self.sub_tasks:
            self.update_progress_rate(ProgressRate(0.0))
            return

        # サブアイテムのステータスが完了のものを取得する
        done_tasks = ScheduledTasks(
            [task for task in self.sub_tasks if task.status == Status.COMPLETED]
        )

        # サブアイテムの予定人時合計を取得する
        sub_tasks_properties = self.sub_tasks.sum_properties()
        total_scheduled_hours = sub_tasks_properties.scheduled_man_hours
        if total_scheduled_hours == ManHours(0):
            self.update_progress_rate(ProgressRate(0.0))
            return

        # 完了済みサブアイテムの予定人時合計を取得する
        done_tasks_properties = done_tasks.sum_properties()
        done_scheduled_hours = done_tasks_properties.scheduled_man_hours

        # 進捗率を計算する
        self.update_progress_rate(
            ProgressRate.from_man_hours(
                dividends=done_scheduled_hours,
                divisors=total_scheduled_hours,
            )
        )

    def update_progress_rate(self, progress_rate: ProgressRate):
        """進捗率を更新する"""
        if self.progress_rate != progress_rate:
            self._toggle_is_updated(
                UpdateContent(
                    key="進捗率",
                    original_value=str(self.progress_rate),
                    update_value=str(progress_rate),
                )
            )
            self.progress_rate = progress_rate

    def _aggregate_executed_man_hours(self) -> ManHours:
        """実績タスクの工数を集計する"""
        if self.executed_tasks is None or len(self.executed_tasks) == 0:
            return ManHours(0)

        executed_man_hours = ManHours(0)
        for executed_task in self.executed_tasks or []:
            executed_man_hours += executed_task.man_hours

        return executed_man_hours

    def aggregate_man_hours(self):
        """実績工数を集計し、ラベルを更新する"""

        sub_executed_man_hours = ExecutedManHours(0)

        if len(self.sub_tasks) > 0:
            # サブアイテムの工数を集計する
            sub_tasks_properties = self.sub_tasks.sum_properties()
            # サブアイテムの実績人時を加算
            sub_executed_man_hours = (
                sub_executed_man_hours + sub_tasks_properties.executed_man_hours
            )
            # サブアイテムの予定人時を更新する
            self.update_scheduled_man_hours(sub_tasks_properties.scheduled_man_hours)

        # 実績タスクの工数を集計する
        executed_tasks_properties = self.executed_tasks.sum_properties()

        self.update_executed_man_hours(
            sub_executed_man_hours + executed_tasks_properties.man_hours
        )

    def update_executed_man_hours(self, executed_man_hours: ManHours):
        """実績人時を更新する"""
        if self.executed_man_hours != executed_man_hours:
            self._toggle_is_updated(
                UpdateContent(
                    key="実績人時",
                    original_value=str(self.executed_man_hours),
                    update_value=str(executed_man_hours),
                )
            )
            self.executed_man_hours = executed_man_hours  # type: ignore

    def update_scheduled_man_hours(self, scheduled_man_hours: ManHours):
        """予定人時を更新する"""
        if self.scheduled_man_hours != scheduled_man_hours:
            self._toggle_is_updated(
                UpdateContent(
                    key="予定人時",
                    original_value=str(self.scheduled_man_hours),
                    update_value=str(scheduled_man_hours),
                )
            )
            self.scheduled_man_hours = scheduled_man_hours  # type: ignore

    def update_executed_tasks(self, executed_tasks: ExecutedTasks):
        """実績タスクを更新する"""
        self.executed_tasks = executed_tasks

    def update_sub_tasks(self, sub_tasks: "ScheduledTasks"):
        """サブアイテムを更新する"""
        self.sub_tasks = sub_tasks

    def is_delayed(self) -> bool:
        """タスクが遅延しているかどうかを判定する"""
        if self.date is None:
            return False
        if self.status == Status.COMPLETED or self.status == Status.CANCELED:
            return False

        # 現在時刻
        now = datetime.now(timezone.utc)
        # タスクの終了日時が現在時刻よりも前で、ステータスが未着手または進行中の場合は遅延とみなす
        return self.date.end < now and (
            self.status == Status.NOT_STARTED or self.status == Status.IN_PROGRESS
        )
