from typing import Callable, List
from domain.value_objects.page_id import PageId
from infrastructure.id_findable import IdFindable
from infrastructure.scheduled_task_update_properties import ScheduledTaskUpdateProperties
from notion_client import Client

import config
from domain.scheduled_task import ScheduledTask
from infrastructure.operator import CheckboxOperator
from infrastructure.task_search_condition import TaskSearchCondition

class ScheduledTaskRepository(IdFindable):
    def __init__(self, token, db_id):
        self.client = Client(
            auth=token,
        )
        self.db_id = db_id
        self.filter = TaskSearchCondition()

    async def find_all(self,
                 on_error: Callable[[Exception, dict[str]], None]
                 ) -> List[ScheduledTask]:
        '''全ての予定を取得する'''
        filter = TaskSearchCondition().and_(
            TaskSearchCondition().where_scheduled_flag(
                operator=CheckboxOperator.EQUALS,
                is_scheduled=True
            ),
        ).build()
        
        response_data = self.client.databases.query(
            **{
                'database_id': self.db_id,
                'filter': filter
            }
        )

        # response_dataをScheduledTaskのリストに変換する
        scheduled_tasks = []
        for data in response_data['results']:
            try:
                scheduled_tasks.append(ScheduledTask.from_response_data(data))
            except Exception as e:
                # 名前が空のときにもスキップされる
                on_error(e, data)
                
        return scheduled_tasks

    async def find_by_condition(self, condition: TaskSearchCondition,
                          on_error: Callable[[Exception, dict[str]], None]
                          ) -> List[ScheduledTask]:
        '''タスクDBの指定タグの予定を全て取得する'''

        filter = TaskSearchCondition().and_(
            TaskSearchCondition().where_scheduled_flag(
                operator=CheckboxOperator.EQUALS,
                is_scheduled=True
            ),
            condition
        ).build()
        
        response_data = self.client.databases.query(
            **{
                'database_id': self.db_id,
                'filter': filter
            }
        )

        # response_dataをScheduledTaskのリストに変換する
        scheduled_tasks = []
        for data in response_data['results']:
            try:
                scheduled_tasks.append(ScheduledTask.from_response_data(data))
            except Exception as e:
                # 名前が空のときにもスキップされる
                on_error(e, data)

        return scheduled_tasks
    
    async def find_by_page_id(self, page_id: PageId) -> ScheduledTask:
        '''ページIDから1件のページ情報を取得する'''
        try:
            response_data = self.client.pages.retrieve(page_id=str(page_id))
            task = ScheduledTask.from_response_data(response_data)
            return task
        
        except Exception as e:
            raise RuntimeError(f"ページ取得失敗: {e}")

    async def update(self, scheduled_task: ScheduledTask,
                     on_success: Callable[[ScheduledTask], None],
                     on_error: Callable[[Exception, ScheduledTask], None]
                     ):
        '''予定タスクを更新する'''

        try:
            properties = ScheduledTaskUpdateProperties(task=scheduled_task) \
                .set_name() \
                .set_executed_man_hours() \
                .build()

            self.client.pages.update(
                **{
                    'page_id': str(scheduled_task.page_id),
                    'properties': properties
                }
            )
            on_success(scheduled_task)
        except Exception as e:
            on_error(e, scheduled_task)

        

# 動作確認用
if __name__ == '__main__':
    token = config.NOTION_TOKEN
    db_id = config.TASK_DB_ID

    scheduled_task_repo = ScheduledTaskRepository(token, db_id)
    scheduled_task = scheduled_task_repo.find_by_page_id(
        page_id='1875ffa1-def1-4c34-8875-e559eb6e5853'
    )
    print(scheduled_task)