from datetime import datetime


def to_isoformat(dt: datetime) -> str:
    """datetimeをISO8601形式(UTC, Z付き)に変換する

    dtはUTCのdatetimeを想定。JSTは受け付けない。
    例: 2023-10-01T12:00:00.000Z
    """
    try:
        return dt.strftime("%Y-%m-%dT%H:%M:%S.") + f"{dt.microsecond // 1000:03d}Z"
    except Exception as e:
        raise ValueError(f"Invalid datetime: {dt}. Error: {e}")


def truncate_decimal(num: float) -> str:
    """小数点以下を1桁に切り捨てる

    ただし、小数点以下が0の場合は整数部分のみ表示
    """
    try:
        result_str = f"{num:.1f}".rstrip("0").rstrip(".")
        return str(result_str)
    except TypeError:
        raise ValueError(f"Invalid input: {num}. Must be a float or int.")


def remove_variant_selectors(text: str) -> str:
    """絵文字のバリアントセレクタを削除する
    例: ⏲️ -> ⏲
    """
    return "".join(c for c in text if not (0xFE00 <= ord(c) <= 0xFE0F))
