from abc import ABC, abstractmethod
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from notiontaskr.domain.name_labels.id_label import IdLabel
    from notiontaskr.domain.name_labels.man_hours_label import ManHoursLabel
    from notiontaskr.domain.name_labels.parent_id_label import ParentIdLabel
    from notiontaskr.domain.name_labels.remind_label import RemindLabel


class LabelRegisterable(ABC):
    """ラベルを登録するクラスのインターフェース"""

    @abstractmethod
    def register_id_label(self, label: "IdLabel"):
        """IDラベルを登録するメソッド"""
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def register_man_hours_label(self, label: "ManHoursLabel"):
        """人時ラベルを登録するメソッド"""
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def register_parent_id_label(self, label: "ParentIdLabel"):
        """親IDラベルを登録するメソッド"""
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def register_remind_label(self, label: "RemindLabel"):
        """リマインドラベルを登録するメソッド"""
        raise NotImplementedError("Subclasses must implement this method.")
