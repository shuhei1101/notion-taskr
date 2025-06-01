from dataclasses import dataclass


@dataclass
class UpdateContent:
    """更新内容を表すクラス"""

    key: str
    original_value: str
    update_value: str

    def is_updated(self) -> bool:
        """更新されたかどうかを判定する"""
        return self.original_value != self.update_value
