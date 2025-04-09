from datetime import datetime

def get_hours_diff(start_date: datetime, end_date: datetime):
    '''日付文字列の差分を計算する
    
    :param start_date: 開始日時
    :param end_date: 終了日時
    :return: 差分時間（時間単位）
    '''
    # 差分を計算
    diff = end_date - start_date

    # 差分を時間単位に変換
    hours_diff = diff.total_seconds() / 3600

    return hours_diff
