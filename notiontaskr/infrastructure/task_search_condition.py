from notiontaskr.domain.value_objects.status import Status
from notiontaskr.infrastructure.operator import *


class TaskSearchCondition:
    """Notionのフィルターを生成するクラス"""

    def __init__(self):
        self.conditions = {}

    def build(self):
        """最終的な条件を返す"""
        return self.conditions

    def and_(self, *conditions: "TaskSearchCondition"):
        """AND 条件で結合"""
        if not conditions:
            raise ValueError("conditions is empty")

        self.conditions = {"and": [condition.build() for condition in conditions]}
        return self

    def or_(self, *conditions: "TaskSearchCondition"):
        """OR 条件で結合"""
        self.conditions = {"or": [condition.build() for condition in conditions]}
        return self

    def where_tag(self, operator: MultiSelectOperator, tag: str):
        """タグのフィルターを生成する"""
        self.conditions = {"property": "タグ", "multi_select": {operator.value: tag}}
        return self

    def where_status(
        self,
        operator: StatusOperator,
        status: str,
    ):
        """ステータスで絞り込む"""
        self.conditions = {"property": "ステータス", "status": {operator.value: status}}
        return self

    def where_scheduled_flag(self, operator: CheckboxOperator, is_scheduled: bool):
        """予定フラグのフィルターを生成する"""
        self.conditions = {
            "property": "予定フラグ",
            "checkbox": {operator.value: is_scheduled},
        }
        return self

    def where_name(self, operator: TextOperator, name: str):
        """名前のフィルターを生成する"""
        self.conditions = {"property": "名前", "title": {operator.value: name}}
        return self

    def where_date(self, operator: DateOperator, date: str = {}):
        """日付のフィルターを生成する"""
        self.conditions = {"property": "日付", "date": {operator.value: date}}
        return self

    def where_last_edited_time(self, operator: DateOperator, date: str = {}):
        """最終更新日時のフィルターを生成する"""
        self.conditions = {
            "property": "最終更新日時",
            "last_edited_time": {operator.value: date},
        }
        return self

    def where_id(self, id: str):
        """IDのフィルターを生成する"""
        self.conditions = {"property": "ID", "unique_id": {"equals": id}}
        return self

    def where_page_id(self, page_id: str):
        """NotionのページIDのフィルターを生成する

        例: 1875ffa1-def1-4c34-8875-e559eb6e5853
        """
        pass


if __name__ == "__main__":
    # テストコード
    condition = TaskSearchCondition()
    condition.or_(
        condition.and_(
            condition.where_tag(MultiSelectOperator.CONTAINS, "test"),
            condition.where_status(StatusOperator.EQUALS, Status.NOT_STARTED.value),
            condition.where_scheduled_flag(CheckboxOperator.EQUALS, True),
        ),
        condition.and_(
            condition.where_name(TextOperator.CONTAINS, "test"),
            condition.where_scheduled_flag(CheckboxOperator.EQUALS, False),
        ),
    )
    # condition.where_scheduled_flag(CheckboxOperator.EQUALS, True)
    # condition.where_name(TextOperator.CONTAINS, "test")
    # json形式で出力
    import json

    print(json.dumps(condition.build(), indent=4, ensure_ascii=False))
