import copy
from typing import List

import config as config
from domain.scheduled_task_service import ScheduledTaskService
from domain.excuted_task import ExcutedTask
from domain.scheduled_task import ScheduledTask
from domain.name_labels.id_label import IdLabel
from domain.name_labels.man_days_label import ManDaysLabel
from infrastructure.excuted_task_repository import ExcutedTaskRepository
from infrastructure.scheduled_task_repository import ScheduledTaskRepository
from infrastructure.operator import *
from infrastructure.task_search_condition import TaskSearchConditions


class TaskApplicationService:
    def __init__(self):
        self.excuted_task_repository = ExcutedTaskRepository(
            config.NOTION_TOKEN, 
            config.TASK_DB_ID
        )
        self.scheduled_task_repository = ScheduledTaskRepository(
            config.NOTION_TOKEN, 
            config.TASK_DB_ID
        )
        self.scheduled_task_service = ScheduledTaskService()
        
    def update_man_days(self, tags: List[str] = None):
        '''予定タスクのIDを持つ実績タスクから実績工数を割り出し、
        予定タスクの実績工数を更新する。

        :param tags: タグのリスト
        '''

        # タスクの実績を取得
        excuted_tasks: List[ExcutedTask] = self.excuted_task_repository.find_by_condition(
            TaskSearchConditions()
                .or_(
                    *(
                        map(
                            lambda tag: TaskSearchConditions().where_tag(
                                operator=MultiSelectOperator.CONTAINS,
                                tag=tag
                            ),
                            tags
                        )
                    )
                )
        ) if tags else self.excuted_task_repository.find_all()

        # タスクの予定を取得
        scheduled_tasks: List[ScheduledTask] = self.scheduled_task_repository.find_by_condition(
            TaskSearchConditions()
                .or_(
                    *(
                        map(
                            lambda tag: TaskSearchConditions().where_tag(
                                operator=MultiSelectOperator.CONTAINS,
                                tag=tag
                            ),
                            tags
                        )
                    )
                )
        ) if tags else self.scheduled_task_repository.find_all()

        # 予定タスクごとに実績工数を集計
        updated_scheduled_tasks: list[ScheduledTask] = self.scheduled_task_service.aggregate_excuted_man_days(
            scheduled_tasks=scheduled_tasks,
            excuted_tasks=excuted_tasks
        )

        self._update_scheduled_tasks(updated_scheduled_tasks)

    def add_id_to_excuted_task(self):
        '''予定タスクのIDを持つ実績タスクにIDを付与する'''
        
        # 未完了の予定タスクを全て取得する
        scheduled_tasks: List[ScheduledTask] = self.scheduled_task_repository.find_by_condition(
            TaskSearchConditions().where_status(
                operator=StatusOperator.EQUALS,
                status="未着手"
            )
        )

        # 予定タスク名を配列に格納する（タグ部分と頭と末尾の空白を除去）
        scheduled_task_names = list(map(
            lambda task: task.name.task_name,
            scheduled_tasks
        ))

        # 予定タスク名に一致する実績タスクを全て取得する
        # このとき、一回のクエリで全て取得する
        excuted_tasks: List[ExcutedTask] = self.excuted_task_repository.find_by_condition(
            TaskSearchConditions().or_(
                *(
                    map(
                        lambda name: TaskSearchConditions().where_name(
                            operator=TextOperator.EQUALS,
                            name=name
                        ),
                        scheduled_task_names
                    )
                )
            )
        )

        # 予定タスク名配列を回し、一致する実績タスクの名前にIDをタグとして付与する
        for scheduled_task in scheduled_tasks:
            # 一致する実績タスクたちを取得
            matched_excuted_tasks = list(filter(
                lambda excuted_task: excuted_task.name.task_name == scheduled_task.name.task_name,
                excuted_tasks
            ))

            if matched_excuted_tasks != []:
                for excuted_task in matched_excuted_tasks:
                    # 実績タスクの名前にIDをタグとして付与
                    excuted_task.update_id_label(IdLabel.from_id(
                        id_prefix=scheduled_task.id_prefix,
                        id_number=scheduled_task.id_number
                    ))
                    

                    # 実績タスクを更新
                    self.excuted_task_repository.update(excuted_task)

            # 予定タスクの名前にIDをタグとして付与（非同期）
            self.scheduled_task_repository.update(scheduled_task)
        
    def _update_scheduled_tasks(self, scheduled_tasks: list[ScheduledTask]):
        '''予定タスクの実績工数を更新するメソッド'''
        for scheduled_task in scheduled_tasks:
            if scheduled_task.is_updated:
                self.scheduled_task_repository.update(scheduled_task)

    def _update_excuted_tasks(self, excuted_tasks: list[ExcutedTask]):
        '''実績タスクの予定タスクIDを更新するメソッド'''
        for excuted_task in excuted_tasks:
            if excuted_task.is_updated:
                self.excuted_task_repository.update(excuted_task)


if __name__ == '__main__':
    service = TaskApplicationService()
    service.add_id_to_excuted_task()
    service.update_man_days(tags=[])
