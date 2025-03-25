from typing import List
from notion_client import Client

from domain.budget_task import BudgetTask


class BudgetTaskRepository:
    def __init__(self, token, db_id):
        self.client = Client(
            auth=token,
        )
        self.db_id = db_id

    def find_by_tags(self, tags: List[str]=[]) -> List[BudgetTask]:
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

    def update(self, budget_task: BudgetTask):
        '''予定タスクを更新する'''
        try:
            self.client.pages.update(
                **{
                    'page_id': budget_task.page_id,
                    'properties': {
                        '名前': {
                            'title': [
                                {
                                    'text': {
                                        'content': budget_task.name
                                    }
                                }
                            ]
                        },
                        '人日(実)': {
                            'number': budget_task.actual_man_hour,
                        },
                    }
                }
            )
        except Exception as e:
            raise