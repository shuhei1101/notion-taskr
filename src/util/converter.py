import re

import config as config

def man_hour_to_man_days(man_hour: float) -> float:
    '''人時を人日に変換する'''

    return man_hour / config.MAN_HOUR_PER_DAY

def truncate_decimal(num: float) -> str:
    '''小数点以下を1桁に切り捨てる
    
    ただし、小数点以下が0の場合は整数部分のみ表示
    '''
    try:
        result_str = f'{num:.1f}'.rstrip('0').rstrip('.')
        return result_str
    except TypeError:
        raise ValueError(f'Invalid input: {num}. Must be a float or int.')

def clean_str(s):
    return re.sub(r'\s+|\u200b|\u200c|\u200d', '', s)


# 動作確認用
if __name__ == '__main__':
    print(clean_str("0.2/0.1")==("0.2/0.1"))