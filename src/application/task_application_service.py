from datetime import datetime
from logging import Logger
from typing import List

import config as config
from app_logger import AppLogger
from app_timer import AppTimer
from domain.executed_task_service import ExecutedTaskService
from domain.name_labels.parent_id_label import ParentIdLabel
from domain.scheduled_task_service import ScheduledTaskService
from domain.executed_task import ExecutedTask
from domain.scheduled_task import ScheduledTask
from domain.task_service import TaskService
from domain.value_objects.status import Status
from infrastructure.executed_task_repository import ExecutedTaskRepository
from infrastructure.scheduled_task_repository import ScheduledTaskRepository
from infrastructure.operator import *
from infrastructure.task_search_condition import TaskSearchConditions


class TaskApplicationService:
    def __init__(self, logger: Logger=AppLogger()):
        self.logger = logger
        self.executed_task_repo = ExecutedTaskRepository(
            config.NOTION_TOKEN,
            config.TASK_DB_ID,
        )
        self.scheduled_task_repo = ScheduledTaskRepository(
            config.NOTION_TOKEN,
            config.TASK_DB_ID,
        )
        self.task_service = TaskService()
        self.scheduled_task_service = ScheduledTaskService()
        self.executed_task_service = ExecutedTaskService()

    def regular_task(self, condition: TaskSearchConditions = None):
        '''予定タスクのIDを持つ実績タスクにIDを付与する'''

        main_timer = AppTimer.init_and_start()

        # 条件作成（過去一ヶ月〜未来）
        if condition is None:
            condition = TaskSearchConditions().or_(
                    TaskSearchConditions().where_date(
                        operator=DateOperator.PAST_YEAR,
                    ),
                    TaskSearchConditions().where_date(
                        date=datetime.now().strftime('%Y-%m-%d'),
                        operator=DateOperator.ON_OR_AFTER
                    ),
                )
        
        create_scheduled_timer = AppTimer.init_and_start()

        # 条件にあう予定タスクを全て取得する
        scheduled_tasks: List[ScheduledTask] = self.scheduled_task_repo.find_by_condition(
            condition=condition,
            on_error=lambda e, data: self.logger.error(
                f"予定タスク[{data['properties']['ID']['unique_id']['number']}]の取得に失敗。エラー内容: {e}"
            )
        )

        self.logger.debug(f"【処理時間】予定タスクの取得: {create_scheduled_timer.get_elapsed_time()}秒")
        update_parent_id_timer = AppTimer.init_and_start()

        # 予定タスクの親アイテムの取得を行う
        for scheduled_task in list(filter(lambda task: task.status != Status('完了'),
            scheduled_tasks)):
            if scheduled_task.parent_task_page_id is None: continue
            try:
                # 現在取得している予定タスクから親アイテムのページIDを取得し、実績タスクを取得する
                scheduled_task.parent_task = next(
                    filter(
                        lambda task: task.page_id == scheduled_task.parent_task_page_id,
                        scheduled_tasks
                    ),
                    None
                )

                # リポジトリから親アイテムのページIDを取得する
                if scheduled_task.parent_task is None:
                    scheduled_task.parent_task = self.scheduled_task_repo.find_by_page_id(
                        page_id=scheduled_task.parent_task_page_id,
                    )
                    # 取得した親アイテムをキャッシュとしてscheduled_taskに格納する
                    scheduled_tasks.append(scheduled_task.parent_task)
                    self.logger.debug(f"キャッシュとして予定タスク[{scheduled_task.parent_task.id.number}]を格納しました。")
            
                # 親アイテムラベルを更新する
                scheduled_task.update_parent_id_label(
                    parent_id_label=ParentIdLabel.from_property(
                        parent_id=scheduled_task.parent_task.id,
                    )
                )
                
            except Exception as e:
                self.logger.error(
                    f"予定タスク[{scheduled_task.id.number}]の親アイテムの取得に失敗。エラー内容: {e}"
                )
                continue

        self.logger.debug(f"【処理時間】親アイテムの取得: {update_parent_id_timer.get_elapsed_time()}秒")
        add_executed_id_timer = AppTimer.init_and_start()

        # 予定タスク名を配列に格納する（タグ部分と頭と末尾の空白を除去）
        scheduled_task_names = list(map(
            lambda task: task.name.task_name,
            scheduled_tasks
        ))

        # 予定タスクIDを配列に格納する
        # scheduled_task_ids = list(map(
        #     lambda task: task.id.number,
        #     scheduled_tasks
        # ))


        # 予定タスク名に一致する実績タスクを全て取得する（100件ずつ分割してリクエスト）
        executed_tasks: List[ExecutedTask] = []
        batch_size = 100

        for i in range(0, len(scheduled_task_names), batch_size):
            batch_names = scheduled_task_names[i:i + batch_size]
            batch_executed_tasks = self.executed_task_repo.find_by_condition(
                TaskSearchConditions().or_(
                    *(
                    map(
                        lambda name: TaskSearchConditions().where_name(
                        operator=TextOperator.EQUALS,
                        name=name
                        ),
                        batch_names
                    )
                    ),
                ),
                on_error=lambda e, data: self.logger.error(
                    f"実績タスク[{data['properties']['ID']['unique_id']['number']}]の取得に失敗。エラー内容: {e}"
                )
            )
            executed_tasks.extend(batch_executed_tasks)

        # 実績タスクにIDを付与する（未付与のもののみ）
        self.executed_task_service.add_id_tag(
            to=executed_tasks,
            source=scheduled_tasks
        )

        # 更新
        self._update_executed_tasks(executed_tasks)

        self.logger.debug(f"【処理時間】実績タスクのID付与: {add_executed_id_timer.get_elapsed_time()}秒")
        culc_man_hours_timer = AppTimer.init_and_start()

        # 予定タスクと実績タスクの紐づけ
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
            scheduled_task.aggregate_executed_man_hours()

        # 実績タスクのプロパティを予定タスクからコピーする
        for scheduled_task in scheduled_tasks:
            try:
                scheduled_task.update_executed_tasks_properties()
            except ValueError:
                self.logger.debug(
                    f"予定タスク[{scheduled_task.id.number}]の実績タスクが存在しませんでした。"
                )

        # 更新
        self._update_scheduled_tasks(scheduled_tasks)
        self._update_executed_tasks([
            executed_task
            for scheduled_task in scheduled_tasks
            for executed_task in scheduled_task.executed_tasks
        ])

        self.logger.debug(f"【処理時間】実績タスクの工数計算: {culc_man_hours_timer.get_elapsed_time()}秒")
        self.logger.debug(f"【処理時間】合計: {main_timer.get_elapsed_time()}秒")
        
    def _update_scheduled_tasks(self, scheduled_tasks: list[ScheduledTask],):
        '''予定タスクの実績工数を更新するメソッド'''
        updated_scheduled_tasks = self.task_service.get_updated_tasks(scheduled_tasks)
        for updated_scheduled_task in updated_scheduled_tasks:
            try:
                self.scheduled_task_repo.update(updated_scheduled_task)
                self.logger.info(f"予定タスク[{updated_scheduled_task.id.number}]の更新: {updated_scheduled_task.update_contents}")
            except Exception as e:
                self.logger.error(f"予定タスク[{updated_scheduled_task.id.number}]の更新に失敗しました。 エラー内容: {e}")

    def _update_executed_tasks(self, executed_tasks: list[ExecutedTask],):
        '''実績タスクの予定タスクIDを更新するメソッド'''
        updated_executed_tasks = self.task_service.get_updated_tasks(executed_tasks)
        for updated_executed_task in updated_executed_tasks:
            try:
                self.executed_task_repo.update(updated_executed_task)
                self.logger.info(f"実績タスク[{updated_executed_task.id.number}]の更新: {updated_executed_task.update_contents}")
            except Exception as e:
                self.logger.error(f"実績タスク[{updated_executed_task.id.number}]の更新に失敗しました。 エラー内容: {e}")

if __name__ == '__main__':
    service = TaskApplicationService()
    service.regular_task()
