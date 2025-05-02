


from domain.executed_task import ExecutedTask
from infrastructure.task_update_properties import TaskUpdateProperties


class ExecutedTaskUpdateProperties(TaskUpdateProperties):
    '''実績タスクの更新用プロパティ辞書を生成するクラス'''

    def __init__(self, task: ExecutedTask):
        super().__init__(task)
        self.task = task
