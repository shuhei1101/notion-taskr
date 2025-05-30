from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Optional

from notiontaskr.domain.name_labels.man_hours_label import ManHoursLabel
from notiontaskr.domain.name_labels.parent_id_label import ParentIdLabel
from notiontaskr.domain.task_name import TaskName
from notiontaskr.domain.value_objects.notion_id import NotionId
from notiontaskr.domain.value_objects.page_id import PageId
from notiontaskr.domain.value_objects.status import Status
from notiontaskr.domain.tags import Tags
from notiontaskr.domain.value_objects.notion_date import NotionDate
from notiontaskr.notifier.task_remind_info import TaskRemindInfo


if TYPE_CHECKING:
    from notiontaskr.domain.name_labels.id_label import IdLabel
    from notiontaskr.domain.name_labels.remind_label import RemindLabel


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
    parent_task_page_id: Optional["PageId"] = None  # 親タスクId
    update_contents: List[str] = field(
        default_factory=list  # 生成時に空のリストを作成(他インスタンスとの共有を避けるため)
    )  # （デバッグ用）更新内容を保存
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
        self.update_contents = []
        self.remind_info = remind_info

    def _toggle_is_updated(self, update_message: str):
        """is_updatedをトグルする"""
        if not self.update_contents:
            self.update_contents = []
        self.is_updated = True
        self.update_contents.append(update_message)

    def update_man_hours_label(self, label: "ManHoursLabel"):
        """工数ラベルを登録し、is_updatedをTrueにする"""
        if self.name.man_hours_label != label:
            self._toggle_is_updated(
                f"工数ラベル: {self.name.man_hours_label} -> {label}"
            )
            self.name.register_man_hours_label(label)

    def update_id_label(self, label: "IdLabel"):
        """IDラベルを登録し、is_updatedをTrueにする"""
        if self.name.id_label != label:
            self._toggle_is_updated(f"IDラベル: {self.name.id_label} -> {label}")
            self.name.register_id_label(label)

    def update_parent_id_label(self, label: "ParentIdLabel"):
        """親IDラベルを更新する"""
        if self.name.parent_id_label != label:
            self._toggle_is_updated(
                f"親IDラベル: {self.name.parent_id_label} -> {label}"
            )
            self.name.register_parent_id_label(label)

    def update_name(self, name: TaskName):
        """タスク名を更新し、is_updatedをTrueにする"""
        if self.name != name:
            self._toggle_is_updated(f"タスク名: {self.name} -> {name}")
            self.name = name

    def update_parent_task_page_id(self, parent_task_page_id: Optional[PageId]):
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

    def update_remind_label(self, label: "RemindLabel"):
        """リマインドラベルを更新し、is_updatedをTrueにする"""
        if self.name.remind_label != label:
            self._toggle_is_updated(
                f"リマインドラベル: {self.name.remind_label} -> {label}"
            )
            self.name.register_remind_label(label)

    def get_display_name(self) -> str:
        """表示用のタスク名を取得する

        :return: 表示用のタスク名
        """
        return str(self.name)

    def is_remind_time_before_start(self) -> bool:
        """現在時刻が開始前リマインド時刻かどうか"""
        return self.remind_info.is_remind_time_before_start()

    def is_remind_time_before_end(self) -> bool:
        """現在時刻が終了前リマインド時刻かどうか"""
        return self.remind_info.is_remind_time_before_end()
