from notiontaskr.domain.name_labels.id_label import IdLabel
from notiontaskr.domain.value_objects.scheduled_task_id import ScheduledTaskId
from notiontaskr.domain.value_objects.notion_id import NotionId
from notiontaskr.domain.task_name import TaskName


class TestScheduledTaskId:
    def test_NotionIdクラスを継承していること(self):

        assert issubclass(ScheduledTaskId, NotionId)

    class Test_task_nameからインスタンスを初期化:
        def test_タスク名からインスタンスを生成できること(self):
            task_name = TaskName(
                task_name="タスク名", id_label=IdLabel(key="", value="123")
            )
            scheduled_task_id = ScheduledTaskId.from_task_name(task_name)
            assert scheduled_task_id is not None
            assert scheduled_task_id.number == "123"

        def test_タスク名にIDラベルがない場合はNoneを返すこと(self):
            task_name = TaskName(task_name="タスク名", id_label=None)
            scheduled_task_id = ScheduledTaskId.from_task_name(task_name)
            assert scheduled_task_id is None
