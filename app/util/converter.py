import config

def man_hour_to_man_days(man_hour: float) -> float:
    '''人時を人日に変換する'''

    return man_hour / config.MAN_HOUR_PER_DAY

