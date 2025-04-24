class TaskUpdateProperties:
    '''タスクの更新用プロパティ辞書を生成するクラス'''

    def __init__(self):
        self.properties = {}

    def set_name(self, name: str):
        '''名前の更新'''
        self.properties['名前'] = {
            'title': [{'text': {'content': name}}]
        }
        return self

    def set_excuted_man_days(self, excuted_man_hour: float):
        '''実際の人日数の更新'''
        self.properties['人日(実)'] = {'number': excuted_man_hour}
        return self

    def set_status(self, status: str):
        '''ステータスの更新'''
        self.properties['ステータス'] = {'select': {'equals': status}}
        return self

    def set_scheduled_flag(self, scheduled_flag: bool):
        '''予定フラグの更新'''
        self.properties['予定フラグ'] = {'checkbox': {'equals': scheduled_flag}}
        return self

    def set_price(self, price: float):
        '''価格の更新'''
        self.properties['Price'] = {'number': price}
        return self

    def build(self):
        '''更新用の最終プロパティを返す'''
        return self.properties if self.properties else {}
