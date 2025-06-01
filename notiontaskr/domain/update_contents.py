from dataclasses import dataclass, field

from notiontaskr.domain.update_content import UpdateContent


@dataclass
class UpdateContents:
    _contents: list[UpdateContent] = field(default_factory=list[UpdateContent])

    def is_updated(self) -> bool:
        """更新されたかどうかを判定する"""
        return any(content.is_updated() for content in self._contents)

    def upsert(self, content: UpdateContent):
        """更新内容を追加または変更する"""
        for existing_content in self._contents:
            if existing_content.key == content.key:
                existing_content.update_value = content.update_value
                return
        self._contents.append(content)

    def __getitem__(self, index: int) -> UpdateContent:
        """インデックスで要素にアクセスする"""
        return self._contents[index]

    def __len__(self) -> int:
        """要素数を返す"""
        return len(self._contents)

    def __str__(self) -> str:
        """文字列表現を返す

        例: "[ステータス]: 未着手 -> 進行中, [優先度]: 低 -> 高"
        """
        return ", ".join(
            f"[{content.key}]: {content.original_value} -> {content.update_value}"
            for content in self._contents
        )
