from dataclasses import dataclass, field
from typing import Optional

from notiontaskr.domain.task import Task
from notiontaskr.domain.task_name import TaskName
from notiontaskr.domain.value_objects.man_hours import ManHours
from notiontaskr.domain.value_objects.notion_date import NotionDate
from notiontaskr.domain.value_objects.notion_id import NotionId
from notiontaskr.domain.value_objects.page_id import PageId
from notiontaskr.domain.value_objects.status import Status

from notiontaskr.domain.tags import Tags

from notiontaskr.domain.value_objects.tag import Tag

from notiontaskr.notifier.task_remind_info import TaskRemindInfo

from notiontaskr.domain.name_labels.remind_label import RemindLabel


@dataclass
class ExecutedTask(Task):
    """実績タスクモデル"""

    man_hours: ManHours = field(default_factory=lambda: ManHours(0))
    scheduled_task_id: Optional[NotionId] = None  # 紐づいている予定タスクのID
    scheduled_task_page_id: Optional[PageId] = None  # 紐づいている予定タスクのページID

    @classmethod
    def from_response_data(cls, data):
        """レスポンスデータからインスタンスを生成する

        :raise KeyError:
        :raise ValueError: レスポンスデータに必要なキーが存在しない場合
        """

        task_number = data["properties"]["ID"]["unique_id"]["number"]
        try:
            task_name = TaskName.from_raw_task_name(
                data["properties"]["名前"]["title"][0]["plain_text"]
            )

            start_date_str = data["properties"]["日付"]["date"]["start"]
            end_date_str = data["properties"]["日付"]["date"]["end"]
            notion_date = NotionDate.from_raw_date(
                start=start_date_str,
                end=end_date_str,
            )

            tags = Tags.from_empty()
            for tag in data["properties"]["タグ"]["multi_select"]:
                tags.append(Tag(tag["name"]))

            # リマインド情報の設定
            has_before_start = data["properties"]["開始前通知"]["checkbox"]
            has_before_end = data["properties"]["終了前通知"]["checkbox"]
            before_start_minutes = data["properties"]["開始前通知時間(分)"].get(
                "number"
            )
            before_end_minutes = data["properties"]["終了前通知時間(分)"].get("number")
            remind_info = TaskRemindInfo.from_raw_values(
                has_before_start=has_before_start,
                has_before_end=has_before_end,
                before_start_minutes=before_start_minutes,
                before_end_minutes=before_end_minutes,
            )

            instance = cls(
                page_id=PageId(data["id"]),
                name=task_name,
                tags=tags,
                id=NotionId(
                    number=task_number,
                    prefix=data["properties"]["ID"]["unique_id"]["prefix"],
                ),
                status=Status.from_str(
                    data["properties"]["ステータス"]["status"]["name"]
                ),
                date=notion_date,
                man_hours=ManHours.from_notion_date(notion_date),
                scheduled_task_id=(
                    NotionId(
                        number=task_name.id_label.value,
                    )
                    if task_name.id_label
                    else None
                ),
                parent_task_page_id=(
                    PageId(
                        value=data["properties"]["親アイテム(予)"]["relation"][0]["id"],
                    )
                    if data["properties"]["親アイテム(予)"]["relation"]
                    else None
                ),
                scheduled_task_page_id=(
                    PageId(
                        value=data["properties"]["予定タスク"]["relation"][0]["id"],
                    )
                    if data["properties"]["予定タスク"]["relation"]
                    else None
                ),
                remind_info=remind_info,
            )

            return instance

        except KeyError as e:
            raise ValueError(f"In ExecutedTask[{task_number}] initialize error, {e}")
        except ValueError as e:
            raise ValueError(f"In ExecutedTask[{task_number}] initialize error, {e}")

    def update_scheduled_task_id(self, scheduled_task_id: NotionId):
        """予定タスクIDを更新するメソッド"""
        if self.scheduled_task_id != scheduled_task_id:
            self._toggle_is_updated(
                f"予定タスクID: {self.scheduled_task_id} -> {scheduled_task_id}"
            )
            self.scheduled_task_id = scheduled_task_id
