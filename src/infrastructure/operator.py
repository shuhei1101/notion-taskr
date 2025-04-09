from enum import Enum

class TextOperator(Enum):
    '''テキスト検索の演算子'''
    # 完全一致
    EQUALS = "equals"
    # 部分一致
    CONTAINS = "contains"
    # 前方一致
    STARTS_WITH = "starts_with"
    # 後方一致
    ENDS_WITH = "ends_with"

class MaltiSelectOperator(Enum):
    '''マルチセレクト検索の演算子'''
    # 完全一致
    EQUALS = "equals"
    # 部分一致
    CONTAINS = "contains"

class StatusOperator(Enum):
    '''セレクト検索の演算子'''
    # 完全一致
    EQUALS = "equals"
    # 空
    IS_EMPTY = "is_empty"
    # 空でない
    IS_NOT_EMPTY = "is_not_empty"

class CheckboxOperator(Enum):
    '''チェックボックス検索の演算子'''
    # 完全一致
    EQUALS = "equals"

class MultiSelectOperator(Enum):
    '''マルチセレクト検索の演算子'''
    # 指定されたタグを含むページを取得
    CONTAINS = "contains"
