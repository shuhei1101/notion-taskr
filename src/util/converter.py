import config as config
import emoji
from datetime import datetime
from datetime import timedelta

def to_isoformat(dt: datetime) -> str:
    '''datetimeをISO8601形式に変換する
    日本時間(JST)をUTCに変換してからISO8601形式に変換する
    例: 2023-10-01T12:00:00.000Z
    '''
    try:
        dt = dt - timedelta(hours=9)
        # ISO形式に変換
        return dt.strftime('%Y-%m-%dT%H:%M:%S.') + f"{dt.microsecond // 1000:03d}Z"
    except Exception as e:
        raise ValueError(f'Invalid datetime: {dt}. Error: {e}')
def truncate_decimal(num: float) -> str:
    '''小数点以下を1桁に切り捨てる
    
    ただし、小数点以下が0の場合は整数部分のみ表示
    '''
    try:
        result_str = f'{num:.1f}'.rstrip('0').rstrip('.')
        return str(result_str)
    except TypeError:
        raise ValueError(f'Invalid input: {num}. Must be a float or int.')

def remove_variant_selectors(text):
    '''絵文字のバリアントセレクタを削除する
    例: ⏲️ -> ⏲
    '''
    return ''.join(c for c in text if not (0xfe00 <= ord(c) <= 0xfe0f))


# 動作確認用
if __name__ == '__main__':
    label = '🌳0/2'
    print(emoji.demojize(label))
    print(emoji.demojize(remove_variant_selectors(label)))
