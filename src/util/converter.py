import config as config

def man_hour_to_man_days(man_hour: float) -> float:
    '''人時を人日に変換する'''

    return man_hour / config.MAN_HOUR_PER_DAY

def truncate_decimal(num: float) -> str:
    '''小数点以下を1桁に切り捨てる
    
    ただし、小数点以下が0の場合は整数部分のみ表示
    '''
    return f'{num:.1f}'.rstrip('0').rstrip('.')