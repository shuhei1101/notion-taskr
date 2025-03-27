from typing import List
from notion_client import Client

from domain.actual_task import ActualTask


class ActualTaskRepository:
    def __init__(self, token, db_id):
        self.client = Client(
            auth=token,
        )
        self.db_id = db_id

    def find_by_tags(self, tags: List[str]=[]) -> List[ActualTask]:
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
            raise

    # 未完了のタスクを取得する
    def find_uncompleted(self) -> List[ActualTask]:
        '''タスクDBの未完了の実績を全て取得する'''
        try:
            response_data = self.client.databases.query(
                **{
                    'database_id': self.db_id,
                    'filter': {
                        'property': '予定フラグ',
                        "checkbox": {
                            "equals": False  # 予定フラグが「チェックなし」のものを取得
                        }
                    }
                }
            )
            # response_dataをActualTaskのリストに変換する
            actual_tasks = list(map(
                lambda data: ActualTask.from_response_data(data),
                response_data['results']
            ))

            return actual_tasks
        except Exception as e:
            raise
