from domain.task import Task


class TaskService:
    def get_updated_tasks(self, tasks: list[Task]):
        '''変更されたタスクを取得する'''
        updated_tasks = list(filter(
            lambda task: task.is_updated,
            tasks
        ))
        
        return updated_tasks
    