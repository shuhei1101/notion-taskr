from domain.name_tag import NameTag


class TagBuilder:
    '''NameTagを生成するクラス'''
    def build_id_tag(self, id_prefix: str, id_number: str) -> str:
        '''IDタグを生成する'''
        return NameTag(
            key=id_prefix,
            value=id_number
        )
    
    def build_man_days_tag(self, budget_man_days: float, actual_man_days: float) -> str:
        '''工数タグを生成する'''
        return NameTag(
            key='人日',
            value=f'{actual_man_days}/{budget_man_days}'
        )
    

