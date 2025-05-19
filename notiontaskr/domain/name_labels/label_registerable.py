from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from notiontaskr.domain.name_labels.id_label import IdLabel
    from notiontaskr.domain.name_labels.man_hours_label import ManHoursLabel
    from notiontaskr.domain.name_labels.parent_id_label import ParentIdLabel


class LabelRegisterable(ABC):
    """ラベルを登録するクラスのインターフェース"""

    @abstractmethod
    def register_id_label(self, label: "IdLabel"):
        """IDラベルを登録するメソッド"""
        pass

    @abstractmethod
    def register_man_hours_label(self, label: "ManHoursLabel"):
        """人時ラベルを登録するメソッド"""
        pass

    @abstractmethod
    def register_parent_id_label(self, label: "ParentIdLabel"):
        """親IDラベルを登録するメソッド"""
        pass
