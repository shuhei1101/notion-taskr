from datetime import datetime
from application.task_application_service import TaskApplicationService
from infrastructure.operator import DateOperator
from infrastructure.task_search_condition import TaskSearchConditions

def run_job():
    condition = TaskSearchConditions().or_(
                    TaskSearchConditions().where_date(
                        operator=DateOperator.PAST_WEEK,
                    ),
                    TaskSearchConditions().where_date(
                        date=datetime.now().strftime('%Y-%m-%d'),
                        operator=DateOperator.ON_OR_AFTER
                    ),
                )
    
    service = TaskApplicationService()
    service.regular_task(condition=condition)
 
if __name__ == "__main__":
    run_job()