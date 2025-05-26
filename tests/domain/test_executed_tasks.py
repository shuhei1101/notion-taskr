from notiontaskr.domain.executed_tasks import ExecutedTasks
from pytest import fixture

from notiontaskr.domain.executed_task import ExecutedTask
from notiontaskr.domain.value_objects.page_id import PageId
from notiontaskr.domain.task_name import TaskName
from notiontaskr.domain.value_objects.tag import Tag
from notiontaskr.domain.value_objects.notion_id import NotionId
from notiontaskr.domain.value_objects.status import Status
from notiontaskr.domain.tags import Tags
from notiontaskr.domain.value_objects.man_hours import ManHours


class TestExecutedTasks:

    @fixture
    def task1(self):
        return ExecutedTask(
            page_id=PageId("page_1"),
            name=TaskName(task_name="タスク1"),
            tags=Tags.from_tags([Tag("tag1"), Tag("tag2")]),
            id=NotionId("1"),
            status=Status.IN_PROGRESS,
            man_hours=ManHours(1.0),
            is_updated=True,
        )

    @fixture
    def task2(self):
        return ExecutedTask(
            page_id=PageId("page_2"),
            name=TaskName(task_name="タスク2"),
            tags=Tags.from_tags([Tag("tag2"), Tag("tag3")]),
            id=NotionId("2"),
            status=Status.COMPLETED,
            man_hours=ManHours(2.0),
            is_updated=False,
        )

    def test_空の状態で初期化できること(self):
        executed_tasks = ExecutedTasks.from_empty()
        assert executed_tasks is not None

    def test__len__メソッドで辞書の要素数を取得できること(self):
        executed_tasks = ExecutedTasks.from_empty()
        assert len(executed_tasks) == 0

    def test_実績タスク配列から初期化できること(self, task1: ExecutedTask):
        executed_tasks = ExecutedTasks.from_tasks([task1])
        assert executed_tasks is not None
        assert len(executed_tasks) == 1

    def test_実績タスクを追加できること(self, task1: ExecutedTask):
        executed_tasks = ExecutedTasks.from_empty()
        executed_tasks.append(task1)
        executed_tasks.append(task1)
        assert len(executed_tasks) == 2

    def test_extendメソッドでリストに自身を追加できること(
        self, task1: ExecutedTask, task2: ExecutedTask
    ):
        executed_tasks1 = ExecutedTasks.from_tasks([task1])
        executed_tasks2 = ExecutedTasks.from_tasks([task1, task2])
        executed_tasks1.extend(executed_tasks2)
        assert len(executed_tasks1) == 3

    def test_拡張for文が使えること(self, task1: ExecutedTask):
        executed_tasks = ExecutedTasks.from_tasks([task1])
        task_names = [str(task) for task in executed_tasks]
        assert task_names == [str(task1)]

    def test_実績タスクの工数の合計を取得できること(
        self, task1: ExecutedTask, task2: ExecutedTask
    ):
        executed_tasks = ExecutedTasks.from_tasks([task1, task2])
        total_man_hours = executed_tasks.get_total_man_hours()
        assert total_man_hours == task1.man_hours + task2.man_hours

    def test_添字で要素を取得できること(self, task1: ExecutedTask):
        executed_tasks = ExecutedTasks.from_tasks([task1])
        assert executed_tasks[0] == task1

    def test_変更されたタスクを取得できること(
        self, task1: ExecutedTask, task2: ExecutedTask
    ):
        scheduled_tasks = ExecutedTasks.from_tasks(
            [task1, task2]  # task1のみis_updated=True
        )
        assert task1 in scheduled_tasks.get_updated_tasks()

    def test_upsert_by_idメソッドでタスクを追加または更新できること(self):
        executed_tasks = ExecutedTasks.from_empty()
        task = ExecutedTask(
            page_id=PageId("page_1"),
            name=TaskName("タスク1"),
            tags=Tags.from_tags([Tag("tag1"), Tag("tag2")]),
            id=NotionId("1"),
            status=Status.IN_PROGRESS,
        )
        executed_tasks.upsert_by_id(task)
        executed_tasks.upsert_by_id(task)
        assert len(executed_tasks) == 1

    class Test_辞書関連:
        @fixture
        def executed_tasks(self, task1: ExecutedTask, task2: ExecutedTask):
            return ExecutedTasks.from_tasks([task1, task2])

        def test_id辞書を取得できること(self, executed_tasks: ExecutedTasks):
            executed_tasks_by_id = executed_tasks.get_tasks_by_id()
            assert executed_tasks_by_id[NotionId("1")] == executed_tasks[0]
            assert executed_tasks_by_id[NotionId("2")] == executed_tasks[1]

        def test_page_id辞書を取得できること(self, executed_tasks: ExecutedTasks):
            executed_tasks_by_page_id = executed_tasks.get_tasks_by_page_id()
            assert executed_tasks_by_page_id[PageId("page_1")] == executed_tasks[0]
            assert executed_tasks_by_page_id[PageId("page_2")] == executed_tasks[1]

        def test_tag辞書を取得できること(self, executed_tasks: ExecutedTasks):
            executed_tasks_by_tag = executed_tasks.get_tasks_by_tag(
                tags=Tags.from_tags([Tag("tag1"), Tag("tag2")])
            )
            assert len(executed_tasks_by_tag[Tag("tag1")]) == 1
            assert len(executed_tasks_by_tag[Tag("tag2")]) == 2

    class Test_辞書から初期化:
        @fixture
        def executed_tasks(self):
            return ExecutedTasks.from_tasks(
                [
                    ExecutedTask(
                        page_id=PageId("page_1"),  # ページIDは同じ
                        name=TaskName("タスク1"),
                        tags=Tags.from_tags([Tag("tag1"), Tag("tag2")]),
                        id=NotionId("1"),  # ページIDは同じ
                        status=Status.IN_PROGRESS,
                        is_updated=True,
                    ),
                    ExecutedTask(
                        page_id=PageId("page_1"),  # ページIDは同じ
                        name=TaskName("タスク2"),
                        tags=Tags.from_tags([Tag("tag2"), Tag("tag3")]),
                        id=NotionId("1"),  # ページIDは同じ
                        status=Status.COMPLETED,
                        is_updated=False,
                    ),
                ]
            )

        def test_id辞書から初期化できること(self, executed_tasks: ExecutedTasks):

            tasks_by_id = executed_tasks.get_tasks_by_id()
            new_executed_tasks = ExecutedTasks.from_tasks_by_id(tasks_by_id)

            # ２番目のタスクが上書きされていること
            assert len(new_executed_tasks) == 1
            assert new_executed_tasks[0].name == TaskName("タスク2")

        def test_page_id辞書から初期化できること(self, executed_tasks: ExecutedTasks):
            tasks_by_page_id = executed_tasks.get_tasks_by_page_id()
            new_executed_tasks = ExecutedTasks.from_tasks_by_page_id(tasks_by_page_id)

            # ２番目のタスクが上書きされていること
            assert len(new_executed_tasks) == 1
            assert new_executed_tasks[0].name == TaskName("タスク2")

    def test_taskのman_hoursを集計できること(self):
        scheduled_tasks = ExecutedTasks.from_tasks(
            [
                ExecutedTask(
                    page_id=PageId("page_1"),  # ページIDは同じ
                    name=TaskName("タスク1"),
                    tags=Tags.from_tags([Tag("tag1"), Tag("tag2")]),
                    id=NotionId("1"),  # ページIDは同じ
                    status=Status.IN_PROGRESS,
                    is_updated=True,
                    man_hours=ManHours(1.0),
                ),
                ExecutedTask(
                    page_id=PageId("page_1"),  # ページIDは同じ
                    name=TaskName("タスク2"),
                    tags=Tags.from_tags([Tag("tag2"), Tag("tag3")]),
                    id=NotionId("1"),  # ページIDは同じ
                    status=Status.COMPLETED,
                    is_updated=False,
                    man_hours=ManHours(1.0),
                ),
            ]
        )
        result_data = scheduled_tasks.sum_properties()
        assert result_data.man_hours == ManHours(2.0)
