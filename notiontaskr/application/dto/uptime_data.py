from dataclasses import dataclass
from datetime import datetime
import json

from notiontaskr.domain.value_objects.tag import Tag
from notiontaskr.domain.value_objects.man_hours import ManHours


@dataclass
class UptimeData:
    """タグごとの稼働実績を格納するDTO"""

    tag: str
    uptime: float
    from_: datetime
    to: datetime

    @classmethod
    def from_domain(
        cls, tag: Tag, uptime: ManHours, from_: datetime, to: datetime
    ) -> "UptimeData":
        """ドメインからDTOを生成する"""
        return cls(tag=str(tag), uptime=float(uptime), from_=from_, to=to)


@dataclass
class UptimeDataByTag:
    """稼働実績を格納するDTO"""

    tag_uptimes_dict: dict[str, UptimeData]

    @classmethod
    def from_empty(cls) -> "UptimeDataByTag":
        """空の状態で初期化する"""
        return cls(tag_uptimes_dict={})

    def get_data(self, tag: str) -> "UptimeData":
        """指定したタグの稼働実績を取得する"""
        if tag not in self.tag_uptimes_dict:
            raise ValueError(f"指定したタグ '{tag}' の稼働実績が存在しません。")
        return self.tag_uptimes_dict[tag]

    @classmethod
    def from_data(cls, data: UptimeData) -> "UptimeDataByTag":

        return cls(tag_uptimes_dict={data.tag: data})

    def insert_data(self, data: UptimeData) -> None:
        """データを追加する"""
        self.tag_uptimes_dict[data.tag] = data

    def to_json(self) -> str:
        """JSON形式で出力する"""
        return json.dumps(
            {
                tag: {
                    "合計工数": f"{data.uptime}h",
                    "対象期間": f"{data.from_.strftime('%Y/%m')} - {data.to.strftime('%Y/%m')}",
                }
                for tag, data in self.tag_uptimes_dict.items()
            },
            ensure_ascii=False,
        )
