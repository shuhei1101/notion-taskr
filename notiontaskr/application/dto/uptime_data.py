from dataclasses import dataclass
import json


@dataclass
class UptimeData:
    """タグごとの稼働実績を格納するDTO"""

    tag: str
    uptime: float


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
                    "tag": tag,
                    "uptime": data.uptime,
                }
                for tag, data in self.tag_uptimes_dict.items()
            },
            ensure_ascii=False,
        )
