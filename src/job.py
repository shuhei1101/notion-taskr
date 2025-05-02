import asyncio
from datetime import datetime
from application.task_application_service import TaskApplicationService
from infrastructure.operator import DateOperator
from infrastructure.task_search_condition import TaskSearchCondition

def run_job():
    condition = TaskSearchCondition().or_(
                    TaskSearchCondition().where_date(
                        operator=DateOperator.PAST_WEEK,
                    ),
                    TaskSearchCondition().where_date(
                        date=datetime.now().strftime('%Y-%m-%d'),
                        operator=DateOperator.ON_OR_AFTER
                    ),
                )
    
    service = TaskApplicationService()
    asyncio.run(service.regular_task(condition=condition))
 
if __name__ == "__main__":
    run_job()