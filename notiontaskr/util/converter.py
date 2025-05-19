from datetime import datetime


def to_isoformat(dt: datetime) -> str:
    """datetimeをISO8601形式(UTC, Z付き)に変換する

    dtはUTCのdatetimeを想定。JSTは受け付けない。
    例: 2023-10-01T12:00:00.000Z
    """
    if not isinstance(dt, datetime):
        raise ValueError(f"Invalid type: {type(dt)}. Must be datetime.")
    return dt.strftime("%Y-%m-%dT%H:%M:%S.") + f"{dt.microsecond // 1000:03d}Z"


def truncate_decimal(num: float) -> str:
    """小数点以下を1桁に切り捨てる

    ただし、小数点以下が0の場合は整数部分のみ表示
    """
    if not isinstance(num, (float, int)):
        raise ValueError(f"Invalid type: {type(num)}. Must be float or int.")
    result_str = f"{num:.1f}".rstrip("0").rstrip(".")
    return str(result_str)


def remove_variant_selectors(text: str) -> str:
    """絵文字のバリアントセレクタを削除する
    例: ⏲️ -> ⏲
    """
    return "".join(c for c in text if not (0xFE00 <= ord(c) <= 0xFE0F))
