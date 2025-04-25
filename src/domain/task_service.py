import copy
from domain.excuted_task import ExcutedTask
from domain.scheduled_task import ScheduledTask
from domain.name_labels.man_days_label import ManDaysLabel
from domain.task import Task


class TaskService:
    def get_changed_tasks(self, tasks: list[Task]):
        '''変更されたタスクを取得する'''
        changed_tasks = list(filter(
            lambda task: task.is_updated,
            tasks
        ))
        
        return changed_tasks


            
                
