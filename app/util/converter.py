import config

def man_hour_to_man_days(man_hour: float) -> float:
    '''人時を人日に変換する
    
    一人日は8時間とする
    '''

    return man_hour / config.MAN_HOUR_PER_DAY

