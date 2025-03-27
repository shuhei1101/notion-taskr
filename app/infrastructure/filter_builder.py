from typing import List

class FilterBuilder:
    '''Notionのフィルターを生成するクラス'''
    @staticmethod
    def tags_filter(tags: List[str]) -> dict:
        '''タグのフィルターを生成する
        
        指定されたタグのいずれかを含むタスクを取得するフィルターを生成する。
        タグが指定されていない場合は空の辞書を返す。
        '''
        return *(
            [{
                "or": [
                    {
                        "property": "タグ",
                        "multi_select": {
                            "contains": tag
                        }
                    } for tag in tags
                ]
            }] if tags else [] 
        ),

    @staticmethod
    def filter_budget_flag(is_budget: bool) -> dict:
        '''予定フラグのフィルターを生成する'''
        return {
            'property': '予定フラグ',
            "checkbox": {
                "equals": is_budget
            }
        }
    


    