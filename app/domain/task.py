from dataclasses import dataclass

@dataclass
class Task():
    '''タスクモデル'''
    page_id: str
    name: str
    tag: str

        
