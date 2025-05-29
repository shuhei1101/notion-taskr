from datetime import datetime
import json
from notiontaskr.application.dto.uptime_data import UptimeData, UptimeDataByTag
import pytest

from notiontaskr.domain.value_objects.tag import Tag

from notiontaskr.domain.value_objects.man_hours import ManHours


class TestUptimeData:
    def test_domainから初期化できること(self):
        tag = Tag("tag1")
        uptime = ManHours(5.0)
        from_ = datetime(2024, 1, 1)
        to = datetime(2024, 1, 31)

        uptime_data = UptimeData.from_domain(
            tag=tag,
            uptime=uptime,
            from_=from_,
            to=to,
        )

        assert uptime_data.tag == str(tag)
        assert uptime_data.uptime == float(uptime)
        assert uptime_data.from_ == from_
        assert uptime_data.to == to


class TestUptimeDataByTag:
    def test_タグと稼働時間を登録できること(self):
        tag = "tag1"
        uptime = 5.0
        from_ = datetime(2024, 1, 1)
        to = datetime(2024, 1, 31)

        uptime_data_by_tag = UptimeDataByTag.from_data(
            UptimeData(
                tag=tag,
                uptime=uptime,
                from_=from_,
                to=to,
            )
        )

        data = uptime_data_by_tag.get_data(tag=tag)
        assert data.tag == tag
        assert data.uptime == uptime

    def test_存在しないタグを指定した場合エラーが発生すること(self):
        tag = "tag1"
        uptime = 5.0
        from_ = datetime(2024, 1, 1)
        to = datetime(2024, 1, 31)

        uptime_data_by_tag = UptimeDataByTag.from_data(
            UptimeData(
                tag=tag,
                uptime=uptime,
                from_=from_,
                to=to,
            )
        )

        with pytest.raises(ValueError) as e:
            uptime_data_by_tag.get_data(tag="unknown_tag")

    def test_空の状態で初期化できること(self):
        uptime_data_by_tag = UptimeDataByTag.from_empty()

        # 空の状態で初期化されていることを確認
        assert uptime_data_by_tag.tag_uptimes_dict == {}

    def test_追加でデータを登録できること(self):
        tag = "tag1"
        uptime = 5.0
        from_ = datetime(2024, 1, 1)
        to = datetime(2024, 1, 31)

        uptime_data_by_tag = UptimeDataByTag.from_empty()
        uptime_data = UptimeData(
            tag=tag,
            uptime=uptime,
            from_=from_,
            to=to,
        )
        uptime_data_by_tag.insert_data(uptime_data)

        actual_data = uptime_data_by_tag.get_data(tag=tag)
        assert actual_data.tag == tag
        assert actual_data.uptime == uptime

    def test_既に存在するタグを指定した場合上書きされること(self):
        tag = "tag1"
        uptime1 = 5.0
        uptime2 = 10.0
        from_ = datetime(2024, 1, 1)
        to = datetime(2024, 1, 31)

        uptime_data_by_tag = UptimeDataByTag.from_empty()
        uptime_data_by_tag.insert_data(
            UptimeData(
                tag=tag,
                uptime=uptime1,
                from_=from_,
                to=to,
            )
        )
        uptime_data_by_tag.insert_data(
            UptimeData(
                tag=tag,
                uptime=uptime2,
                from_=from_,
                to=to,
            )
        )

        actual_data = uptime_data_by_tag.get_data(tag=tag)
        assert actual_data.tag == tag
        assert actual_data.uptime == uptime2

    def test_json形式での出力ができること(self):
        tag = "tag1"
        uptime = 5.0
        from_ = datetime(2024, 1, 1)
        to = datetime(2024, 1, 31)

        uptime_data_by_tag = UptimeDataByTag.from_data(
            UptimeData(
                tag=tag,
                uptime=uptime,
                from_=from_,
                to=to,
            )
        )

        expected_json = json.dumps(
            {
                tag: {
                    "合計工数": f"{uptime}h",
                    "対象期間": f"{from_.strftime('%Y/%m')} - {to.strftime('%Y/%m')}",
                }
            },
            ensure_ascii=False,
        )

        assert uptime_data_by_tag.to_json() == expected_json
