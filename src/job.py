from application.task_application_service import TaskApplicationService

def run_job():
    service = TaskApplicationService()
    service.regular_task()
 
if __name__ == "__main__":
    run_job()