import asyncio
from datetime import datetime, timedelta
from logging import Logger
from typing import List

import config as config
from util.converter import to_isoformat
from app_logger import AppLogger
from app_timer import AppTimer
from domain.executed_task_service import ExecutedTaskService
from domain.scheduled_task_service import ScheduledTaskService
from domain.executed_task import ExecutedTask
from domain.scheduled_task import ScheduledTask
from domain.task_service import TaskService
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
        self.scheduled_task_cache = ScheduledTaskCache(save_path=config.LOCAL_SCHEDULED_PICKLE_PATH)
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

        # 予定タスクをすべて取得する
        scheduled_tasks = await self.scheduled_task_repo.find_by_condition(
            condition=condition,
            on_error=lambda e, data: self.logger.error(
                f"予定タスク[{data['properties']['ID']['unique_id']['number']}]の取得に失敗。エラー内容: {e}"
            )
        )

        # 実績タスクを全て取得する
        executed_tasks = await self.executed_task_repo.find_by_condition(
            condition=condition,
            on_error=lambda e, data: self.logger.error(
                f"実績タスク[{data['properties']['ID']['unique_id']['number']}]の取得に失敗。エラー内容: {e}"
            )
        )

        # 実績タスクにIDを付与する(未付与のもののみ)
        ExecutedTaskService.add_id_tag(
            to=executed_tasks,
            source=scheduled_tasks
        )

        # 予定タスクに実績タスクを紐づける
        ScheduledTaskService.add_executed_tasks(
            scheduled_tasks=scheduled_tasks,
            executed_tasks=executed_tasks,
            on_error=lambda e, task: self.logger.error(
                f"予定タスク[{task.id.number}]と実績タスクの紐づけに失敗。エラー内容: {e}"
            ),
        )

        # 予定タスクにサブアイテムを紐づける
        ScheduledTaskService.add_child_tasks(
            child_tasks=scheduled_tasks,
            parent_tasks=scheduled_tasks,
            on_error=lambda e, task: self.logger.error(
                f"予定タスク[{task.id.number}]とサブアイテムの紐づけに失敗。エラー内容: {e}"
            ),
        )

        # 予定タスクの工数を計算
        for scheduled_task in scheduled_tasks:
            scheduled_task.aggregate_executed_man_hours()

        # サブアイテムに親ラベルを付与する
        for scheduled_task in scheduled_tasks:
            scheduled_task.update_child_tasks_properties()

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

        self.logger.debug(f"【処理時間】合計: {main_timer.get_elapsed_time()}秒")

        # pickleに保存する
        self.scheduled_task_cache.save(
            tasks=scheduled_tasks,
            on_success=lambda: self.logger.info("Pickleの保存に成功しました。"),
            on_error=lambda e: self.logger.error(f"Pickleの保存に失敗。エラー内容: {e}")
        )

        # pickleをGCSにアップロードする
        self.gcs_handler.upload(
            from_=self.scheduled_task_cache.save_path,
            to=config.BUCKET_SCHEDULED_PICKLE_PATH,
            on_success=lambda: self.logger.info("PickleのGCSへのアップロードに成功しました。"),
            on_error=lambda e: self.logger.error(f"PickleのGCSへのアップロードに失敗。エラー内容: {e}")
        )

        self.logger.info("処理時間: " + str(main_timer.get_elapsed_time()) + "秒")

    async def regular_task(self):
        '''予定タスクのIDを持つ実績タスクにIDを付与する'''

        main_timer = AppTimer.init_and_start()

        # バケットからPickleをダウンロードする
        self.gcs_handler.download(
            from_=config.BUCKET_SCHEDULED_PICKLE_PATH,
            to=self.scheduled_task_cache.save_path,
            on_success=lambda: self.logger.info("PickleのGCSからのダウンロードに成功しました。"),
            on_error=lambda e: self.logger.error(f"PickleのGCSからのダウンロードに失敗。エラー内容: {e}")
        )

        try:
            # コールバック関数を定義
            def handle_error(e): raise ValueError(e)

            # Pickleから予定タスクを読み込む
            cache_scheduled_tasks = self.scheduled_task_cache.load(
                on_success=lambda: self.logger.info("Pickleの読み込みに成功しました。"),
                on_error=handle_error
            )

        except Exception as e:
            self.logger.critical(f"Pickleの読み込みに失敗。エラー内容: {e}")
            self.logger.critical("処理を終了します。")
            return
        
        # 条件作成(最終更新日が1分前~現在。formatは`2025-05-09T14:40:00.000Z`ISO 8601形式)
        condition = TaskSearchCondition().and_(
            # 1分前~
            TaskSearchCondition().where_last_edited_time(
                operator=DateOperator.ON_OR_AFTER,
                date=to_isoformat(datetime.now() - timedelta(minutes=2))
            ),
            # ~現在
            TaskSearchCondition().where_last_edited_time(
                operator=DateOperator.ON_OR_BEFORE,
                date=to_isoformat(datetime.now())
            ),
        )
        
        fetch_scheduled_task_timer = AppTimer.init_and_start()

        # 条件にあう予定タスクを全て取得する
        fetched_scheduled_tasks: List[ScheduledTask] = await self.scheduled_task_repo.find_by_condition(
            condition=condition,
            on_error=lambda e, data: self.logger.error(
                f"予定タスク[{data['properties']['ID']['unique_id']['number']}]の取得に失敗。エラー内容: {e}"
            )
        )
        self.logger.debug(f"【処理時間】予定タスクの取得: {fetch_scheduled_task_timer.get_elapsed_time()}秒")
        self.logger.info(f"取得した予定タスクの数: {len(fetched_scheduled_tasks)}")

        fetch_executed_task_timer = AppTimer.init_and_start()
        # 条件にあう実績タスクを全て取得する
        fetched_executed_tasks: List[ExecutedTask] = await self.executed_task_repo.find_by_condition(
            condition=condition,
            on_error=lambda e, data: self.logger.error(
                f"実績タスク[{data['properties']['ID']['unique_id']['number']}]の取得に失敗。エラー内容: {e}"
            )
        )
        self.logger.debug(f"【処理時間】実績タスクの取得: {fetch_executed_task_timer.get_elapsed_time()}秒")
        self.logger.info(f"取得した実績タスクの数: {len(fetched_executed_tasks)}")

        add_executed_id_timer = AppTimer.init_and_start()

        all_scheduled_task_data = {
            scheduled_task.id.number: scheduled_task
            for scheduled_task in fetched_scheduled_tasks + cache_scheduled_tasks
        }

        # 実績タスクにIDを付与する(未付与のもののみ)
        updated_scheduled_tasks = ExecutedTaskService.get_tasks_add_id_tag(
            to=fetched_executed_tasks,
            source=all_scheduled_task_data.values()
        )

        self.logger.debug(f"【処理時間】実績タスクのID付与: {add_executed_id_timer.get_elapsed_time()}秒")
        calc_man_hours_timer = AppTimer.init_and_start()

        # 予定タスクと実績タスクの紐づけ
        ScheduledTaskService.add_executed_tasks(
            scheduled_tasks=all_scheduled_task_data.values(),
            executed_tasks=fetched_executed_tasks,
            on_error=lambda e, task: self.logger.error(
                f"予定タスク[{task.id.number}]と実績タスクの紐づけに失敗。エラー内容: {e}"
            ),
        )

        # キャッシュから予定タスクの親IDに一致する予定タスクを検索し、紐づける
        updated_parent_tasks = ScheduledTaskService.get_tasks_appended_child_tasks(
            child_tasks=fetched_scheduled_tasks,
            parent_tasks=all_scheduled_task_data.values(),
            on_error=lambda e, task: self.logger.error(
                f"予定タスク[{task.id.number}]とサブアイテムの紐づけに失敗。エラー内容: {e}"
            ),
        )
        
        # 更新予定のタスクを作成
        update_scheduled_task_data = {
            scheduled_task.id.number: scheduled_task
            for scheduled_task in fetched_scheduled_tasks + updated_parent_tasks + updated_scheduled_tasks
        }

        # 予定タスクの工数を計算
        for scheduled_task in update_scheduled_task_data.values():
            scheduled_task.aggregate_executed_man_hours()

        # サブアイテムに親ラベルを付与する
        for scheduled_task in update_scheduled_task_data.values():
            scheduled_task.update_child_tasks_properties()

        # 予定タスクが持つ実績タスクのプロパティを更新する
        for scheduled_task in update_scheduled_task_data.values():
            try:
                scheduled_task.update_executed_tasks_properties()
            except ValueError:
                self.logger.debug(
                    f"予定タスク[{scheduled_task.id.number}]の実績タスクが存在しませんでした。"
                )

        # 既存データを辞書に変換
        update_executed_task_data = {task.id.number: task for task in fetched_executed_tasks}

        # 更新データを上書き
        for scheduled_task in update_scheduled_task_data.values():
            for executed_task in scheduled_task.executed_tasks:
                update_executed_task_data[executed_task.id.number] = executed_task

        # 更新
        tasks = []
        tasks.append(self._update_scheduled_tasks(update_scheduled_task_data.values()))
        tasks.append(self._update_executed_tasks(update_executed_task_data.values()))

        await asyncio.gather(*tasks)

        # pickleに保存する
        self.scheduled_task_cache.save(
            tasks=all_scheduled_task_data,
            on_success=lambda: self.logger.info("Pickleの保存に成功しました。"),
            on_error=lambda e: self.logger.error(f"Pickleの保存に失敗。エラー内容: {e}")
        )

        # pickleをGCSにアップロードする
        self.gcs_handler.upload(
            from_=self.scheduled_task_cache.save_path,
            to=config.BUCKET_SCHEDULED_PICKLE_PATH,
            on_success=lambda: self.logger.info("PickleのGCSへのアップロードに成功しました。"),
            on_error=lambda e: self.logger.error(f"PickleのGCSへのアップロードに失敗。エラー内容: {e}")
        )

        self.logger.debug(f"【処理時間】実績タスクの工数計算: {calc_man_hours_timer.get_elapsed_time()}秒")
        self.logger.debug(f"【処理時間】合計: {main_timer.get_elapsed_time()}秒")
        
    async def _update_scheduled_tasks(self, scheduled_tasks: list[ScheduledTask],):
        '''予定タスクの実績工数を更新するメソッド'''
        updated_scheduled_tasks = TaskService.get_updated_tasks(scheduled_tasks)
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
        updated_executed_tasks = TaskService.get_updated_tasks(executed_tasks)
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
    # asyncio.run(service.daily_task())
    asyncio.run(service.regular_task())
    