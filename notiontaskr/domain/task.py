from dataclasses import dataclass
from typing import TYPE_CHECKING, List

from notiontaskr.domain.name_labels.man_hours_label import ManHoursLabel
from notiontaskr.domain.name_labels.parent_id_label import ParentIdLabel
from notiontaskr.domain.task_name import TaskName
from notiontaskr.domain.value_objects.notion_id import NotionId
from notiontaskr.domain.value_objects.page_id import PageId
from notiontaskr.domain.value_objects.status import Status
from notiontaskr.domain.value_objects.tag import Tag

if TYPE_CHECKING:
    from notiontaskr.domain.name_labels.id_label import IdLabel


@dataclass
class Task:
    """タスクモデル"""

    page_id: PageId
    name: TaskName
    tags: List[Tag]
    is_updated: bool = False
    id: NotionId = None
    status: Status = None
    parent_task_page_id: "PageId" = None  # 親タスクId
    update_contents: List[str] = None  # （デバッグ用）更新内容を保存

    def __init__(
        self,
        page_id: PageId,
        name: TaskName,
        tags: List[Tag],
        id: NotionId = None,
        status: Status = None,
    ):
        self.page_id = page_id
        self.name = name
        self.tags = tags
        self.id = id
        self.status = status

    def _toggle_is_updated(self, update_message: str):
        """is_updatedをトグルする"""
        if not self.update_contents:
            self.update_contents = []
        self.is_updated = True
        self.update_contents.append(update_message)

    def update_man_hours_label(self, man_hours_label: "ManHoursLabel"):
        """工数ラベルを登録し、is_updatedをTrueにする"""
        if self.name.man_hours_label != man_hours_label:
            self._toggle_is_updated(
                f"工数ラベル: {self.name.man_hours_label} -> {man_hours_label}"
            )
            self.name.man_hours_label = man_hours_label

    def update_id_label(self, label: "IdLabel"):
        """IDラベルを登録し、is_updatedをTrueにする"""
        if self.name.id_label != label:
            self._toggle_is_updated(f"IDラベル: {self.name.id_label} -> {label}")
            self.name.id_label = label

    def update_parent_id_label(self, parent_id_label: "ParentIdLabel"):
        """親IDラベルを更新する"""
        if self.name.parent_id_label != parent_id_label:
            self._toggle_is_updated(
                f"親IDラベル: {self.name.parent_id_label} -> {parent_id_label}"
            )
            self.name.parent_id_label = parent_id_label

    def check_sub_task_status(self, status: Status):
        """ステータスを更新し、is_updatedをTrueにする"""
        if self.status != status:
            self._toggle_is_updated(f"ステータス: {self.status} -> {status}")
            self.status = status

    def update_name(self, name: TaskName):
        """タスク名を更新し、is_updatedをTrueにする"""
        if self.name != name:
            self._toggle_is_updated(f"タスク名: {self.name} -> {name}")
            self.name = name

    def update_parent_task_page_id(self, parent_task_page_id: PageId):
        """親タスクIDを更新し、is_updatedをTrueにする"""
        if self.parent_task_page_id != parent_task_page_id:
            self._toggle_is_updated(
                f"親タスクID: {self.parent_task_page_id} -> {parent_task_page_id}"
            )
            self.parent_task_page_id = parent_task_page_id

    def update_scheduled_task_page_id(self, scheduled_task_page_id: PageId):
        """予定タスクページIDを更新するメソッド"""
        if self.scheduled_task_page_id != scheduled_task_page_id:
            self._toggle_is_updated(
                f"予定タスクページID: {self.scheduled_task_page_id} -> {scheduled_task_page_id}"
            )
            self.scheduled_task_page_id = scheduled_task_page_id

    def update_status(self, status: Status):
        """ステータスを更新し、is_updatedをTrueにする"""
        if self.status != status:
            self._toggle_is_updated(f"ステータス: {self.status} -> {status}")
            self.status = status

    def get_display_name(self) -> str:
        """表示用のタスク名を取得する

        :return: 表示用のタスク名
        """
        return str(self.name)
