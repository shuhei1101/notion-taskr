from app.infrastructure.operator import *

class TaskSearchConditions:
    '''Notionのフィルターを生成するクラス'''
    def __init__(self):
        self.conditions = {}

    def build(self):
        """最終的な条件を返す"""
        return self.conditions

    def and_(self, *conditions: 'TaskSearchConditions'):
        """AND 条件で結合"""
        if not conditions:
            raise ValueError("conditions is empty")
        
        self.conditions = {
            'and': [
                condition.build() for condition in conditions
            ]
        }
        return self

    def or_(self, *conditions: 'TaskSearchConditions'):
        """OR 条件で結合"""
        self.conditions = {
            'or': [
                condition.build() for condition in conditions
            ]
        }
        return self
    
    def where_tag(self, operator: MultiSelectOperator, tag: str):
        '''タグのフィルターを生成する'''
        self.conditions = {
            'property': 'タグ',
            "multi_select": {
                operator.value: tag
            }
        }
        return self

    def where_status(self, operator: StatusOperator, status: str, ):
        self.conditions = {
            'property': 'ステータス',
            "status": {
                operator.value: status
            }
        }
        return self

    def where_budget_flag(self, operator: CheckboxOperator, is_budget: bool):
        '''予定フラグのフィルターを生成する'''
        self.conditions = {
            'property': '予定フラグ',
            "checkbox": {
                operator.value: is_budget
            }
        }
        return self
    
    def where_name(self, operator: TextOperator, name: str):
        '''名前のフィルターを生成する'''
        self.conditions = {
            'property': '名前',
            "title": {
                operator.value: name
            }
        }
        return self



if __name__ == "__main__":
    # テストコード
    condition = TaskSearchConditions()
    condition.or_(
    condition.and_(
        condition.where_tag(MultiSelectOperator.CONTAINS, "test"),
        condition.where_status(StatusOperator.EQUALS, "未着手"),
        condition.where_budget_flag(CheckboxOperator.EQUALS, True),
    ),
    condition.and_(
        condition.where_name(TextOperator.CONTAINS, "test"),
        condition.where_budget_flag(CheckboxOperator.EQUALS, False),
    ))
    # condition.where_budget_flag(CheckboxOperator.EQUALS, True)
    # condition.where_name(TextOperator.CONTAINS, "test")
    # json形式で出力
    import json
    print(json.dumps(condition.build(), indent=4, ensure_ascii=False))
    