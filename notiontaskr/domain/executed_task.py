from dataclasses import dataclass, field
from typing import Optional

from notiontaskr.domain.task import Task
from notiontaskr.domain.task_name import TaskName
from notiontaskr.domain.update_content import UpdateContent
from notiontaskr.domain.value_objects.man_hours import ManHours
from notiontaskr.domain.value_objects.notion_date import NotionDate
from notiontaskr.domain.value_objects.notion_id import NotionId
from notiontaskr.domain.value_objects.page_id import PageId
from notiontaskr.domain.value_objects.parent_task_page_id import ParentTaskPageId
from notiontaskr.domain.value_objects.scheduled_task_id import ScheduledTaskId
from notiontaskr.domain.value_objects.scheduled_task_page_id import ScheduledTaskPageId
from notiontaskr.domain.value_objects.status import Status
from notiontaskr.domain.tags import Tags
from notiontaskr.notifier.task_remind_info import TaskRemindInfo


@dataclass
class ExecutedTask(Task):
    """実績タスクモデル"""

    man_hours: ManHours = field(default_factory=lambda: ManHours(0))
    scheduled_task_id: Optional[ScheduledTaskId] = None  # 紐づいている予定タスクのID
    scheduled_task_page_id: Optional[ScheduledTaskPageId] = (
        None  # 紐づいている予定タスクのページID
    )

    @classmethod
    def from_response_data(cls, data: dict) -> "ExecutedTask":
        """レスポンスデータからインスタンスを生成する

        :raise KeyError:
        :raise ValueError: レスポンスデータに必要なキーが存在しない場合
        """

        task_number = data["properties"]["ID"]["unique_id"]["number"]
        try:
            # ========== タスク名 ==========
            task_name = TaskName.from_response_data(data)

            # ========== 日付 ==========
            notion_date = NotionDate.from_response_data(data)
            man_hours = ManHours.from_notion_date(notion_date)

            # ========== インスタンス生成 ==========
            instance = cls(
                page_id=PageId.from_response_data_for_scheduled_task(data),  #
                name=TaskName.from_response_data(data),
                tags=Tags.from_response_data(data),
                id=NotionId.from_response_data(data),
                status=Status.from_response_data(data),
                date=notion_date,
                man_hours=man_hours,
                scheduled_task_id=ScheduledTaskId.from_task_name(task_name),
                parent_task_page_id=ParentTaskPageId.from_response_data_for_executed_task(
                    data
                ),
                scheduled_task_page_id=ScheduledTaskPageId.from_response_data_for_scheduled_task(
                    data
                ),
                remind_info=TaskRemindInfo.from_response_data(data),
            )

            # ========== リマインド情報の更新 ==========
            if not instance.remind_info.has_value():
                # 開始前通知時間と終了前通知時間が設定されていない場合はデフォルト値で更新
                instance.update_remind_info(instance.remind_info.get_default_self())

            return instance

        except KeyError as e:
            raise ValueError(f"In ExecutedTask[{task_number}] initialize error, {e}")
        except ValueError as e:
            raise ValueError(f"In ExecutedTask[{task_number}] initialize error, {e}")

    def update_scheduled_task_id(self, scheduled_task_id: ScheduledTaskId):
        """予定タスクIDを更新するメソッド"""
        if self.scheduled_task_id != scheduled_task_id:
            self._toggle_is_updated(
                UpdateContent(
                    key="予定タスクID",
                    original_value=str(self.scheduled_task_id),
                    update_value=str(scheduled_task_id),
                )
            )
            self.scheduled_task_id = scheduled_task_id
