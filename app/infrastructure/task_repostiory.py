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

    def get_actual_tasks(self, tags: List[str]=[]) -> List[ActualTask]:
        '''タスクDBの指定タグの実績を全て取得する'''

        filter_condition = {
                    "and": [
                        *(
                            [{
                                "or": [
                                    {
                                        "property": "タグ",
                                        "multi_select": {
                                            "contains": tag
                                        }
                                    } for tag in tags
                                ]
                            }] if tags else []  # ✅ 空ならタグのフィルタを追加しない
                        ),
                        # プロパティ「予定フラグ」が「チェックなし」である
                        {
                            'property': '予定フラグ',
                            "checkbox": {
                                "equals": False  # 予定フラグが「チェックなし」のものを取得
                            }
                        },
                    ]
                }
        try:
            response_data = self.client.databases.query(
                **{
                    'database_id': self.db_id,
                    'filter': filter_condition,
                }
            )
            # response_dataをActualTaskのリストに変換する
            actual_tasks = list(map(
                lambda data: ActualTask.from_response_data(data),
                response_data['results']
            ))

            return actual_tasks
        except Exception as e:
            raise TaskRepositoryException(f'Error: {e}')
        
    def get_budget_tasks(self, tags: List[str]=[]) -> List[BudgetTask]:
        '''タスクDBの指定タグの予定を全て取得する'''
        filter_condition = {
                    "and": [
                        *(
                            [{
                                "or": [
                                    {
                                        "property": "タグ",
                                        "multi_select": {
                                            "contains": tag
                                        }
                                    } for tag in tags
                                ]
                            }] if tags else []  # ✅ 空ならタグのフィルタを追加しない
                        ),
                        # プロパティ「予定フラグ」が「チェックあり」である
                        {
                            'property': '予定フラグ',
                            "checkbox": {
                                "equals": True  # 予定フラグが「チェックあり」のものを取得
                            }
                        },
                    ]
                }
        try:
            response_data = self.client.databases.query(
                **{
                    'database_id': self.db_id,
                    'filter': filter_condition,
                }
            )
            # response_dataをBudgetTaskのリストに変換する
            budget_tasks = []
            for data in response_data['results']:
                try:
                    budget_tasks.append(BudgetTask.from_response_data(data))
                except Exception as e:
                    print(f"スキップ: {e}")  # エラー内容を表示（デバッグ用）

            return budget_tasks
        except Exception as e:
            raise TaskRepositoryException(f'Error: {e}')
        
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
    
    
