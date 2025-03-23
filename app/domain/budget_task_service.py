import re

from domain.budget_task import BudgetTask

class BudgetTaskService():
    '''Taskのドメインサービスクラス'''

    def get_name_with_man_days_tag(self, task: BudgetTask, actual_man_days: float):
        '''工数タグをタスク名に付与する

        タグ例: 予定工数が8人日で、実績工数が5人日の場合、
        [5/8人日]
        という文字列を返す

        ただし、既に工数タグが付与されている場合は、上書きする
        '''
        # 既に工数タグが付与されている場合は、上書きする
        pattern = r'\[.*人日\]'
        name_sub = re.sub(pattern, '', task.name).strip()
        
        # タスク名に工数タグを付与
        man_days_tag = f'[{actual_man_days}/{task.budget_man_hour}人日]'
        new_name = f'{name_sub} {man_days_tag}'
        return new_name
    
    def _has_man_days_tag(self, name: str):
        pattern = r'\[.*人日\]'
        return re.search(pattern, name)

if __name__ == '__main__':
    service = BudgetTaskService()
    if service._has_man_days_tag('TODOをタスクに昇格する [SN-377][3.875/4人日]'):
        print('OK')
    else:
        print('NG')



