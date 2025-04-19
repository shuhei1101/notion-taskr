from domain.task import Task


class TaskService:
    def get_changed_tasks(self, tasks: list[Task]):
        '''変更されたタスクを取得する'''
        changed_tasks = list(filter(
            lambda task: task.is_changed,
            tasks
        ))
        
        return changed_tasks