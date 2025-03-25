from typing import List
from notion_client import Client

from domain.actual_task import ActualTask
from domain.budget_task import BudgetTask
from infrastructure.exceptions import TaskRepositoryException

class TaskRepository():
    '''notion_clientクラスのラッパークラス'''
    def __init__(self, token, db_id):
        '''初期化'''
        self.client = Client(
            auth=token,
        )
        self.db_id = db_id

    def update_man_hour(self, page_id, actual_man_days, name):
        '''予定タスクを更新する'''

        try:
            self.client.pages.update(
                **{
                    'page_id': page_id,
                    'properties': {
                        '名前': {
                            'title': [
                                {
                                    'text': {
                                        'content': name
                                    }
                                }
                            ]
                        },
                        '人日(実)': {
                            'number': actual_man_days,
                        },
                    }
                }
            )
        except Exception as e:
            raise TaskRepositoryException(f'Error: {e}')
        
# テスト実行用
if __name__ == '__main__':#
    token = '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'
    db_id = '1b08fe3c9ed280dab2f3c53738b9cdc8'
    task_query_service = TaskRepository(token, db_id)
    actual_tasks = task_query_service.get_actual_tasks(tag='お小遣いクエストボード')
    print(actual_tasks[0].name)
    print(actual_tasks[0].tag)
    print(actual_tasks[0].start_date)
    print(actual_tasks[0].end_date)
    print(actual_tasks[0].man_hour)
    # print(data)
    
    
