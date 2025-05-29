import copy
from unittest.mock import Mock, patch
import pytest
from datetime import datetime, timedelta, timezone

from notiontaskr.domain.scheduled_task import ScheduledTask
from notiontaskr.domain.name_labels.parent_id_label import ParentIdLabel
from notiontaskr.domain.value_objects.status import Status
from notiontaskr.domain.value_objects.progress_rate import ProgressRate
from notiontaskr.domain.value_objects.man_hours import ManHours
from notiontaskr.domain.tags import Tags
from notiontaskr.domain.value_objects.tag import Tag
from notiontaskr.domain.executed_tasks import ExecutedTasks
from notiontaskr.domain.scheduled_tasks import ScheduledTasks

from notiontaskr.domain.value_objects.notion_date import NotionDate


class TestScheduledTask:
    class Test_from_response_data:
        def test_正常なレスポンスデータを渡したときに正常に初期化されること(self):
            data = {
                "id": "123",
                "properties": {
                    "名前": {"title": [{"plain_text": "タスク名"}]},
                    "タグ": {"multi_select": [{"name": "タグ1"}, {"name": "タグ2"}]},
                    "ID": {"unique_id": {"number": "1", "prefix": "ID1"}},
                    "ステータス": {"status": {"name": "完了"}},
                    "親アイテム": {
                        "relation": [
                            {"id": "parent_id_1"},
                        ]
                    },
                    "人時(予)": {"number": 5},
                    "人時(実)": {"number": 3},
                    "サブアイテム": {
                        "relation": [
                            {"id": "sub_task_id_1"},
                            {"id": "sub_task_id_2"},
                        ]
                    },
                    "進捗率": {"number": 80},
                    "日付": {"date": {"start": "2023-10-01", "end": None}},
                },
            }
            task = ScheduledTask.from_response_data(data)
            assert task.page_id.value == data["id"]
            assert (
                task.name.task_name
                == data["properties"]["名前"]["title"][0]["plain_text"]
            )
            assert task.tags == Tags.from_tags([Tag("タグ1"), Tag("タグ2")])
            assert task.id.number == data["properties"]["ID"]["unique_id"]["number"]
            assert (
                task.status.value == data["properties"]["ステータス"]["status"]["name"]
            )

        def test_レスポンスデータに必要なキーが存在しない場合にExceptionでキャッチできること(
            self,
        ):
            data = {
                "id": "123",
                "properties": {
                    # 必要なキーが欠けている
                    "名前": {"title": [{"plain_text": "タスク名"}]},
                    # 他のプロパティも必要に応じて追加
                },
            }

            with pytest.raises(Exception):
                ScheduledTask.from_response_data(data)

    class Test_update_executed_tasks_properties:
        def test_実績タスクのプロパティが更新されること(self):
            task = ScheduledTask(
                page_id=Mock(),
                name=Mock(),
                tags=Mock(),
                id=Mock(),
                status=Mock(),
                parent_task_page_id=None,
            )
            task.executed_tasks = ExecutedTasks.from_tasks([Mock(), Mock()])
            task.update_executed_tasks_properties()
            for executed_task in task.executed_tasks:
                executed_task.update_name.assert_called_once_with(task.name)  # type: ignore
                executed_task.update_status.assert_called_once_with(task.status)  # type: ignore
                executed_task.update_parent_task_page_id.assert_called_once_with(  # type: ignore
                    task.parent_task_page_id
                )

    class Test_update_sub_tasks_properties:
        def test_サブタスクのプロパティが更新されること(self):
            task = ScheduledTask(
                page_id=Mock(),
                name=Mock(),
                tags=Mock(),
                id=Mock(),
                status=Mock(),
                parent_task_page_id=None,
            )
            task.sub_tasks = ScheduledTasks.from_tasks([Mock(), Mock()])
            task.update_sub_tasks_properties()
            for sub_task in task.sub_tasks:
                sub_task.update_parent_id_label.assert_called_once_with(  # type: ignore
                    ParentIdLabel.from_property(parent_id=task.id)
                )  # type: ignore

    class Test__update_status_by_checking_executed_tasks:
        def test_実績タスクがない場合は処理を終了すること(self):
            task = ScheduledTask(
                page_id=Mock(),
                name=Mock(),
                tags=Mock(),
                id=Mock(),
                status=Mock(),
                parent_task_page_id=None,
            )
            task.executed_tasks = ExecutedTasks.from_empty()
            task.update_status = Mock()
            task._update_status_by_checking_executed_tasks()
            task.update_status.assert_not_called()

        def test_実績タスクの開始時間が現在時刻よりも前の場合はステータスを進行中にすること(
            self,
        ):
            now = datetime.now(timezone.utc)

            task = ScheduledTask(
                page_id=Mock(),
                name=Mock(),
                tags=Mock(),
                id=Mock(),
                status=Status.NOT_STARTED,
                parent_task_page_id=None,
            )
            task.executed_tasks = ExecutedTasks.from_tasks(
                [
                    Mock(
                        date=Mock(
                            start=now - timedelta(days=1),  # 「現在時刻 - 1日」を指定
                            end=None,
                        )
                    )
                ]
            )
            task.update_status = Mock()
            task._update_status_by_checking_executed_tasks()
            task.update_status.assert_called_once_with(Status.IN_PROGRESS)

        def test_実績タスクの終了時間が現在時刻よりも後の場合はステータスを未着手にすること(
            self,
        ):
            now = datetime.now(timezone.utc)

            task = ScheduledTask(
                page_id=Mock(),
                name=Mock(),
                tags=Mock(),
                id=Mock(),
                status=Status.IN_PROGRESS,
                parent_task_page_id=None,
            )
            task.executed_tasks = ExecutedTasks.from_tasks(
                [
                    Mock(
                        date=Mock(
                            start=now + timedelta(days=2),  # 「現在時刻 + 2日」を指定
                            end=now + timedelta(days=1),  # 「現在時刻 + 1日」を指定
                        )
                    )
                ]
            )
            task.update_status = Mock()
            task._update_status_by_checking_executed_tasks()
            task.update_status.assert_called_once_with(Status.NOT_STARTED)

    class Test_update_status_by_checking_properties:
        def test_自身のステータスが中止の場合は処理をしないこと(self):
            task = ScheduledTask(
                page_id=Mock(),
                name=Mock(),
                tags=Mock(),
                id=Mock(),
                status=Mock(),
                parent_task_page_id=None,
            )
            # update_id_labelをモック化
            task.update_id_label = Mock()

            task.status = Status.CANCELED
            task.update_status_by_checking_properties()
            task.update_id_label.assert_not_called()

        def test_全てのサブアイテムが完了している場合は親タスクを完了にすること(self):
            task = ScheduledTask(
                page_id=Mock(),
                name=Mock(),
                tags=Mock(),
                id=Mock(),
                status=Status.NOT_STARTED,
                parent_task_page_id=None,
            )
            task.sub_tasks = ScheduledTasks.from_tasks(
                [
                    Mock(status=Status.COMPLETED),
                    Mock(status=Status.COMPLETED),
                ]
            )
            task.update_status = Mock()
            task.update_status_by_checking_properties()
            task.update_status.assert_called_once_with(Status.COMPLETED)

        def test_一つでもサブアイテムが進行中の場合は親タスクを進行中にすること(
            self,
        ):
            task = ScheduledTask(
                page_id=Mock(),
                name=Mock(),
                tags=Mock(),
                id=Mock(),
                status=Status.NOT_STARTED,
                parent_task_page_id=None,
            )
            task.sub_tasks = ScheduledTasks.from_tasks(
                [
                    Mock(status=Status.COMPLETED),
                    Mock(status=Status.IN_PROGRESS),
                ]
            )
            task.update_status = Mock()
            task.update_status_by_checking_properties()
            task.update_status.assert_called_once_with(Status.IN_PROGRESS)

        def test_サブアイテムが全て未着手の場合は親タスクを未着手にすること(
            self,
        ):
            task = ScheduledTask(
                page_id=Mock(),
                name=Mock(),
                tags=Mock(),
                id=Mock(),
                status=Status.IN_PROGRESS,
                parent_task_page_id=None,
            )
            task.sub_tasks = ScheduledTasks.from_tasks(
                [
                    Mock(status=Status.NOT_STARTED),
                    Mock(status=Status.NOT_STARTED),
                ]
            )
            task.update_status = Mock()
            task.update_status_by_checking_properties()
            task.update_status.assert_called_once_with(Status.NOT_STARTED)

        def test_サブアイテムを進行中にした後に親アイテムを進行中にすること(
            self,
        ):
            task = ScheduledTask(
                page_id=Mock(),
                name=Mock(),
                tags=Mock(),
                id=Mock(),
                status=Status.NOT_STARTED,
                parent_task_page_id=None,
            )
            task.sub_tasks = ScheduledTasks.from_tasks(
                [
                    ScheduledTask(
                        page_id=Mock(),
                        name=Mock(),
                        tags=Mock(),
                        id=Mock(),
                        status=Status.NOT_STARTED,
                        parent_task_page_id=None,
                        executed_tasks=ExecutedTasks.from_tasks(
                            [
                                Mock(
                                    date=Mock(
                                        start=datetime.now(timezone.utc)
                                        - timedelta(days=1),
                                        end=None,
                                    )
                                )
                            ]
                        ),
                    ),
                ]
            )
            task.update_status_by_checking_properties()
            assert task.status == Status.IN_PROGRESS
            assert task.sub_tasks[0].status == Status.IN_PROGRESS

        def test_is_delayedがTrueの場合はステータスを遅延にすること(self):
            task = ScheduledTask(
                page_id=Mock(),
                name=Mock(),
                tags=Mock(),
                id=Mock(),
                status=Status.NOT_STARTED,
                parent_task_page_id=None,
                date=NotionDate(
                    start=datetime.now(timezone.utc)
                    - timedelta(days=2),  # 現在時刻より2日前を設定
                    end=None,  # 終了日はNoneに設定(startと同じ日付を想定)
                ),
            )
            task.update_status = Mock()
            task.update_status_by_checking_properties()
            task.update_status.assert_called_once_with(Status.DELAYED)

    class Test_calc_progress_rate:
        class Test_自身のステータスが完了の場合:
            def test_自身の進捗率を1にすること(self):
                task = ScheduledTask(
                    page_id=Mock(),
                    name=Mock(),
                    tags=Mock(),
                    id=Mock(),
                    status=Status.COMPLETED,
                    parent_task_page_id=None,
                )
                task.update_progress_rate = Mock()
                task.calc_progress_rate()
                task.update_progress_rate.assert_called_once_with(ProgressRate(1.0))

        class Test_サブアイテムがない場合:
            def test_進捗率を0にすること(self):
                task = ScheduledTask(
                    page_id=Mock(),
                    name=Mock(),
                    tags=Mock(),
                    id=Mock(),
                    status=Status.NOT_STARTED,
                    parent_task_page_id=None,
                )
                task.update_progress_rate = Mock()
                task.calc_progress_rate()
                task.update_progress_rate.assert_called_once_with(ProgressRate(0.0))

        class Test_その他の場合:
            def test_進捗率を計算して更新すること(self):
                task = ScheduledTask(
                    page_id=Mock(),
                    name=Mock(),
                    tags=Mock(),
                    id=Mock(),
                    status=Status.NOT_STARTED,
                    parent_task_page_id=None,
                )
                task.sub_tasks = ScheduledTasks.from_tasks(
                    [
                        Mock(
                            scheduled_man_hours=ManHours(5),
                            status=Status.COMPLETED,
                            executed_man_hours=ManHours(5),
                        ),
                        Mock(
                            scheduled_man_hours=ManHours(5),
                            status=Status.NOT_STARTED,
                            executed_man_hours=ManHours(5),
                        ),
                    ]
                )
                task.update_progress_rate = Mock()
                task.calc_progress_rate()
                task.update_progress_rate.assert_called_once_with(ProgressRate(0.5))

            def test_サブアイテムの予定人時合計が0の場合に進捗率を0にすること(self):
                """0で割ることを避けるための仕様"""
                task = ScheduledTask(
                    page_id=Mock(),
                    name=Mock(),
                    tags=Mock(),
                    id=Mock(),
                    status=Status.NOT_STARTED,
                    parent_task_page_id=None,
                )
                task.sub_tasks = ScheduledTasks.from_tasks(
                    [
                        Mock(
                            scheduled_man_hours=ManHours(0),
                            status=Status.COMPLETED,
                            executed_man_hours=ManHours(5),
                        ),
                        Mock(
                            scheduled_man_hours=ManHours(0),
                            status=Status.NOT_STARTED,
                            executed_man_hours=ManHours(5),
                        ),
                    ]
                )
                task.update_progress_rate = Mock()
                task.calc_progress_rate()
                task.update_progress_rate.assert_called_once_with(ProgressRate(0.0))

    class Test_update_progress_rate:
        def test_進捗率が異なる場合に更新されること(self):
            task = ScheduledTask(
                page_id=Mock(),
                name=Mock(),
                tags=Mock(),
                id=Mock(),
                status=Mock(),
                progress_rate=ProgressRate(0.0),  # 初期値を0に設定
            )
            task.update_progress_rate(ProgressRate(0.5))  # 進捗率を0.5に更新
            assert task.progress_rate == ProgressRate(0.5)

        def test_進捗率が同じ場合は更新されないこと(self):
            task = ScheduledTask(
                page_id=Mock(),
                name=Mock(),
                tags=Mock(),
                id=Mock(),
                status=Mock(),
                progress_rate=ProgressRate(0.5),  # 初期値を0.5に設定
            )
            task._toggle_is_updated = Mock()
            task.update_progress_rate(ProgressRate(0.5))  # 進捗率を0.5に更新
            task._toggle_is_updated.assert_not_called()  # 更新処理が呼ばれないことを確認

    class Test__aggregate_executed_man_hours:
        class Test_実績タスクがない場合:
            def test_0を返すこと(self):
                task = ScheduledTask(
                    page_id=Mock(),
                    name=Mock(),
                    tags=Mock(),
                    id=Mock(),
                    status=Mock(),
                    parent_task_page_id=None,
                    executed_tasks=ExecutedTasks.from_empty(),  # 実績タスクを空に設定
                )
                result = task._aggregate_executed_man_hours()
                assert result == ManHours(0)  # 0を返すことを確認

        class Test_実績タスクがある場合:
            def test_実績タスクの工数を集計して返すこと(self):
                task = ScheduledTask(
                    page_id=Mock(),
                    name=Mock(),
                    tags=Mock(),
                    id=Mock(),
                    status=Mock(),
                    parent_task_page_id=None,
                )
                executed_task1 = Mock()
                executed_task2 = Mock()

                executed_task1.man_hours = ManHours(2)
                executed_task2.man_hours = ManHours(3)
                task.executed_tasks = ExecutedTasks.from_tasks(
                    [executed_task1, executed_task2]
                )
                result = task._aggregate_executed_man_hours()

                # 実績タスクの工数を集計して返すことを確認
                assert result == ManHours(5)  # 2 + 3

    class Test_aggregate_man_hours:
        class Test_サブアイテムがない場合:
            def test_予定人時を更新しないこと(self):
                task = ScheduledTask(
                    page_id=Mock(),
                    name=Mock(),
                    tags=Mock(),
                    id=Mock(),
                    status=Mock(),
                    parent_task_page_id=None,
                )
                task.sub_tasks = ScheduledTasks.from_empty()  # サブアイテムを空に設定

                task.update_scheduled_man_hours = Mock()  # 対象のメソッドをモック化
                task.aggregate_man_hours()

                task.update_scheduled_man_hours.assert_not_called()  # 予定人時が更新されないことを確認

            def test_サブアイテムの有無にかかわらず実績人時の合計を更新すること(self):
                task = ScheduledTask(
                    page_id=Mock(),
                    name=Mock(),
                    tags=Mock(),
                    id=Mock(),
                    status=Mock(),
                    parent_task_page_id=None,
                )
                task.update_executed_man_hours = Mock()  # 対象のメソッドをモック化

                task.aggregate_man_hours()

                task.update_executed_man_hours.assert_called_once()  # 実績人時が更新されることを確認

    class Test_update_executed_man_hours:
        def test_実績人時が異なる場合に更新されること(self):
            task = ScheduledTask(
                page_id=Mock(),
                name=Mock(),
                tags=Mock(),
                id=Mock(),
                status=Mock(),
                parent_task_page_id=None,
                executed_man_hours=ManHours(0),  # 初期値を0に設定
            )
            task._toggle_is_updated = Mock()  # _toggle_is_updatedをモック化

            task.update_executed_man_hours(ManHours(5))  # 実績人時を5に更新
            assert task.executed_man_hours == ManHours(5)  # 更新されたことを確認
            task._toggle_is_updated.assert_called_once()  # _toggle_is_updatedが呼ばれることを確認

        def test_実績人時が同じ場合は更新されないこと(self):
            task = ScheduledTask(
                page_id=Mock(),
                name=Mock(),
                tags=Mock(),
                id=Mock(),
                status=Mock(),
                parent_task_page_id=None,
                executed_man_hours=ManHours(5),  # 初期値を5に設定
            )

            task._toggle_is_updated = Mock()

            task.update_executed_man_hours(ManHours(5))  # 実績人時を5に更新
            task._toggle_is_updated.assert_not_called()  # _toggle_is_updatedが呼ばれないことを確認

    class Test_update_scheduled_man_hours:
        def test予定人時が異なる場合に更新されること(self):
            task = ScheduledTask(
                page_id=Mock(),
                name=Mock(),
                tags=Mock(),
                id=Mock(),
                status=Mock(),
                parent_task_page_id=None,
                scheduled_man_hours=ManHours(0),  # 初期値を0に設定
            )
            task._toggle_is_updated = Mock()  # _toggle_is_updatedをモック化

            task.update_scheduled_man_hours(ManHours(5))  # 予定人時を5に更新
            assert task.scheduled_man_hours == ManHours(5)  # 更新されたことを確認
            task._toggle_is_updated.assert_called_once()  # _toggle_is_updatedが呼ばれることを確認

        def test予定人時が同じ場合は更新されないこと(self):
            task = ScheduledTask(
                page_id=Mock(),
                name=Mock(),
                tags=Mock(),
                id=Mock(),
                status=Mock(),
                parent_task_page_id=None,
                executed_man_hours=ManHours(5),  # 初期値を5に設定
            )

            task._toggle_is_updated = Mock()

            task.update_executed_man_hours(ManHours(5))  # 実績人時を5に更新
            task._toggle_is_updated.assert_not_called()  # _toggle_is_updatedが呼ばれないことを確認

    class Test_update_executed_tasks:
        def test_中身を確認せず実績タスクリストを更新すること(self):
            task = ScheduledTask(
                page_id=Mock(),
                name=Mock(),
                tags=Mock(),
                id=Mock(),
                status=Mock(),
                parent_task_page_id=None,
            )
            executed_task1 = Mock()
            executed_task2 = Mock()
            task.executed_tasks = ExecutedTasks.from_tasks(
                [executed_task1, executed_task2]
            )

            tmp_executed_tasks = ExecutedTasks.from_empty()
            task.update_executed_tasks(tmp_executed_tasks)

            assert (
                task.executed_tasks == tmp_executed_tasks
            )  # 実績タスクリストが更新されていることを確認

    class Test_update_sub_tasks:
        def test_中身を確認せずサブタスクリストを更新すること(self):
            task = ScheduledTask(
                page_id=Mock(),
                name=Mock(),
                tags=Mock(),
                id=Mock(),
                status=Mock(),
                parent_task_page_id=None,
            )
            sub_task1 = Mock()
            sub_task2 = Mock()
            task.sub_tasks = ScheduledTasks.from_tasks([sub_task1, sub_task2])

            tmp_sub_tasks = ScheduledTasks.from_empty()
            task.update_sub_tasks(tmp_sub_tasks)

            assert (
                task.sub_tasks == tmp_sub_tasks
            )  # 実績タスクリストが更新されていることを確認

    def test_現在時刻が予定時刻を超えているときにis_delayがTrueになること(self):
        task = ScheduledTask(
            page_id=Mock(),
            name=Mock(),
            tags=Mock(),
            id=Mock(),
            status=Status.NOT_STARTED,
            parent_task_page_id=None,
            date=NotionDate(
                start=datetime.now(timezone.utc)
                - timedelta(days=2),  # 現在時刻より2日前を設定
                end=None,  # 終了日はNoneに設定(startと同じ日付を想定)
            ),
        )

        assert task.is_delayed() is True
