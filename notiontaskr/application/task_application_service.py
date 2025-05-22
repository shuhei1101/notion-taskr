import asyncio
from datetime import datetime, timedelta, timezone
from typing import List

import notiontaskr.config as config
from notiontaskr.util.converter import dt_to_month_start_end, to_isoformat
from notiontaskr.app_logger import AppLogger
from notiontaskr.app_timer import AppTimer
from notiontaskr.gcs_handler import GCSHandler
from notiontaskr.domain.name_labels.man_hours_label import ManHoursLabel
from notiontaskr.domain.executed_task_service import ExecutedTaskService
from notiontaskr.domain.scheduled_task_service import ScheduledTaskService
from notiontaskr.domain.executed_task import ExecutedTask
from notiontaskr.domain.scheduled_task import ScheduledTask
from notiontaskr.domain.task_service import TaskService
from notiontaskr.infrastructure.executed_task_repository import ExecutedTaskRepository
from notiontaskr.infrastructure.scheduled_task_repository import ScheduledTaskRepository
from notiontaskr.infrastructure.operator import *
from notiontaskr.infrastructure.task_search_condition import TaskSearchCondition
from notiontaskr.infrastructure.scheduled_task_cache import ScheduledTaskCache
from notiontaskr.application.dto.uptime_data import UptimeData, UptimeDataByTag

from notiontaskr.domain.tags import Tags


class TaskApplicationService:
    def __init__(self, logger: AppLogger = AppLogger()):
        self.logger = logger
        self.executed_task_repo = ExecutedTaskRepository(
            config.NOTION_TOKEN,
            config.TASK_DB_ID,
        )
        self.scheduled_task_repo = ScheduledTaskRepository(
            config.NOTION_TOKEN,
            config.TASK_DB_ID,
        )
        self.scheduled_task_cache = ScheduledTaskCache(
            save_path=config.LOCAL_SCHEDULED_PICKLE_PATH
        )

    async def daily_task(self):
        """毎日0時に実行されるタスク"""

        gcs_handler = GCSHandler(
            bucket_name=config.BUCKET_NAME,
            on_error=lambda e: self.logger.error(
                f"GCSの初期化に失敗。エラー内容: {e}",
            ),
        )

        # notionから過去一年分の情報を取得し、Pickleに保存する
        self.logger.info("デイリータスクを開始します。")
        main_timer = AppTimer.init_and_start()

        # 過去一年分のタスクを取得
        # 条件作成(過去一年~未来)
        condition = TaskSearchCondition().or_(
            TaskSearchCondition().where_last_edited_time(
                operator=DateOperator.PAST_YEAR,
            ),
            TaskSearchCondition().where_last_edited_time(
                date=datetime.now().strftime("%Y-%m-%d"),
                operator=DateOperator.ON_OR_AFTER,
            ),
        )

        # 予定タスクをすべて取得する
        scheduled_tasks = await self.scheduled_task_repo.find_all_by_condition(
            condition=condition,
            on_error=lambda e, data: self.logger.error(
                f"予定タスク[{data['properties']['ID']['unique_id']['number']}]の取得に失敗。エラー内容: {e}"
            ),
        )

        # 実績タスクを全て取得する
        executed_tasks = await self.executed_task_repo.find_all_by_condition(
            condition=condition,
            on_error=lambda e, data: self.logger.error(
                f"実績タスク[{data['properties']['ID']['unique_id']['number']}]の取得に失敗。エラー内容: {e}"
            ),
        )

        # 実績タスクにIDを付与する(未付与のもののみ)
        _ = ExecutedTaskService.get_tasks_add_id_tag(
            to=executed_tasks, source=scheduled_tasks
        )

        # 予定タスクに実績タスクを紐づける
        _ = ScheduledTaskService.get_tasks_upserted_executed_tasks(
            scheduled_tasks_by_id={
                scheduled_task.id: scheduled_task for scheduled_task in scheduled_tasks
            },
            executed_tasks=executed_tasks,
            on_error=lambda e, task: self.logger.error(
                f"予定タスク[{task.id.number}]と実績タスクの紐づけに失敗。エラー内容: {e}"
            ),
        )

        # 予定タスクにサブアイテムを紐づける
        _ = ScheduledTaskService.get_tasks_appended_sub_tasks(
            sub_tasks=scheduled_tasks,
            parent_tasks_by_page_id={
                scheduled_task.page_id: scheduled_task
                for scheduled_task in scheduled_tasks
            },
            on_error=lambda e, task: self.logger.error(
                f"予定タスク[{task.id.number}]とサブアイテムの紐づけに失敗。エラー内容: {e}"
            ),
        )

        # 予定タスクのプロパティを更新
        for scheduled_task in scheduled_tasks:
            self._update_scheduled_task_properties(scheduled_task)

        # 更新
        tasks = []
        tasks.append(self._update_scheduled_tasks(scheduled_tasks))
        tasks.append(
            self._update_executed_tasks(
                [
                    executed_task
                    for scheduled_task in scheduled_tasks
                    for executed_task in scheduled_task.executed_tasks
                    if scheduled_task.executed_tasks
                ]
            )
        )

        _ = await asyncio.gather(*tasks)

        # pickleの保存
        await self._save_pickle(
            scheduled_tasks=scheduled_tasks, gcs_handler=gcs_handler
        )

        self.logger.info("処理時間: " + str(main_timer.get_elapsed_time()) + "秒")

    async def regular_task(self):
        """予定タスクのIDを持つ実績タスクにIDを付与する"""
        self.logger.info("レギュラータスクを開始します。")
        main_timer = AppTimer.init_and_start()

        gcs_handler = GCSHandler(
            bucket_name=config.BUCKET_NAME,
            on_error=lambda e: self.logger.error(
                f"GCSの初期化に失敗。エラー内容: {e}",
            ),
        )

        # 条件作成(最終更新日が1分前~現在。formatは`2025-05-09T14:40:00.000Z`ISO 8601形式)
        condition = TaskSearchCondition().and_(
            # 1分前~
            TaskSearchCondition().where_last_edited_time(
                operator=DateOperator.ON_OR_AFTER,
                date=to_isoformat(
                    datetime.now(timezone.utc) - timedelta(minutes=1, seconds=30)
                ),
            ),
            # ~現在
            TaskSearchCondition().where_last_edited_time(
                operator=DateOperator.ON_OR_BEFORE,
                date=to_isoformat(datetime.now(timezone.utc)),
            ),
        )
        self.logger.debug(f"検索条件: {condition.build()}")

        fetch_tasks_timer = AppTimer.init_and_start()

        # 条件にあう予定タスクと実績タスクを並列で取得する
        results = await asyncio.gather(
            self.scheduled_task_repo.find_by_condition(
                condition=condition,
                on_error=lambda e, data: self.logger.error(
                    f"予定タスク[{data['properties']['ID']['unique_id']['number']}]の取得に失敗。エラー内容: {e}"
                ),
            ),
            self.executed_task_repo.find_by_condition(
                condition=condition,
                on_error=lambda e, data: self.logger.error(
                    f"実績タスク[{data['properties']['ID']['unique_id']['number']}]の取得に失敗。エラー内容: {e}"
                ),
            ),
        )
        fetched_scheduled_tasks, fetched_executed_tasks = results[0], results[1]

        self.logger.debug(
            f"【処理時間】予定タスクと実績タスクの取得: {fetch_tasks_timer.get_elapsed_time()}秒"
        )
        self.logger.info(f"取得した予定タスクの数: {len(fetched_scheduled_tasks)}")
        self.logger.info(f"取得した実績タスクの数: {len(fetched_executed_tasks)}")

        if len(fetched_scheduled_tasks) == 0 and len(fetched_executed_tasks) == 0:
            self.logger.info(
                "取得した予定タスクと実績タスクがありません。処理を終了します。"
            )
            self.logger.debug(f"【処理時間】合計: {main_timer.get_elapsed_time()}秒")
            return

        # pickleから予定タスクを取得
        cache_scheduled_tasks = await self._load_pickle(gcs_handler=gcs_handler)
        if cache_scheduled_tasks is None:
            return

        add_executed_id_timer = AppTimer.init_and_start()

        # キャッシュの予定タスクを辞書に変換
        scheduled_tasks_by_id = {
            scheduled_task.id: scheduled_task
            for scheduled_task in cache_scheduled_tasks  # type: ignore
        }

        # キャッシュと取得した予定タスクをマージする
        scheduled_tasks_by_id = ScheduledTaskService.merge_scheduled_tasks(
            scheduled_tasks_by_id=scheduled_tasks_by_id,
            sources=fetched_scheduled_tasks,
        )

        # 実績タスクにIDを付与し、付与した予定タスクを取得(未付与のもののみ)
        scheduled_tasks_id_added = ExecutedTaskService.get_tasks_add_id_tag(
            to=fetched_executed_tasks, source=list(scheduled_tasks_by_id.values())
        )

        self.logger.debug(
            f"【処理時間】実績タスクのID付与: {add_executed_id_timer.get_elapsed_time()}秒"
        )
        calc_man_hours_timer = AppTimer.init_and_start()

        # 予定タスクと実績タスクの紐づけ
        scheduled_tasks_upserted_executed = ScheduledTaskService.get_tasks_upserted_executed_tasks(
            scheduled_tasks_by_id=scheduled_tasks_by_id,
            executed_tasks=fetched_executed_tasks,
            on_error=lambda e, task: self.logger.error(
                f"予定タスク[{task.id.number}]と実績タスクの紐づけに失敗。エラー内容: {e}"
            ),
        )

        # キャッシュから予定タスクの親IDに一致する予定タスクを検索し、紐づける
        parent_tasks_appended_child = ScheduledTaskService.get_tasks_appended_sub_tasks(
            sub_tasks=fetched_scheduled_tasks,
            parent_tasks_by_page_id={
                scheduled_task.page_id: scheduled_task
                for scheduled_task in list(scheduled_tasks_by_id.values())
            },
            on_error=lambda e, task: self.logger.error(
                f"予定タスク[{task.id.number}]とサブアイテムの紐づけに失敗。エラー内容: {e}"
            ),
        )

        # 更新予定のタスクを作成
        scheduled_tasks_to_update_by_id = {
            scheduled_task.id: scheduled_task
            for scheduled_task in fetched_scheduled_tasks
            + scheduled_tasks_id_added
            + scheduled_tasks_upserted_executed
            + parent_tasks_appended_child
        }

        # 予定タスクのプロパティを更新
        for scheduled_task in list(scheduled_tasks_to_update_by_id.values()):
            self._update_scheduled_task_properties(scheduled_task)

        # 既存データを辞書に変換
        update_executed_task_data = {task.id: task for task in fetched_executed_tasks}

        # 更新データを上書き
        for scheduled_task in list(scheduled_tasks_to_update_by_id.values()):
            for executed_task in scheduled_task.executed_tasks:
                if update_executed_task_data.get(executed_task.id) is None:
                    continue
                update_executed_task_data[executed_task.id] = executed_task

        # 更新
        tasks = []
        tasks.append(
            self._update_scheduled_tasks(list(scheduled_tasks_to_update_by_id.values()))
        )
        tasks.append(
            self._update_executed_tasks(list(update_executed_task_data.values()))
        )

        await asyncio.gather(*tasks)

        # pickleの保存
        await self._save_pickle(
            scheduled_tasks=list(scheduled_tasks_to_update_by_id.values()),
            gcs_handler=gcs_handler,
        )

        self.logger.debug(
            f"【処理時間】実績タスクの工数計算: {calc_man_hours_timer.get_elapsed_time()}秒"
        )
        self.logger.debug(f"【処理時間】合計: {main_timer.get_elapsed_time()}秒")

    async def get_uptime(
        self, tags: Tags, from_: datetime, to: datetime
    ) -> "UptimeDataByTag":
        """指定したタグの稼働実績を取得する

        :param tags: タグのリスト
        :return: 稼働実績DTO
        """

        condition = TaskSearchCondition().and_(
            # 日付のフィルター
            TaskSearchCondition().where_date(
                operator=DateOperator.ON_OR_AFTER,
                date=to_isoformat(from_),
            ),
            TaskSearchCondition().where_date(
                operator=DateOperator.ON_OR_BEFORE,
                date=to_isoformat(to),
            ),
        )

        fetched_executed_tasks = await self.executed_task_repo.find_by_condition(
            condition=condition,
            on_error=lambda e, data: self.logger.error(
                f"実績タスク[{data['properties']['ID']['unique_id']['number']}]の取得に失敗。エラー内容: {e}"
            ),
        )

        # 指定タグ配列に一致する予定タスクを辞書型で取得する
        executed_tasks_by_tag = fetched_executed_tasks.get_tasks_by_tag(
            tags=tags,
        )

        # タグごとの稼働実績を計算する
        uptime_data_by_tag = UptimeDataByTag.from_empty()
        for tag, tasks in executed_tasks_by_tag.items():
            uptime_data_by_tag.insert_data(
                data=UptimeData(
                    tag=tag,
                    uptime=ExecutedTaskService.get_total_man_hours(tasks),
                    from_=from_,
                    to=to,
                )
            )

        # DTOを返却
        return uptime_data_by_tag

    def _update_scheduled_task_properties(self, scheduled_task: ScheduledTask):
        """予定タスクのプロパティを更新するメソッド"""
        # サブアイテムに親IDラベルを付与する
        scheduled_task.update_sub_tasks_properties()
        # サブアイテムの工数を集計し、ラベルを更新する
        scheduled_task.aggregate_man_hours()
        # 実績タスクのステータスを更新する
        scheduled_task.update_status_by_checking_properties()
        # 進捗率を更新する
        scheduled_task.calc_progress_rate()
        # 実績人時ラベルを更新する
        scheduled_task.update_man_hours_label(
            ManHoursLabel.from_man_hours(
                executed_man_hours=scheduled_task.executed_man_hours,
                scheduled_man_hours=scheduled_task.scheduled_man_hours,
            )
        )
        # 予定タスクが持つ実績タスクのプロパティを更新する
        scheduled_task.update_executed_tasks_properties()

    async def _update_scheduled_tasks(
        self,
        scheduled_tasks: list[ScheduledTask],
    ):
        """予定タスクの実績工数を更新するメソッド"""
        updated_scheduled_tasks = TaskService.get_updated_tasks(scheduled_tasks)
        tasks = []
        for updated_scheduled_task in updated_scheduled_tasks:
            tasks.append(
                self.scheduled_task_repo.update(
                    scheduled_task=updated_scheduled_task,
                    on_success=lambda task: self.logger.info(
                        f"予定タスク[{task.id.number}]の更新: {task.update_contents}"
                    ),
                    on_error=lambda e, task: self.logger.error(
                        f"予定タスク[{task.id.number}]の更新に失敗しました。 エラー内容: {e}"
                    ),
                )
            )
        await asyncio.gather(*tasks)

    async def _load_pickle(self, gcs_handler: GCSHandler) -> List[ScheduledTask] | None:
        """GCSからPickleをダウンロードし、読み込むメソッド"""
        try:
            gcs_handler.download(
                from_=config.BUCKET_SCHEDULED_PICKLE_PATH,
                to=self.scheduled_task_cache.save_path,
            )
            self.logger.info("PickleのGCSからのダウンロードに成功しました。")

            # Pickleから予定タスクを読み込む
            scheduled_task = self.scheduled_task_cache.load()
            self.logger.info("Pickleの読み込みに成功しました。")
            return scheduled_task
        except Exception as e:
            self.logger.critical(
                f"PickleのGCSからのダウンロードに失敗。エラー内容: {e}"
            )
            self.logger.critical("処理を終了します。")
            return None

    async def _save_pickle(
        self, scheduled_tasks: List[ScheduledTask], gcs_handler: GCSHandler
    ):
        """GCSにPickleをアップロードするメソッド"""
        try:
            self.scheduled_task_cache.save(
                tasks=scheduled_tasks,
            )
            self.logger.info("Pickleの保存に成功しました。")

            # pickleをGCSにアップロードする
            gcs_handler.upload(
                from_=self.scheduled_task_cache.save_path,
                to=config.BUCKET_SCHEDULED_PICKLE_PATH,
            )
            self.logger.info("PickleのGCSへのアップロードに成功しました。")
        except Exception as e:
            self.logger.critical(f"Pickleの保存に失敗。エラー内容: {e}")
            self.logger.critical("処理を終了します。")

    async def _update_executed_tasks(
        self,
        executed_tasks: list[ExecutedTask],
    ):
        """実績タスクの予定タスクIDを更新するメソッド"""
        updated_executed_tasks = TaskService.get_updated_tasks(executed_tasks)
        tasks = []
        for updated_executed_task in updated_executed_tasks:
            tasks.append(
                self.executed_task_repo.update(
                    executed_task=updated_executed_task,
                    on_success=lambda task: self.logger.info(
                        f"実績タスク[{task.id.number}]の更新: {task.update_contents}"
                    ),
                    on_error=lambda e, task: self.logger.error(
                        f"実績タスク[{task.id.number}]の更新に失敗しました。 エラー内容: {e}"
                    ),
                )
            )

        await asyncio.gather(*tasks)
