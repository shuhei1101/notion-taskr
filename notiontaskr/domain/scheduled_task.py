from dataclasses import dataclass, field
from datetime import datetime, timezone

from notiontaskr.domain.executed_task import ExecutedTask
from notiontaskr.domain.name_labels.id_label import IdLabel
from notiontaskr.domain.name_labels.parent_id_label import ParentIdLabel
from notiontaskr.domain.task import Task
from notiontaskr.domain.task_name import TaskName
from notiontaskr.domain.value_objects.man_hours import ManHours
from notiontaskr.domain.value_objects.notion_id import NotionId
from notiontaskr.domain.value_objects.page_id import PageId
from notiontaskr.domain.value_objects.progress_rate import ProgressRate
from notiontaskr.domain.value_objects.status import Status


@dataclass
class ScheduledTask(Task):
    """予定タスクモデル"""

    scheduled_man_hours: ManHours = field(default_factory=lambda: ManHours(0))
    executed_man_hours: ManHours = field(default_factory=lambda: ManHours(0))
    executed_tasks: list["ExecutedTask"] = field(
        default_factory=list
    )  # 紐づいている実績タスク
    sub_task_page_ids: list["PageId"] = field(
        default_factory=list
    )  # サブアイテムのページID
    sub_tasks: list["ScheduledTask"] = field(default_factory=list)  # サブアイテム
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
            task_name = TaskName.from_raw_task_name(
                data["properties"]["名前"]["title"][0]["plain_text"]
            )
            notion_id = NotionId(
                prefix=data["properties"]["ID"]["unique_id"]["prefix"],
                number=task_number,
            )

            status = Status.from_str(data["properties"]["ステータス"]["status"]["name"])
            tags = []
            for tag in data["properties"]["タグ"]["multi_select"]:
                tags.append(tag["name"])

            instance = cls(
                page_id=PageId(data["id"]),
                name=task_name,
                tags=tags,
                id=notion_id,
                status=status,
                parent_task_page_id=(
                    PageId(
                        value=data["properties"]["親アイテム"]["relation"][0]["id"],
                    )
                    if data["properties"]["親アイテム"]["relation"]
                    else None
                ),
                scheduled_man_hours=ManHours(data["properties"]["人時(予)"]["number"]),
                executed_man_hours=ManHours(data["properties"]["人時(実)"]["number"]),
                executed_tasks=[],
                sub_task_page_ids=[
                    PageId(relation["id"])
                    for relation in data["properties"]["サブアイテム"]["relation"]
                ],
                sub_tasks=[],
                progress_rate=ProgressRate(data["properties"]["進捗率"]["number"]),
            )

            # IDラベルを更新
            instance.update_id_label(
                IdLabel.from_property(
                    id=notion_id,
                    status=status,
                )
            )

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

    def update_sub_tasks_properties(self):
        """サブアイテムのプロパティを更新する"""
        # サブアイテムの親IDラベルを更新する
        for sub_task in self.sub_tasks:
            sub_task.update_parent_id_label(
                ParentIdLabel.from_property(parent_id=self.id)
            )

    def _update_status_by_checking_executed_tasks(self):
        """実績タスクの進捗を確認し、ステータスを更新する"""
        if not self.executed_tasks or len(self.executed_tasks) == 0:
            return

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

    def update_status_by_checking_properties(self):
        """タスクのプロパティに応じてステータスを更新する"""

        if self.status == Status.CANCELED:
            # ステータスが中止の場合は、何もしない
            return

        # 実績タスクのステータスを確認し、ステータスを更新する
        self._update_status_by_checking_executed_tasks()

        if not self.sub_tasks or len(self.sub_tasks) == 0:
            # サブアイテムがない場合、処理を終了する
            return

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
        done_tasks = [
            task for task in self.sub_tasks if task.status == Status.COMPLETED
        ]

        # サブアイテムの予定人時合計を取得する
        total_scheduled_hours = sum(
            float(task.scheduled_man_hours) for task in self.sub_tasks
        )
        if total_scheduled_hours == 0:
            self.update_progress_rate(ProgressRate(0.0))
            return

        # 完了済みサブアイテムの予定人時合計を取得する
        done_scheduled_hours = sum(
            float(task.scheduled_man_hours) for task in done_tasks
        )

        # 進捗率を計算する
        progress = done_scheduled_hours / total_scheduled_hours
        self.update_progress_rate(ProgressRate(progress))

    def update_progress_rate(self, progress_rate: ProgressRate):
        """進捗率を更新する"""
        if self.progress_rate != progress_rate:
            self._toggle_is_updated(f"進捗率: {self.progress_rate} -> {progress_rate}")
            self.progress_rate = progress_rate

    def _aggregate_sub_man_hours(self) -> tuple[ManHours, ManHours]:
        """サブアイテムの工数を集計する"""
        if self.sub_tasks is None or len(self.sub_tasks) == 0:
            return (ManHours(0), ManHours(0))
        sub_scheduled_man_hours = 0.0
        sub_executed_man_hours = 0.0
        for sub_task in self.sub_tasks:
            sub_task.aggregate_man_hours()
            sub_scheduled_man_hours += float(sub_task.scheduled_man_hours)
            sub_executed_man_hours += float(sub_task.executed_man_hours)
        return (
            ManHours(sub_scheduled_man_hours),
            ManHours(sub_executed_man_hours),
        )

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

        sub_scheduled_man_hours = ManHours(0)
        sub_executed_man_hours = ManHours(0)

        if len(self.sub_tasks) > 0:
            # サブアイテムの工数を集計する
            sub_scheduled_man_hours, sub_executed_man_hours = (
                self._aggregate_sub_man_hours()
            )
            # サブアイテムの予定人時を更新する
            self.update_scheduled_man_hours(sub_scheduled_man_hours)

        # 実績タスクの工数を集計する
        executed_man_hours = self._aggregate_executed_man_hours()

        self.update_executed_man_hours(sub_executed_man_hours + executed_man_hours)

    def update_executed_man_hours(self, executed_man_hours: ManHours):
        """実績人時を更新する"""
        if self.executed_man_hours != executed_man_hours:
            self._toggle_is_updated(
                f"実績人時: {self.executed_man_hours} -> {executed_man_hours}"
            )
            self.executed_man_hours = executed_man_hours

    def update_scheduled_man_hours(self, scheduled_man_hours: ManHours):
        """予定人時を更新する"""
        if self.scheduled_man_hours != scheduled_man_hours:
            self._toggle_is_updated(
                f"予定人時: {self.scheduled_man_hours} -> {scheduled_man_hours}"
            )
        self.scheduled_man_hours = scheduled_man_hours

    def update_executed_tasks(
        self,
        executed_tasks: list["ExecutedTask"],
    ):
        """実績タスクを更新する"""
        self.executed_tasks = executed_tasks

    def update_sub_tasks(
        self,
        sub_tasks: list["ScheduledTask"],
    ):
        """サブアイテムを更新する"""
        self.sub_tasks = sub_tasks
