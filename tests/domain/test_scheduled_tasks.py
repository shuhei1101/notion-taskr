from notiontaskr.domain.scheduled_tasks import ScheduledTasks
from pytest import fixture

from notiontaskr.domain.scheduled_task import ScheduledTask
from notiontaskr.domain.value_objects.page_id import PageId
from notiontaskr.domain.task_name import TaskName
from notiontaskr.domain.value_objects.notion_id import NotionId
from notiontaskr.domain.value_objects.status import Status
from notiontaskr.domain.value_objects.tag import Tag
from notiontaskr.domain.tags import Tags

from notiontaskr.domain.value_objects.man_hours import ManHours


class TestScheduledTasks:
    @fixture
    def task1(self):
        return ScheduledTask(
            page_id=PageId("page_1"),
            name=TaskName("タスク1"),
            tags=Tags.from_tags([Tag("tag1"), Tag("tag2")]),
            id=NotionId("1"),
            status=Status.IN_PROGRESS,
            is_updated=True,
        )

    @fixture
    def task2(self):
        return ScheduledTask(
            page_id=PageId("page_2"),
            name=TaskName("タスク2"),
            tags=Tags.from_tags([Tag("tag2"), Tag("tag3")]),
            id=NotionId("2"),
            status=Status.COMPLETED,
            is_updated=False,
        )

    def test_空の状態で初期化できること(self):
        scheduled_tasks = ScheduledTasks.from_empty()
        assert scheduled_tasks is not None

    def test__len__メソッドで辞書の要素数を取得できること(self):
        scheduled_tasks = ScheduledTasks.from_empty()
        assert len(scheduled_tasks) == 0

    def test_スケジュールタスク配列から初期化できること(self, task1: ScheduledTask):
        scheduled_tasks = ScheduledTasks.from_tasks([task1])
        assert scheduled_tasks is not None
        assert len(scheduled_tasks) == 1

    def test_スケジュールタスクを追加できること(self, task1: ScheduledTask):
        scheduled_tasks = ScheduledTasks.from_empty()
        scheduled_tasks.append(task1)
        scheduled_tasks.append(task1)
        assert len(scheduled_tasks) == 2

    def test_extendメソッドでスケジュールタスクを追加できること(
        self, task1: ScheduledTask, task2: ScheduledTask
    ):
        scheduled_tasks = ScheduledTasks.from_empty()
        scheduled_tasks.extend(ScheduledTasks.from_tasks([task1, task2]))
        assert len(scheduled_tasks) == 2

    def test_拡張for文が使えること(self, task1: ScheduledTask):
        scheduled_tasks = ScheduledTasks.from_tasks([task1])
        task_names = [str(task) for task in scheduled_tasks]
        assert task_names == [str(task1)]

    def test_添字で要素を取得できること(self, task1: ScheduledTask):
        scheduled_tasks = ScheduledTasks.from_tasks([task1])
        assert scheduled_tasks[0] == task1

    def test_変更されたタスクを取得できること(
        self, task1: ScheduledTask, task2: ScheduledTask
    ):
        scheduled_tasks = ScheduledTasks.from_tasks(
            [task1, task2]  # task1のみis_updated=True
        )
        assert task1 in scheduled_tasks.get_updated_tasks()

    def test_タスクを追加または更新できること(self):
        task = ScheduledTask(
            page_id=PageId("page_1"),
            name=TaskName("タスク1"),
            tags=Tags.from_tags([Tag("tag1"), Tag("tag2")]),
            id=NotionId("1"),
            status=Status.IN_PROGRESS,
        )
        scheduled_tasks = ScheduledTasks.from_empty()
        scheduled_tasks.upsert_by_id(task)
        scheduled_tasks.upsert_by_id(task)
        assert len(scheduled_tasks) == 1

    class Test_辞書関連:
        @fixture
        def scheduled_tasks(self, task1: ScheduledTask, task2: ScheduledTask):
            return ScheduledTasks.from_tasks([task1, task2])

        def test_id辞書を取得できること(self, scheduled_tasks: ScheduledTasks):
            tasks_by_id = scheduled_tasks.get_tasks_by_id()
            assert len(tasks_by_id) == 2
            assert tasks_by_id[NotionId("1")] == scheduled_tasks[0]
            assert tasks_by_id[NotionId("2")] == scheduled_tasks[1]

        def test_page_id辞書を取得できること(self, scheduled_tasks: ScheduledTasks):
            tasks_by_page_id = scheduled_tasks.get_tasks_by_page_id()
            assert len(tasks_by_page_id) == 2
            assert tasks_by_page_id[PageId("page_1")] == scheduled_tasks[0]
            assert tasks_by_page_id[PageId("page_2")] == scheduled_tasks[1]

        def test_tag辞書を取得できること(self, scheduled_tasks: ScheduledTasks):
            tasks_by_tag = scheduled_tasks.get_tasks_by_tag(
                tags=Tags.from_tags([Tag("tag1"), Tag("tag2")])
            )
            assert len(tasks_by_tag[Tag("tag1")]) == 1
            assert len(tasks_by_tag[Tag("tag2")]) == 2

    class Test_辞書から初期化:
        @fixture
        def scheduled_tasks(self):
            return ScheduledTasks.from_tasks(
                [
                    ScheduledTask(
                        page_id=PageId("page_1"),  # ページIDは同じ
                        name=TaskName("タスク1"),
                        tags=Tags.from_tags([Tag("tag1"), Tag("tag2")]),
                        id=NotionId("1"),  # ページIDは同じ
                        status=Status.IN_PROGRESS,
                        is_updated=True,
                    ),
                    ScheduledTask(
                        page_id=PageId("page_1"),  # ページIDは同じ
                        name=TaskName("タスク2"),
                        tags=Tags.from_tags([Tag("tag2"), Tag("tag3")]),
                        id=NotionId("1"),  # ページIDは同じ
                        status=Status.COMPLETED,
                        is_updated=False,
                    ),
                ]
            )

        def test_id辞書から初期化できること(self, scheduled_tasks: ScheduledTasks):

            tasks_by_id = scheduled_tasks.get_tasks_by_id()
            new_scheduled_tasks = ScheduledTasks.from_tasks_by_id(tasks_by_id)

            # ２番目のタスクが上書きされていること
            assert len(new_scheduled_tasks) == 1
            assert new_scheduled_tasks[0].name == TaskName("タスク2")

        def test_page_id辞書から初期化できること(self, scheduled_tasks: ScheduledTasks):
            tasks_by_page_id = scheduled_tasks.get_tasks_by_page_id()
            new_scheduled_tasks = ScheduledTasks.from_tasks_by_page_id(tasks_by_page_id)

            # ２番目のタスクが上書きされていること
            assert len(new_scheduled_tasks) == 1
            assert new_scheduled_tasks[0].name == TaskName("タスク2")

    def test_taskの親IDラベルを更新できること(self):
        scheduled_tasks = ScheduledTasks.from_tasks(
            [
                ScheduledTask(
                    page_id=PageId("page_1"),  # ページIDは同じ
                    name=TaskName("タスク1"),
                    tags=Tags.from_tags([Tag("tag1"), Tag("tag2")]),
                    id=NotionId("1"),  # ページIDは同じ
                    status=Status.IN_PROGRESS,
                    is_updated=True,
                ),
                ScheduledTask(
                    page_id=PageId("page_1"),  # ページIDは同じ
                    name=TaskName("タスク2"),
                    tags=Tags.from_tags([Tag("tag2"), Tag("tag3")]),
                    id=NotionId("1"),  # ページIDは同じ
                    status=Status.COMPLETED,
                    is_updated=False,
                ),
            ]
        )
        parent_id = NotionId("1")
        scheduled_tasks.update_parent_id_label(parent_id=parent_id)
        assert scheduled_tasks[0].name.parent_id_label.value == str(  # type: ignore
            parent_id.number
        )
        assert scheduled_tasks[1].name.parent_id_label.value == str(  # type: ignore
            parent_id.number
        )

    def test_taskのman_hoursを集計できること(self):
        scheduled_tasks = ScheduledTasks.from_tasks(
            [
                ScheduledTask(
                    page_id=PageId("page_1"),  # ページIDは同じ
                    name=TaskName("タスク1"),
                    tags=Tags.from_tags([Tag("tag1"), Tag("tag2")]),
                    id=NotionId("1"),  # ページIDは同じ
                    status=Status.IN_PROGRESS,
                    is_updated=True,
                    scheduled_man_hours=ManHours(1.0),
                    executed_man_hours=ManHours(2.0),
                ),
                ScheduledTask(
                    page_id=PageId("page_1"),  # ページIDは同じ
                    name=TaskName("タスク2"),
                    tags=Tags.from_tags([Tag("tag2"), Tag("tag3")]),
                    id=NotionId("1"),  # ページIDは同じ
                    status=Status.COMPLETED,
                    is_updated=False,
                    scheduled_man_hours=ManHours(1.0),
                    executed_man_hours=ManHours(2.0),
                ),
            ]
        )
        result_data = scheduled_tasks.sum_properties()
        assert result_data.scheduled_man_hours == ManHours(2.0)
        assert result_data.executed_man_hours == ManHours(4.0)
