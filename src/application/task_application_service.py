from logging import Logger
from typing import List

from app_logger import AppLogger
from app_timer import AppTimer
import config as config
from domain.executed_task_service import ExecutedTaskService
from domain.scheduled_task_service import ScheduledTaskService
from domain.executed_task import ExecutedTask
from domain.scheduled_task import ScheduledTask
from domain.task_service import TaskService
from infrastructure.executed_task_repository import ExecutedTaskRepository
from infrastructure.scheduled_task_repository import ScheduledTaskRepository
from infrastructure.operator import *
from infrastructure.task_search_condition import TaskSearchConditions
from datetime import datetime

class TaskApplicationService:
    def __init__(self, logger: Logger=AppLogger()):
        self.logger = logger
        self.executed_task_repo = ExecutedTaskRepository(
            config.NOTION_TOKEN, 
            config.TASK_DB_ID
        )
        self.scheduled_task_repo = ScheduledTaskRepository(
            config.NOTION_TOKEN, 
            config.TASK_DB_ID
        )
        self.task_service = TaskService()
        self.scheduled_task_service = ScheduledTaskService()
        self.executed_task_service = ExecutedTaskService()

    def regular_task(self):
        '''予定タスクのIDを持つ実績タスクにIDを付与する'''

        app_timer = AppTimer()
        app_timer.start()

        # 条件作成（過去一ヶ月〜未来）
        condition = TaskSearchConditions().or_(
                TaskSearchConditions().where_date(
                    operator=DateOperator.PAST_MONTH,
                ),
                TaskSearchConditions().where_date(
                    date=datetime.now().strftime('%Y-%m-%d'),
                    operator=DateOperator.ON_OR_AFTER
                )
            )
        
        # 条件にあう予定タスクを全て取得する
        scheduled_tasks: List[ScheduledTask] = self.scheduled_task_repo.find_by_condition(
            condition=condition,
            on_error=lambda e, data: self.logger.error(
                f"予定タスク[{data['properties']['ID']['unique_id']['number']}]の取得に失敗。エラー内容: {e}"
            )
        )

        # 予定タスク名を配列に格納する（タグ部分と頭と末尾の空白を除去）
        scheduled_task_names = list(map(
            lambda task: task.name.task_name,
            scheduled_tasks
        ))

        # 予定タスクIDを配列に格納する
        scheduled_task_ids = list(map(
            lambda task: task.id.number,
            scheduled_tasks
        ))

        # 予定タスク名に一致する実績タスクを全て取得する
        # （一回のクエリで全て取得する）
        executed_tasks: List[ExecutedTask] = self.executed_task_repo.find_by_condition(
            TaskSearchConditions().or_(
                *(
                    map(
                        lambda name: TaskSearchConditions().where_name(
                            operator=TextOperator.EQUALS,
                            name=name
                        ),
                        scheduled_task_names
                    )
                ),
                *(
                    map(
                        lambda id: TaskSearchConditions().where_id(
                            id=id
                        ),
                        scheduled_task_ids
                    )
                )
            ),
            on_error=lambda e, data: self.logger.error(
                f"実績タスク[{data['properties']['ID']['unique_id']['number']}]の取得に失敗。エラー内容: {e}"
            )
        )

        # 実績タスクにIDを付与する（未付与のもののみ）
        self.executed_task_service.add_id_tag(
            to=executed_tasks,
            source=scheduled_tasks
        )

        # 更新
        self._update_executed_tasks(executed_tasks)

        # 予定タスクにIDが一致する実績タスクを追加する
        self.scheduled_task_service.add_executed_tasks_to_scheduled(
                to=scheduled_tasks,
                source=self.executed_task_repo.find_by_condition(
                    condition=condition,
                    on_error=lambda e, data: self.logger.error(
                        f"実績タスク[{data['properties']['ID']['unique_id']['number']}]の取得に失敗。エラー内容: {e}"
                    )
                ),
                on_error=lambda e, task: self.logger.error(
                    f"予定タスク[{task.id.number}]と実績タスクの紐づけに失敗。エラー内容: {e}"
                ),
            )

        # 予定タスクの工数を計算
        for scheduled_task in scheduled_tasks:
            scheduled_task.aggregate_executed_man_days()

        # 実績タスクの名前を更新する
        for scheduled_task in scheduled_tasks:
            scheduled_task.update_executed_task_name()

        # 更新
        self._update_scheduled_tasks(scheduled_tasks)
        self._update_executed_tasks([
            executed_task
            for scheduled_task in scheduled_tasks
            for executed_task in scheduled_task.executed_tasks
        ])

        # 経過時間を表示
        self.logger.info(
            f"処理時間: {app_timer.get_elapsed_time()}秒"
        )
        
    def _update_scheduled_tasks(self, scheduled_tasks: list[ScheduledTask],):
        '''予定タスクの実績工数を更新するメソッド'''
        updated_scheduled_tasks = self.task_service.get_updated_tasks(scheduled_tasks)
        for updated_scheduled_task in updated_scheduled_tasks:
            try:
                self.scheduled_task_repo.update(updated_scheduled_task)
                self.logger.info(f"予定タスク[{updated_scheduled_task.id.number}]を更新しました。")
            except Exception as e:
                self.logger.error(f"予定タスク[{updated_scheduled_task.id.number}]の更新に失敗しました。 エラー内容: {e}")

    def _update_executed_tasks(self, executed_tasks: list[ExecutedTask],):
        '''実績タスクの予定タスクIDを更新するメソッド'''
        updated_executed_tasks = self.task_service.get_updated_tasks(executed_tasks)
        for updated_executed_task in updated_executed_tasks:
            try:
                self.executed_task_repo.update(updated_executed_task)
                self.logger.info(f"実績タスク[{updated_executed_task.id.number}]を更新しました。")
            except Exception as e:
                self.logger.error(f"実績タスク[{updated_executed_task.id.number}]の更新に失敗しました。 エラー内容: {e}")

if __name__ == '__main__':
    service = TaskApplicationService()
    service.regular_task()
