from datetime import datetime, timezone

import pytest
from notiontaskr.domain.value_objects.notion_date import NotionDate


class TestNotionDate:
    class Test_initメソッド:
        def test_引数dateがdatetimeのとき正常に初期化されること(self):
            date = NotionDate(datetime(2023, 1, 1), datetime(2023, 1, 2))
            assert date.start == datetime(2023, 1, 1, tzinfo=timezone.utc)
            assert date.end == datetime(2023, 1, 2, tzinfo=timezone.utc)

        def test_引数startがNoneのときTypeErrorが発生すること(self):
            with pytest.raises(TypeError):
                NotionDate(None, datetime(2023, 1, 2))  # type: ignore

        def test_引数endがNoneのときendにstartが代入されること(self):
            date = NotionDate(datetime(2023, 1, 1), None)  # type: ignore
            assert date.start == datetime(2023, 1, 1, tzinfo=timezone.utc)
            assert date.end == datetime(
                2023, 1, 1, 23, 59, 59, 999999, tzinfo=timezone.utc
            )

        def test_引数startがendよりも後のときValueErrorが発生すること(self):
            with pytest.raises(ValueError):
                NotionDate(datetime(2023, 1, 2), datetime(2023, 1, 1))

    class Test_from_raw_dateメソッド:
        def test_引数startがNoneのときValueErrorが発生すること(self):
            with pytest.raises(ValueError):
                NotionDate.from_raw_date(None, "2023-01-02")  # type: ignore

        def test_引数endがNoneのときendにstartが代入されること(self):
            date = NotionDate.from_raw_date("2023-01-01", None)  # type: ignore
            assert date.start == datetime(2023, 1, 1, tzinfo=timezone.utc)
            assert date.end == datetime(
                2023, 1, 1, 23, 59, 59, 999999, tzinfo=timezone.utc
            )

        def test_引数startがISOフォーマットの文字列のとき正常に初期化されること(self):
            date = NotionDate.from_raw_date("2023-01-01", "2023-01-02")
            assert date.start == datetime(2023, 1, 1, tzinfo=timezone.utc)
            assert date.end == datetime(2023, 1, 2, tzinfo=timezone.utc)

        def test_引数startがISOフォーマットでない文字列のときValueErrorが発生すること(
            self,
        ):
            with pytest.raises(ValueError):
                NotionDate.from_raw_date("2023/01/01", "2023/01/02")

    class Test_notionのresponse_dataからのインスタンス生成:
        """例:

        start_date_str = data["properties"]["日付"]["date"]["start"]
        end_date_str = data["properties"]["日付"]["date"]["end"]
        notion_date = NotionDate.from_raw_date(
            start=start_date_str,
            end=end_date_str,
        )
        """

        def test_正しい形式のresponse_dataからNotionDateを生成できること(self):
            response_data = {
                "properties": {
                    "日付": {
                        "date": {
                            "start": "2023-01-01T00:00:00Z",
                            "end": "2023-01-02T00:00:00Z",
                        }
                    }
                }
            }
            notion_date = NotionDate.from_response_data(response_data)
            assert notion_date.start == datetime(2023, 1, 1, tzinfo=timezone.utc)
            assert notion_date.end == datetime(2023, 1, 2, tzinfo=timezone.utc)

        def test_response_dataに日付情報がない場合はValueErrorを発生させること(
            self,
        ):
            response_data = {"properties": {"日付": {}}}
            with pytest.raises(ValueError):
                NotionDate.from_response_data(response_data)
