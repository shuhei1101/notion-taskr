from datetime import datetime, timezone
import pytz

def to_isoformat(dt: datetime) -> str:
    '''datetimeをISO8601形式(UTC, Z付き)に変換する
    naiveなdatetimeはJSTとして扱い、UTCに変換して返す
    例: 2023-10-01T12:00:00.000Z
    '''
    try:
        tokyo_tz = pytz.timezone('Asia/Tokyo')
        if dt.tzinfo is None:
            # naive datetimeはJSTとして扱う
            dt = tokyo_tz.localize(dt)
            dt = dt.astimezone(pytz.utc)
        else:
            # すでにtzinfoがある場合は、そのままUTCへ変換
            dt = dt.astimezone(pytz.utc)
        return dt.strftime('%Y-%m-%dT%H:%M:%S.') + f"{dt.microsecond // 1000:03d}Z"
    except Exception as e:
        raise ValueError(f'Invalid datetime: {dt}. Error: {e}')

# 動作確認用
if __name__ == '__main__':
    # 日本時間のテスト (datetime.now()でテスト)
    dt_jst = datetime.now(pytz.timezone('Asia/Tokyo'))  # 日本時間で取得
    print("JST:", to_isoformat(dt_jst))  # JST => UTC => 例: 2025-05-09T22:51:54.005Z

    # UTCのテスト (datetime.now()でUTCタイムゾーン)
    dt_utc = datetime.now(timezone.utc)  # UTCタイムゾーンで取得
    print("UTC:", to_isoformat(dt_utc))  # そのまま => 例: 2025-05-09T22:51:54.005Z

    # naiveなdatetime（ローカルタイムをJSTとして扱う）
    dt_naive = datetime.now()  # ローカルタイム（タイムゾーンなし）
    print("Naive:", to_isoformat(dt_naive))  # ローカルタイムをJSTとして扱い変換


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



