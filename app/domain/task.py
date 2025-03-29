from dataclasses import dataclass
from typing import List

from app.domain.task_name import TaskName

@dataclass
class Task():
    '''タスクモデル'''
    page_id: str
    name: TaskName
    tags: List[str]
    

    
        
