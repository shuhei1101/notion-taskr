from notiontaskr.domain.executed_tasks import ExecutedTasks
from pytest import fixture

from notiontaskr.domain.executed_task import ExecutedTask
from notiontaskr.domain.value_objects.page_id import PageId
from notiontaskr.domain.task_name import TaskName
from notiontaskr.domain.value_objects.tag import Tag
from notiontaskr.domain.value_objects.notion_id import NotionId
from notiontaskr.domain.value_objects.status import Status

from notiontaskr.domain.tags import Tags


class TestExecuted_tasks:

    @fixture
    def task1(self):
        return ExecutedTask(
            page_id=PageId("page_1"),
            name=TaskName(task_name="タスク1"),
            tags=Tags.from_tags([Tag("tag1"), Tag("tag2")]),
            id=NotionId("1"),
            status=Status.IN_PROGRESS,
        )

    @fixture
    def task2(self):
        return ExecutedTask(
            page_id=PageId("page_2"),
            name=TaskName(task_name="タスク2"),
            tags=Tags.from_tags([Tag("tag2"), Tag("tag3")]),
            id=NotionId("2"),
            status=Status.COMPLETED,
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

    class Test_辞書関連:
        @fixture
        def executed_tasks(self, task1: ExecutedTask, task2: ExecutedTask):
            return ExecutedTasks.from_tasks([task1, task2])

        def test_id辞書を取得できること(
            self,
            executed_tasks: ExecutedTasks,
            task1: ExecutedTask,
            task2: ExecutedTask,
        ):
            executed_tasks_by_id = executed_tasks.get_tasks_by_id()
            assert executed_tasks_by_id[NotionId("1")] == task1
            assert executed_tasks_by_id[NotionId("2")] == task2

        def test_page_id辞書を取得できること(
            self,
            executed_tasks: ExecutedTasks,
            task1: ExecutedTask,
            task2: ExecutedTask,
        ):
            executed_tasks_by_page_id = executed_tasks.get_tasks_by_page_id()
            assert executed_tasks_by_page_id[PageId("page_1")] == task1
            assert executed_tasks_by_page_id[PageId("page_2")] == task2

        def test_tag辞書を取得できること(
            self,
            executed_tasks: ExecutedTasks,
        ):
            executed_tasks_by_tag = executed_tasks.get_tasks_by_tag(
                tags=Tags.from_tags([Tag("tag1"), Tag("tag2")])
            )
            assert len(executed_tasks_by_tag[Tag("tag1")]) == 1
            assert len(executed_tasks_by_tag[Tag("tag2")]) == 2

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
