import asyncio
from datetime import datetime, timedelta
from logging import Logger
from typing import List

import config as config
from app_logger import AppLogger
from app_timer import AppTimer
from domain.executed_task_service import ExecutedTaskService
from domain.scheduled_task_service import ScheduledTaskService
from domain.executed_task import ExecutedTask
from domain.scheduled_task import ScheduledTask
from domain.task_service import TaskService
from domain.value_objects.status import Status
from gcs_handler import GCSHandler
from infrastructure.executed_task_repository import ExecutedTaskRepository
from infrastructure.scheduled_task_repository import ScheduledTaskRepository
from infrastructure.operator import *
from infrastructure.task_search_condition import TaskSearchCondition
from infrastructure.scheduled_task_cache import ScheduledTaskCache

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
        self.scheduled_task_cache = ScheduledTaskCache()
        self.gcs_handler = GCSHandler(
            bucket_name=config.BUCKET_NAME,
            on_error=lambda e: self.logger.error(
                f"GCSの初期化に失敗。エラー内容: {e}",
            )
        )

    async def daily_task(self):
        '''毎日0時に実行されるタスク'''

        # notionから過去一年分の情報を取得し、Pickleに保存する

        main_timer = AppTimer.init_and_start()
        self.logger.info("実績タスクのキャッシュを更新します。")

        # 過去一年分の実績タスクを取得
        # 条件作成(過去一年~未来)
        condition = TaskSearchCondition().or_(
            TaskSearchCondition().where_date(
                operator=DateOperator.PAST_YEAR,
            ),
            TaskSearchCondition().where_date(
                date=datetime.now().strftime('%Y-%m-%d'),
                operator=DateOperator.ON_OR_AFTER
            ),
        )

        # 実績タスクを全て取得する
        executed_tasks = await self.executed_task_repo.find_by_condition(
            condition=condition,
            on_error=lambda e, data: self.logger.error(
                f"実績タスク[{data['properties']['ID']['unique_id']['number']}]の取得に失敗。エラー内容: {e}"
            )
        )

        # 予定タスクをすべて取得する
        scheduled_tasks = await self.scheduled_task_repo.find_by_condition(
            condition=condition,
            on_error=lambda e, data: self.logger.error(
                f"予定タスク[{data['properties']['ID']['unique_id']['number']}]の取得に失敗。エラー内容: {e}"
            )
        )

        # 予定タスクに実績タスクを紐づける
        self.scheduled_task_service.add_executed_tasks(
            to=scheduled_tasks,
            source=executed_tasks,
            on_error=lambda e, task: self.logger.error(
                f"予定タスク[{task.id.number}]と実績タスクの紐づけに失敗。エラー内容: {e}"
            ),
        )

        # pickleに保存する
        self.scheduled_task_cache.save(scheduled_tasks)

        # pickleをGCSにアップロードする
        self.gcs_handler.upload(
            from_=self.scheduled_task_cache.save_path,
            to=config.BUCKET_SCHEDULED_PICKLE_PATH,
            on_upload_error=lambda e: self.logger.error(
                f"PickleのGCSへのアップロードに失敗。エラー内容: {e}"
            )
        )

        self.logger.info("処理時間: " + str(main_timer.get_elapsed_time()) + "秒")

    async def regular_task(self, condition: TaskSearchCondition = None):
        '''予定タスクのIDを持つ実績タスクにIDを付与する'''

        main_timer = AppTimer.init_and_start()

        # バケットからPickleをダウンロードする
        self.gcs_handler.download(
            from_=config.BUCKET_SCHEDULED_PICKLE_PATH,
            to=self.scheduled_task_cache.save_path,
            on_download_error=lambda e: self.logger.error(
                f"PickleのGCSからのダウンロードに失敗。エラー内容: {e}"
            )
        )

        # Pickleから予定タスクを読み込む
        scheduled_tasks = self.scheduled_task_cache.load()

        # 条件作成(一分前~現在)
        if condition is None:
            condition = TaskSearchCondition().and_(
                    # 1分前~
                    TaskSearchCondition().where_date(
                        operator=DateOperator.ON_OR_AFTER,
                        date=(datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
                    ),
                    # ~現在
                    TaskSearchCondition().where_date(
                        operator=DateOperator.ON_OR_BEFORE,
                        date=datetime.now().strftime('%Y-%m-%d'),
                    ),
                )
        
        create_scheduled_timer = AppTimer.init_and_start()

        # 条件にあう予定タスクを全て取得する
        scheduled_tasks: List[ScheduledTask] = await self.scheduled_task_repo.find_by_condition(
            condition=condition,
            on_error=lambda e, data: self.logger.error(
                f"予定タスク[{data['properties']['ID']['unique_id']['number']}]の取得に失敗。エラー内容: {e}"
            )
        )

        self.logger.debug(f"【処理時間】予定タスクの取得: {create_scheduled_timer.get_elapsed_time()}秒")
        update_parent_id_timer = AppTimer.init_and_start()

        # 予定タスクの親アイテムの取得を行う
        tasks = []
        for scheduled_task in list(filter(lambda task: task.status != Status('完了'),
            scheduled_tasks)):
            if scheduled_task.parent_task_page_id is None: continue
            tasks.append(self.scheduled_task_service.update_parent_id(
                scheduled_task=scheduled_task,
                scheduled_tasks=scheduled_tasks,
                scheduled_task_repo=self.scheduled_task_cache,
                on_error=lambda e, task: self.logger.error(
                    f"予定タスク[{task.id.number}]の親アイテムの取得に失敗。エラー内容: {e}"
                )
            ))

        await asyncio.gather(*tasks)

        self.logger.debug(f"【処理時間】親アイテムの取得: {update_parent_id_timer.get_elapsed_time()}秒")
        add_executed_id_timer = AppTimer.init_and_start()

        # 予定タスク名を配列に格納する(タグ部分と頭と末尾の空白を除去)
        scheduled_task_names = list(map(
            lambda task: task.name.task_name,
            scheduled_tasks
        ))

        # 予定タスク名に一致する実績タスクを全て取得する(100件ずつ分割してリクエスト)
        executed_tasks: List[ExecutedTask] = []
        BATCH_SIZE = 100

        tasks = []
        for i in range(0, len(scheduled_task_names), BATCH_SIZE):
            batch_names = scheduled_task_names[i:i + BATCH_SIZE]
            executed_tasks = await self.executed_task_repo.find_by_condition(
                TaskSearchCondition().or_(
                    *(
                    map(
                        lambda name: TaskSearchCondition().where_name(
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

        # 実績タスクにIDを付与する(未付与のもののみ)
        self.executed_task_service.add_id_tag(
            to=executed_tasks,
            source=scheduled_tasks
        )

        # 非同期で更新
        asyncio.create_task(self._update_executed_tasks(executed_tasks))

        self.logger.debug(f"【処理時間】実績タスクのID付与: {add_executed_id_timer.get_elapsed_time()}秒")
        culc_man_hours_timer = AppTimer.init_and_start()

        # 予定タスクと実績タスクの紐づけ
        self.scheduled_task_service.add_executed_tasks(
            to=scheduled_tasks,
            source=await self.executed_task_repo.find_by_condition(
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
        tasks = []
        tasks.append(self._update_scheduled_tasks(scheduled_tasks))
        tasks.append(self._update_executed_tasks([
            executed_task
            for scheduled_task in scheduled_tasks
            for executed_task in scheduled_task.executed_tasks if scheduled_task.executed_tasks
        ]))

        await asyncio.gather(*tasks)

        self.logger.debug(f"【処理時間】実績タスクの工数計算: {culc_man_hours_timer.get_elapsed_time()}秒")
        self.logger.debug(f"【処理時間】合計: {main_timer.get_elapsed_time()}秒")
        
    async def _update_scheduled_tasks(self, scheduled_tasks: list[ScheduledTask],):
        '''予定タスクの実績工数を更新するメソッド'''
        updated_scheduled_tasks = self.task_service.get_updated_tasks(scheduled_tasks)
        tasks = []
        for updated_scheduled_task in updated_scheduled_tasks:
            tasks.append(self.scheduled_task_repo.update(
                scheduled_task=updated_scheduled_task,
                on_success=lambda task: self.logger.info(
                    f"予定タスク[{task.id.number}]の更新: {task.update_contents}"
                ),
                on_error=lambda e, task: self.logger.error(
                    f"予定タスク[{task.id.number}]の更新に失敗しました。 エラー内容: {e}"
                )
            ))
        await asyncio.gather(*tasks)

    async def _update_executed_tasks(self, executed_tasks: list[ExecutedTask],):
        '''実績タスクの予定タスクIDを更新するメソッド'''
        updated_executed_tasks = self.task_service.get_updated_tasks(executed_tasks)
        tasks = []
        for updated_executed_task in updated_executed_tasks:
            tasks.append(self.executed_task_repo.update(
                executed_task=updated_executed_task,
                on_success=lambda task: self.logger.info(
                    f"実績タスク[{task.id.number}]の更新: {task.update_contents}"
                ),
                on_error=lambda e, task: self.logger.error(
                    f"実績タスク[{task.id.number}]の更新に失敗しました。 エラー内容: {e}"
                )
            ))

        await asyncio.gather(*tasks)

if __name__ == '__main__':
    service = TaskApplicationService()
    # asyncio.run(service.regular_task())
    asyncio.run(service.daily_task())
    