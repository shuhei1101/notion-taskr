from dataclasses import dataclass
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

    scheduled_man_hours: ManHours = None
    executed_man_hours: ManHours = None
    executed_tasks: list["ExecutedTask"] = None  # 紐づいている実績タスク
    sub_task_page_ids: list["PageId"] = None  # サブアイテムのページID
    sub_tasks: list["ScheduledTask"] = None  # サブアイテム
    progress_rate: ProgressRate = 0  # 進捗率

    @classmethod
    def from_response_data(cls, data: dict):
        """レスポンスデータからインスタンスを生成する

        :raise KeyError:
        :raise ValueError: レスポンスデータに必要なキーが存在しない場合
        """

        try:
            task_number = data["properties"]["ID"]["unique_id"]["number"]
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
            executed_task.update_status_to(self.status)
            executed_task.update_parent_task_page_id(self.parent_task_page_id)
            executed_task.update_scheduled_task_page_id(self.page_id)

    def update_sub_tasks_properties(self):
        """サブアイテムのプロパティを更新する"""
        # サブアイテムの親IDラベルを更新する
        for sub_task in self.sub_tasks:
            sub_task.update_parent_id_label(
                ParentIdLabel.from_property(parent_id=self.id)
            )

    def _update_status_to_check_executed_tasks(self):
        """実績タスクの進捗を確認し、ステータスを更新する"""
        if not self.executed_tasks:
            return

        # 現在時刻
        now = datetime.now(timezone.utc)
        # もし、自身のステータスが未着手かつ
        # 実績タスクの開始時間が現在時刻よりも前のものが一件でもあれば、進行中にする
        if self.status == Status.NOT_STARTED and any(
            executed_task.date.start < now for executed_task in self.executed_tasks
        ):
            self.update_status(Status.IN_PROGRESS)
        # もし実績タスクの終了時間が現在時刻よりも前のものが一件もなければ、未着手にする
        elif self.status == Status.IN_PROGRESS and all(
            executed_task.date.start > now for executed_task in self.executed_tasks
        ):
            self.update_status(Status.NOT_STARTED)

    def update_status_to_check_properties(self):
        """タスクのプロパティに応じてステータスを更新する"""

        # 実績タスクのステータスを確認し、ステータスを更新する
        self._update_status_to_check_executed_tasks()

        if not self.sub_tasks:
            return

        # サブアイテムのステータスを更新し、ステータスを集計する
        statuses = []
        for sub_task in self.sub_tasks:
            sub_task.update_status_to_check_properties()
            statuses.append(sub_task.status)

        if any(status == Status.IN_PROGRESS for status in statuses):
            # 進行中のサブアイテムがある場合、親タスクは進行中にする
            self.update_status(Status.IN_PROGRESS)
        elif all(status == Status.COMPLETED for status in statuses):
            # 全てのサブアイテムが完了している場合、親タスクは完了にする
            self.update_status(Status.COMPLETED)
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
        """
        if not self.sub_tasks:
            self.update_progress_rate(ProgressRate(0.0))
            return

        done_tasks = [
            task for task in self.sub_tasks if task.status == Status.COMPLETED
        ]

        total_scheduled_hours = sum(
            task.scheduled_man_hours.value for task in self.sub_tasks
        )
        if total_scheduled_hours == 0:
            self.update_progress_rate(ProgressRate(0.0))
            return

        done_scheduled_hours = sum(
            task.scheduled_man_hours.value for task in done_tasks
        )

        progress = done_scheduled_hours / total_scheduled_hours
        self.update_progress_rate(ProgressRate(progress))

    def update_progress_rate(self, progress_rate: ProgressRate):
        """進捗率を更新する"""
        if self.progress_rate != progress_rate:
            self._toggle_is_updated(f"進捗率: {self.progress_rate} -> {progress_rate}")
            self.progress_rate = progress_rate

    def _aggregate_sub_man_hours(self, sub_tasks: list["ScheduledTask"]):
        """サブアイテムの工数を集計し、ラベルを更新する"""
        if sub_tasks is None or len(sub_tasks) == 0:
            return (None, ManHours(0))
        sub_scheduled_man_hours = 0.0
        sub_executed_man_hours = 0.0
        for sub_task in sub_tasks:
            sub_task.aggregate_man_hours()
            sub_scheduled_man_hours += sub_task.scheduled_man_hours.value
            sub_executed_man_hours += sub_task.executed_man_hours.value
        return (
            ManHours(sub_scheduled_man_hours),
            ManHours(sub_executed_man_hours),
        )

    def aggregate_man_hours(self):
        """実績工数を集計し、ラベルを更新する"""
        # サブアイテムの工数を集計する
        sub_scheduled_man_hours, sub_executed_man_hours = self._aggregate_sub_man_hours(
            self.sub_tasks
        )

        # サブアイテムがある場合のみ、予定人時を更新する
        if len(self.sub_tasks) > 0:
            self.update_scheduled_man_hours(sub_scheduled_man_hours)

        executed_man_hours = 0

        for executed_task in self.executed_tasks or []:
            executed_man_hours += float(executed_task.man_hours)

        self.update_executed_man_hours(
            sub_executed_man_hours + ManHours(executed_man_hours)
        )

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
