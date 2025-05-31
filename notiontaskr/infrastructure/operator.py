from enum import Enum


class TextOperator(Enum):
    """テキスト検索の演算子"""

    # 完全一致
    EQUALS = "equals"
    # 部分一致
    CONTAINS = "contains"
    # 前方一致
    STARTS_WITH = "starts_with"
    # 後方一致
    ENDS_WITH = "ends_with"


class StatusOperator(Enum):
    """セレクト検索の演算子"""

    # 完全一致
    EQUALS = "equals"
    # 空
    IS_EMPTY = "is_empty"
    # 空でない
    IS_NOT_EMPTY = "is_not_empty"


class CheckboxOperator(Enum):
    """チェックボックス検索の演算子"""

    # 完全一致
    EQUALS = "equals"


class MultiSelectOperator(Enum):
    """マルチセレクト検索の演算子"""

    # 指定されたタグを含むページを取得
    CONTAINS = "contains"


class DateOperator(Enum):
    """日付検索の演算子

    ### Notion APIのドキュメントに記載されている演算子一覧
    (演算子: 意味)
    - equals: 完全一致
    - before: 指定日より前
    - after: 指定日より後
    - on_or_before: 指定日以前
    - on_or_after: 指定日以降
    - past_week: 直近1週間
    - past_month: 直近1か月
    - past_year: 直近1年
    - next_week: 次の1週間
    - next_month: 次の1か月
    - next_year: 次の1年
    - this_week: 今週
    """

    # 完全一致
    EQUALS = "equals"
    # 指定日より前
    BEFORE = "before"
    # 指定日より後
    AFTER = "after"
    # 指定日以前
    ON_OR_BEFORE = "on_or_before"
    # 指定日以降
    ON_OR_AFTER = "on_or_after"
    # 直近1週間
    PAST_WEEK = "past_week"
    # 直近1か月
    PAST_MONTH = "past_month"
    # 直近1年
    PAST_YEAR = "past_year"
    # 次の1週間
    NEXT_WEEK = "next_week"
    # 次の1か月
    NEXT_MONTH = "next_month"
    # 次の1年
    NEXT_YEAR = "next_year"
    # 今週
    THIS_WEEK = "this_week"
