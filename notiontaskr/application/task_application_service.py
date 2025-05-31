import asyncio
from datetime import datetime, timedelta, timezone
import logging
from typing import Optional, cast

import notiontaskr.config as config
from notiontaskr.infrastructure.pickle_handler import PickleHandler
from notiontaskr.notifier.task_reminder import TaskReminder
from notiontaskr.util.converter import to_isoformat
from notiontaskr.app_logger import AppLogger
from notiontaskr.app_timer import AppTimer
from notiontaskr.gcs_handler import GCSHandler
from notiontaskr.domain.executed_task_service import ExecutedTaskService
from notiontaskr.domain.scheduled_task_service import ScheduledTaskService
from notiontaskr.infrastructure.executed_task_repository import ExecutedTaskRepository
from notiontaskr.infrastructure.scheduled_task_repository import ScheduledTaskRepository
from notiontaskr.infrastructure.operator import *
from notiontaskr.infrastructure.task_search_condition import TaskSearchCondition
from notiontaskr.application.dto.uptime_data import UptimeData, UptimeDataByTag
from notiontaskr.domain.tags import Tags
from notiontaskr.domain.scheduled_tasks import ScheduledTasks
from notiontaskr.domain.executed_tasks import ExecutedTasks


class TaskApplicationService:
    def __init__(self, logger: logging.Logger = AppLogger().get()):
        self.logger = logger
        self.executed_task_repo = ExecutedTaskRepository(
            config.NOTION_TOKEN,
            config.TASK_DB_ID,
        )
        self.scheduled_task_repo = ScheduledTaskRepository(
            config.NOTION_TOKEN,
            config.TASK_DB_ID,
        )
        self.scheduled_task_cache = PickleHandler(
            save_path=config.LOCAL_SCHEDULED_PICKLE_PATH
        )
        self.executed_task_cache = PickleHandler(
            save_path=config.LOCAL_EXECUTED_PICKLE_PATH
        )
        self.scheduled_task_service = ScheduledTaskService()
        self.executed_task_service = ExecutedTaskService()
        self.reminder = TaskReminder(
            notifier=config.NOTIFIER,
        )

    async def daily_task(self):
        """毎日0時に実行されるタスク"""

        timer = AppTimer.init_and_start(
            logger=self.logger,
            message="デイリータスクの開始",
        )

        # ========== GCSハンドラーの初期化 ==========
        gcs_handler = None
        if not config.DEBUG_MODE:
            gcs_handler = GCSHandler(
                bucket_name=config.BUCKET_NAME,
                on_error=lambda e: self.logger.error(
                    f"GCSの初期化に失敗。エラー内容: {e}",
                ),
            )
            timer.snap_delta("GCSハンドラーの初期化完了")

        # ========== 過去一年分のタスクを取得 ==========
        # 条件作成(最終更新日が過去1年~未来)
        condition = TaskSearchCondition().or_(
            TaskSearchCondition().where_last_edited_time(
                operator=DateOperator.PAST_YEAR,
            ),
            TaskSearchCondition().where_last_edited_time(
                date=datetime.now().strftime("%Y-%m-%d"),
                operator=DateOperator.ON_OR_AFTER,
            ),
        )

        # 予定タスクの取得
        scheduled_tasks = await self.scheduled_task_repo.find_all_by_condition(
            condition=condition,
            on_error=lambda e, data: self.logger.error(
                f"予定タスク[{data['properties']['ID']['unique_id']['number']}]の取得に失敗。エラー内容: {e}"
            ),
        )

        # 実績タスクの取得
        executed_tasks = await self.executed_task_repo.find_all_by_condition(
            condition=condition,
            on_error=lambda e, data: self.logger.error(
                f"実績タスク[{data['properties']['ID']['unique_id']['number']}]の取得に失敗。エラー内容: {e}"
            ),
        )

        timer.snap_delta("Notionからタスクの取得完了")

        self.logger.info(f"取得予定タスク数: {len(scheduled_tasks)}")
        self.logger.info(f"取得実績タスク数: {len(executed_tasks)}")

        # ========== タスクの更新 ==========
        # 実績タスクに予定IDを付与
        _ = self.executed_task_service.get_scheduled_tasks_added_executed_id(
            to=executed_tasks, source=scheduled_tasks
        )

        # 予定タスクに実績タスクを紐づける
        _ = self.scheduled_task_service.get_tasks_upserted_executed_tasks(
            to=scheduled_tasks,
            source=executed_tasks,
            on_error=lambda e, task: self.logger.error(
                f"予定タスク[{task.scheduled_task_id.number}]と実績タスク[{task.id.number}]の紐づけに失敗。エラー内容: {e}"  # type: ignore
            ),
        )

        # 予定タスクにサブアイテムを紐づける
        _ = self.scheduled_task_service.get_parent_tasks_appended_sub_tasks(
            parent_tasks=scheduled_tasks,
            sub_tasks=scheduled_tasks,
            on_error=lambda e, task: self.logger.error(
                f"予定タスク[{task.id.number}]とサブアイテムの紐づけに失敗。エラー内容: {e}"
            ),
        )

        # タスクのプロパティを更新
        scheduled_tasks.update_tasks_properties()

        # 更新
        tasks = []
        tasks.append(self._update_scheduled_tasks(scheduled_tasks))
        tasks.append(self._update_executed_tasks(scheduled_tasks.get_executed_tasks()))

        timer.snap_delta("タスクの更新完了")

        await asyncio.gather(*tasks)

        # ========== pickleの保存 ==========
        tasks = []
        # 予定タスク
        tasks.append(
            self._save_pickle(
                obj=scheduled_tasks,
                gcs_handler=gcs_handler,
                bucket_path=config.BUCKET_SCHEDULED_PICKLE_PATH,
                cache=self.scheduled_task_cache,
            )
        )
        # 実績タスク
        tasks.append(
            self._save_pickle(
                obj=executed_tasks,
                gcs_handler=gcs_handler,
                bucket_path=config.BUCKET_EXECUTED_PICKLE_PATH,
                cache=self.executed_task_cache,
            )
        )

        await asyncio.gather(*tasks)

        timer.snap_delta("Pickleの保存完了")
        timer.snap_total("処理完了")

    async def regular_task(self):
        """予定タスクのIDを持つ実績タスクにIDを付与する"""
        timer = AppTimer.init_and_start(
            logger=self.logger,
            message="レギュラータスクの開始",
        )

        # ========== GCSハンドラーの初期化 ==========
        gcs_handler: Optional[GCSHandler] = None
        if not config.DEBUG_MODE:
            gcs_handler = GCSHandler(
                bucket_name=config.BUCKET_NAME,
                on_error=lambda e: self.logger.error(
                    f"GCSの初期化に失敗。エラー内容: {e}",
                ),
            )

        # ========== Notionからタスクの取得 ==========
        # 条件作成(最終更新日が1分前~現在)
        condition = TaskSearchCondition().and_(
            TaskSearchCondition().where_last_edited_time(
                operator=DateOperator.ON_OR_AFTER,
                date=to_isoformat(
                    datetime.now(timezone.utc) - timedelta(minutes=1, seconds=30)
                ),  # `2025-05-09T14:40:00.000Z`ISO 8601形式
            ),
            TaskSearchCondition().where_last_edited_time(
                operator=DateOperator.ON_OR_BEFORE,
                date=to_isoformat(datetime.now(timezone.utc)),
            ),
        )

        # 条件作成(リマインド時間が1分前~1分後)
        before_start_remind_condition = TaskSearchCondition().and_(
            TaskSearchCondition().where_before_start_minutes(
                operator=DateOperator.ON_OR_AFTER,
                date=to_isoformat(
                    datetime.now(timezone.utc) - timedelta(minutes=1, seconds=30)
                ),
            ),
            TaskSearchCondition().where_before_start_minutes(
                operator=DateOperator.ON_OR_BEFORE,
                date=to_isoformat(
                    datetime.now(timezone.utc) + timedelta(minutes=1, seconds=30)
                ),
            ),
        )
        before_end_remind_condition = TaskSearchCondition().and_(
            TaskSearchCondition().where_before_end_minutes(
                operator=DateOperator.ON_OR_AFTER,
                date=to_isoformat(
                    datetime.now(timezone.utc) - timedelta(minutes=1, seconds=30)
                ),
            ),
            TaskSearchCondition().where_before_end_minutes(
                operator=DateOperator.ON_OR_BEFORE,
                date=to_isoformat(
                    datetime.now(timezone.utc) + timedelta(minutes=1, seconds=30)
                ),
            ),
        )

        # タスクの取得
        results = await asyncio.gather(
            # タスクの取得
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
            # リマインド用タスクの取得
            self.executed_task_repo.find_by_condition(
                condition=before_start_remind_condition,
                on_error=lambda e, data: self.logger.error(
                    f"実績タスク[{data['properties']['ID']['unique_id']['number']}]の取得に失敗。エラー内容: {e}"
                ),
            ),
            self.executed_task_repo.find_by_condition(
                condition=before_end_remind_condition,
                on_error=lambda e, data: self.logger.error(
                    f"実績タスク[{data['properties']['ID']['unique_id']['number']}]の取得に失敗。エラー内容: {e}"
                ),
            ),
        )

        # 更新用タスクの取得
        fetched_scheduled_tasks, fetched_executed_tasks = results[0], results[1]
        timer.snap_delta("Notionからタスクの取得完了")
        self.logger.info(f"取得した予定タスクの数: {len(fetched_scheduled_tasks)}")
        self.logger.info(f"取得した実績タスクの数: {len(fetched_executed_tasks)}")

        # リマインド用タスクの取得
        fetched_remind_tasks = results[2].upserted_by_id(results[3])
        self.logger.info(f"取得したリマインド用タスクの数: {len(fetched_remind_tasks)}")
        has_fetched_remind_tasks = len(fetched_remind_tasks) > 0

        # ========== pickleからタスクを取得 ==========
        # 予定タスク
        cache_scheduled_tasks = await self._load_pickle(
            gcs_handler=gcs_handler,
            bucket_path=config.BUCKET_SCHEDULED_PICKLE_PATH,
            cache=self.scheduled_task_cache,
        )
        # 実績タスク
        cache_executed_tasks = await self._load_pickle(
            gcs_handler=gcs_handler,
            bucket_path=config.BUCKET_EXECUTED_PICKLE_PATH,
            cache=self.executed_task_cache,
        )
        if cache_scheduled_tasks is None or cache_executed_tasks is None:
            self.logger.critical("キャッシュが空です。処理を終了します。")
            return

        # 取得したタスクをキャスト
        cache_scheduled_tasks = cast(ScheduledTasks, cache_scheduled_tasks)
        cache_executed_tasks = cast(ExecutedTasks, cache_executed_tasks)

        timer.snap_delta("Pickleからタスクの取得完了")

        # 取得したタスクとキャッシュのマージ
        merged_scheduled_tasks = cache_scheduled_tasks.upserted_by_id(
            fetched_scheduled_tasks
        )
        merged_executed_tasks = cache_executed_tasks.upserted_by_id(
            fetched_executed_tasks
        )
        has_fetched_scheduled_tasks = len(merged_scheduled_tasks) > 0
        has_fetched_executed_tasks = len(merged_executed_tasks) > 0
        if has_fetched_scheduled_tasks and has_fetched_executed_tasks:
            # ========== タスクの更新 ==========

            # 更新対象タスクの初期化
            scheduled_tasks_to_update = ScheduledTasks.from_empty()
            scheduled_tasks_to_update.upsert_by_id(fetched_scheduled_tasks)

            # 実績タスクID付与 + 付与された予定タスク取得
            scheduled_tasks_to_update.upsert_by_id(
                self.executed_task_service.get_scheduled_tasks_added_executed_id(
                    to=fetched_executed_tasks,
                    source=merged_scheduled_tasks,
                )
            )

            # 実績タスクの紐づけ
            scheduled_tasks_to_update.upsert_by_id(
                self.scheduled_task_service.get_tasks_upserted_executed_tasks(
                    to=merged_scheduled_tasks,
                    source=fetched_executed_tasks,
                    on_error=lambda e, task: self.logger.error(
                        f"予定タスク[{task.id.number}]と実績タスクの紐づけに失敗。エラー内容: {e}"
                    ),
                )
            )

            # 取得予定タスクにサブアイテムを紐づける
            scheduled_tasks_to_update.upsert_by_id(
                self.scheduled_task_service.get_parent_tasks_appended_sub_tasks(
                    sub_tasks=merged_scheduled_tasks,
                    parent_tasks=fetched_scheduled_tasks,
                    on_error=lambda e, task: self.logger.error(
                        f"予定タスク[{task.id.number}]とサブアイテムの紐づけに失敗。エラー内容: {e}"
                    ),
                )
            )

            # 取得サブアイテムに親タスクを紐づける
            scheduled_tasks_to_update.upsert_by_id(
                self.scheduled_task_service.get_parent_tasks_appended_sub_tasks(
                    sub_tasks=fetched_scheduled_tasks,
                    parent_tasks=merged_scheduled_tasks,
                    on_error=lambda e, task: self.logger.error(
                        f"予定タスク[{task.id.number}]とサブアイテムの紐づけに失敗。エラー内容: {e}"
                    ),
                )
            )

            # タスクのプロパティ更新
            scheduled_tasks_to_update.update_tasks_properties()

            # Notionの更新
            tasks = []
            tasks.append(self._update_scheduled_tasks(scheduled_tasks_to_update))
            tasks.append(
                self._update_executed_tasks(
                    fetched_executed_tasks.upserted_by_id(
                        scheduled_tasks_to_update.get_executed_tasks()
                    )
                )
            )
            await asyncio.gather(*tasks)

            timer.snap_delta("タスクの更新完了")
        else:
            self.logger.warning(
                "取得したタスクがありません。更新処理をスキップします。"
            )

        # ========== Slackリマインド通知 ==========
        if has_fetched_remind_tasks:
            # 非同期でリマインド通知を実行
            asyncio.create_task(
                self.reminder.remind(
                    tasks=fetched_remind_tasks.get_remind_tasks(),
                    on_success=lambda task: self.logger.info(
                        f"Slack通知送信(タスクID: {task.name.get_remind_message()})"
                    ),
                    on_error=lambda e, task: self.logger.error(
                        f"Slack通知失敗(タスクID: {task.name.get_remind_message()}) エラー内容: {e}"
                    ),
                )
            )

            timer.snap_delta("Slack通知処理完了")
        else:
            self.logger.warning(
                "リマインド対象のタスクがありません。Slack通知をスキップします。"
            )

        # ========== Pickleの保存 ==========
        tasks = []
        if has_fetched_scheduled_tasks:
            # 予定タスク
            tasks.append(
                self._save_pickle(
                    obj=merged_scheduled_tasks,
                    gcs_handler=gcs_handler,
                    bucket_path=config.BUCKET_SCHEDULED_PICKLE_PATH,
                    cache=self.scheduled_task_cache,
                )
            )
        else:
            self.logger.warning(
                "取得した予定タスクがありません。Pickleの保存をスキップします。"
            )
        if has_fetched_executed_tasks:
            # 実績タスク
            tasks.append(
                self._save_pickle(
                    obj=merged_executed_tasks,
                    gcs_handler=gcs_handler,
                    bucket_path=config.BUCKET_EXECUTED_PICKLE_PATH,
                    cache=self.executed_task_cache,
                )
            )
        else:
            self.logger.warning(
                "取得した実績タスクがありません。Pickleの保存をスキップします。"
            )

        await asyncio.gather(*tasks)

        timer.snap_delta("Pickleの保存処理完了")

        timer.snap_total("処理完了")

    async def get_uptime(
        self, tags: Tags, from_: datetime, to: datetime
    ) -> "UptimeDataByTag":
        """指定したタグの稼働実績を取得する

        :param tags: タグのリスト
        :return: 稼働実績DTO
        """

        timer = AppTimer.init_and_start(
            logger=self.logger,
            message="稼働実績の取得を開始",
        )

        # ========== タスクの取得 ==========
        condition = TaskSearchCondition().and_(
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
        timer.snap_delta("Notionから実績タスクの取得完了")

        # ========== 稼働実績を計算 ==========
        # 指定タグ配列に一致する予定タスクを辞書型で取得する
        executed_tasks_by_tag = fetched_executed_tasks.get_tasks_by_tag(
            tags=tags,
        )

        # タグごとの稼働実績を計算する
        uptime_data_by_tag = UptimeDataByTag.from_empty()
        for tag, tasks in executed_tasks_by_tag.items():
            uptime_data_by_tag.insert_data(
                data=UptimeData.from_domain(
                    tag=tag,
                    uptime=tasks.get_total_man_hours(),
                    from_=from_,
                    to=to,
                )
            )
        timer.snap_delta("稼働実績を計算完了")
        timer.snap_total("処理完了")

        # ========== タグごとの稼働実績を返す ==========
        return uptime_data_by_tag

    async def _load_pickle(
        self,
        gcs_handler: Optional[GCSHandler],
        bucket_path: str,
        cache: PickleHandler,
    ) -> object | None:
        """GCSからPickleをダウンロードし、読み込むメソッド"""
        try:
            if not config.DEBUG_MODE and gcs_handler is not None:
                gcs_handler.download(
                    from_=bucket_path,
                    to=cache.save_path,
                )
                self.logger.info("PickleをGCSからダウンロード成功")
        except Exception as e:
            self.logger.info(f"PickleをGCSからダウンロード失敗。エラー内容: {e}")

        try:
            # Pickleから予定タスクを読み込む
            obj = cache.load()
            self.logger.info(f"Pickleの読み込みに成功: {cache.save_path}")
            return obj
        except Exception as e:
            self.logger.critical(f"Pickleの読み込みに失敗。エラー内容: {e}")
            return None

    async def _save_pickle(
        self,
        obj: object,
        gcs_handler: Optional[GCSHandler],
        bucket_path: str,
        cache: PickleHandler,
    ):
        """GCSにPickleをアップロードするメソッド"""
        try:
            cache.save(
                tasks=obj,
            )
            self.logger.info(f"Pickleの保存に成功: {cache.save_path}")

        except Exception as e:
            self.logger.critical(f"Pickleの保存に失敗。エラー内容: {e}")

        try:
            if not config.DEBUG_MODE and gcs_handler is not None:
                # pickleをGCSにアップロードする
                gcs_handler.upload(
                    from_=cache.save_path,
                    to=bucket_path,
                )
                self.logger.info("PickleをGCSへアップロード成功")
        except Exception as e:
            self.logger.error(f"PickleをGCSへアップロード失敗。エラー内容: {e}")

    async def _update_scheduled_tasks(
        self,
        scheduled_tasks: ScheduledTasks,
    ):
        """予定タスクの実績工数を更新するメソッド"""
        updated_scheduled_tasks = scheduled_tasks.get_updated_tasks()
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

    async def _update_executed_tasks(
        self,
        executed_tasks: ExecutedTasks,
    ):
        """実績タスクの予定タスクIDを更新するメソッド"""
        updated_executed_tasks = executed_tasks.get_updated_tasks()
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
