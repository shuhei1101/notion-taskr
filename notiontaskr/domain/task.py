from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Optional

from notiontaskr.domain.name_labels.man_hours_label import ManHoursLabel
from notiontaskr.domain.name_labels.parent_id_label import ParentIdLabel
from notiontaskr.domain.task_name import TaskName
from notiontaskr.domain.update_content import UpdateContent
from notiontaskr.domain.update_contents import UpdateContents
from notiontaskr.domain.value_objects.notion_id import NotionId
from notiontaskr.domain.value_objects.page_id import PageId
from notiontaskr.domain.value_objects.parent_task_page_id import ParentTaskPageId
from notiontaskr.domain.value_objects.status import Status
from notiontaskr.domain.tags import Tags
from notiontaskr.domain.value_objects.notion_date import NotionDate
from notiontaskr.notifier.task_remind_info import TaskRemindInfo


if TYPE_CHECKING:
    from notiontaskr.domain.name_labels.id_label import IdLabel


@dataclass
class Task:
    """タスクモデル"""

    page_id: PageId
    name: TaskName
    tags: Tags
    id: NotionId
    status: Status
    remind_info: "TaskRemindInfo" = field(
        default_factory=lambda: TaskRemindInfo()
    )  # リマインド情報
    is_updated: bool = False
    parent_task_page_id: Optional["ParentTaskPageId"] = None  # 親タスクId
    update_contents: UpdateContents = field(
        default_factory=UpdateContents
    )  # 更新内容のリスト
    date: Optional["NotionDate"] = None

    def __init__(
        self,
        page_id: PageId,
        name: TaskName,
        tags: Tags,
        id: NotionId,
        status: Status,
        remind_info: "TaskRemindInfo" = TaskRemindInfo(),
    ):
        self.page_id = page_id
        self.name = name
        self.tags = tags
        self.id = id
        self.status = status
        self.is_updated = False
        self.parent_task_page_id = None
        self.remind_info = remind_info

    def _toggle_is_updated(self, content: UpdateContent):
        """is_updatedをトグルする"""
        self.update_contents.upsert(content)
        self.is_updated = self.update_contents.is_updated()

    def update_man_hours_label(self, label: "ManHoursLabel"):
        """工数ラベルを登録し、is_updatedをTrueにする"""
        if self.name.man_hours_label != label:
            self._toggle_is_updated(
                UpdateContent(
                    key="工数ラベル",
                    original_value=str(self.name.man_hours_label),
                    update_value=str(label),
                )
            )
            self.name.register_man_hours_label(label)

    def update_id_label(self, label: "IdLabel"):
        """IDラベルを登録し、is_updatedをTrueにする"""
        if self.name.id_label != label:
            self._toggle_is_updated(
                UpdateContent(
                    key="IDラベル",
                    original_value=str(self.name.id_label),
                    update_value=str(label),
                )
            )
            self.name.register_id_label(label)

    def update_parent_id_label(self, label: "ParentIdLabel"):
        """親IDラベルを更新する"""
        if self.name.parent_id_label != label:
            self._toggle_is_updated(
                UpdateContent(
                    key="親IDラベル",
                    original_value=str(self.name.parent_id_label),
                    update_value=str(label),
                )
            )
            self.name.register_parent_id_label(label)

    def update_name(self, name: TaskName):
        """タスク名を更新し、is_updatedをTrueにする"""
        if self.name != name:
            self._toggle_is_updated(
                UpdateContent(
                    key="タスク名",
                    original_value=str(self.name),
                    update_value=str(name),
                )
            )
            self.name = name

    def update_parent_task_page_id(
        self, parent_task_page_id: Optional[ParentTaskPageId]
    ):
        """親タスクIDを更新し、is_updatedをTrueにする"""
        if self.parent_task_page_id != parent_task_page_id:
            self._toggle_is_updated(
                UpdateContent(
                    key="親タスクID",
                    original_value=str(self.parent_task_page_id),
                    update_value=str(parent_task_page_id),
                )
            )
            self.parent_task_page_id = parent_task_page_id

    def update_scheduled_task_page_id(self, scheduled_task_page_id: PageId):
        """予定タスクページIDを更新するメソッド"""
        if self.scheduled_task_page_id != scheduled_task_page_id:
            self._toggle_is_updated(
                UpdateContent(
                    key="予定タスクページID",
                    original_value=str(self.scheduled_task_page_id),
                    update_value=str(scheduled_task_page_id),
                )
            )
            self.scheduled_task_page_id = scheduled_task_page_id

    def update_status(self, status: Status):
        """ステータスを更新し、is_updatedをTrueにする"""
        if self.status != status:
            self._toggle_is_updated(
                UpdateContent(
                    key="ステータス",
                    original_value=str(self.status),
                    update_value=str(status),
                )
            )
            self.status = status

    def update_remind_info(self, remind_info: "TaskRemindInfo"):
        """リマインド情報を更新し、is_updatedをTrueにする"""
        if self.remind_info != remind_info:
            self._toggle_is_updated(
                UpdateContent(
                    key="リマインド情報",
                    original_value=str(self.remind_info),
                    update_value=str(remind_info),
                )
            )
            self.remind_info = remind_info

    def __str__(self) -> str:
        return str(self.name)
