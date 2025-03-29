import copy
from typing import List

import app.config as config
from app.domain.budget_task_service import BudgetTaskService
from app.domain.actual_task import ActualTask
from app.domain.budget_task import BudgetTask
from app.domain.tag_builder import TagBuilder
from app.infrastructure.actual_task_repository import ActualTaskRepository
from app.infrastructure.budget_task_repository import BudgetTaskRepository
from app.infrastructure.operator import *
from app.infrastructure.task_search_condition import TaskSearchConditions

class TaskApplicationService:
    def __init__(self):
        self.actual_task_repository = ActualTaskRepository(
            config.NOTION_TOKEN, 
            config.TASK_DB_ID
        )
        self.budget_task_repository = BudgetTaskRepository(
            config.NOTION_TOKEN, 
            config.TASK_DB_ID
        )
        self.service = BudgetTaskService()
        
    def update_man_days(self, tags: List[str] = None):
        '''予定タスクのIDを持つ実績タスクから実績工数を割り出し、
        予定タスクの実績工数を更新する。

        :param tags: タグのリスト
        '''

        # タスクの実績を取得
        actual_tasks: List[ActualTask] = self.actual_task_repository.find_by_condition(
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
        ) if tags else self.actual_task_repository.find_all()

        # タスクの予定を取得
        budget_tasks: List[BudgetTask] = self.budget_task_repository.find_by_condition(
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
        ) if tags else self.budget_task_repository.find_all()

        # 予定タスクごとに実績工数を集計
        for budget_task in budget_tasks:
            actual_man_days = sum(map(
                # もし予定タスクのIDを持つ実績タスクがあれば、その工数を取得
                lambda actual_task: actual_task.man_days if actual_task.budget_task_id == budget_task.id else 0,
                actual_tasks
            ))
            
            # コピーして実績工数を更新
            updated_budget_task = copy.deepcopy(budget_task)
            updated_budget_task.actual_man_days = actual_man_days

            # 予定タスクの名前のタグに実績工数を追加
            tag_builder = TagBuilder()
            updated_budget_task.name.register_tag(
                tag=tag_builder.build_man_days_tag(
                    actual_man_days=actual_man_days,
                    budget_man_days=budget_task.budget_man_days,
                )
            )

            if actual_man_days != 0 and actual_man_days != budget_task.actual_man_days:
                # 予定タスクの実績工数を更新
                self.budget_task_repository.update(
                    updated_budget_task
                )

        # Id自動付与機能

    def add_id_to_actual_task(self):
        '''予定タスクのIDを持つ実績タスクにIDを付与する'''
        
        # 未完了の予定タスクを全て取得する
        budget_tasks: List[BudgetTask] = self.budget_task_repository.find_by_condition(
            TaskSearchConditions().where_status(
                operator=StatusOperator.EQUALS,
                status="未着手"
            )
        )

        # 予定タスク名を配列に格納する（タグ部分と頭と末尾の空白を除去）
        budget_task_names = list(map(
            lambda task: task.name.task_name,
            budget_tasks
        ))

        # 予定タスク名に一致する実績タスクを全て取得する
        # このとき、一回のクエリで全て取得する
        actual_tasks: List[ActualTask] = self.actual_task_repository.find_by_condition(
            TaskSearchConditions().or_(
                *(
                    map(
                        lambda name: TaskSearchConditions().where_name(
                            operator=TextOperator.EQUALS,
                            name=name
                        ),
                        budget_task_names
                    )
                )
            )
        )

        # 予定タスク名配列を回し、一致する実績タスクの名前にIDをタグとして付与する
        for budget_task in budget_tasks:
            # 一致する実績タスクたちを取得
            matched_actual_tasks = list(filter(
                lambda actual_task: actual_task.name.task_name == budget_task.name.task_name,
                actual_tasks
            ))

            if matched_actual_tasks != []:
                for actual_task in matched_actual_tasks:
                    # 実績タスクの名前にIDをタグとして付与
                    tag_builder = TagBuilder()
                    actual_task.name.register_tag(
                        tag=tag_builder.build_id_tag(
                            id_prefix=budget_task.id_prefix,
                            id_number=budget_task.id_number
                        )
                    )

                    # 実績タスクを更新
                    self.actual_task_repository.update(actual_task)
        
if __name__ == '__main__':
    service = TaskApplicationService()
    service.update_man_days(tags=[])
    # service.add_id_to_actual_task()
