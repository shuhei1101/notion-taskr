import emoji


def has_emoji(s: str) -> bool:
    """文字列に絵文字が含まれているかを判定する関数"""

    return any(char in emoji.EMOJI_DATA for char in s)


def is_emoji_matches(emoji1: str, emoji2: str) -> bool:
    """絵文字が一致するかを判定する関数"""

    return emoji.demojize(emoji1) == emoji.demojize(emoji2)
