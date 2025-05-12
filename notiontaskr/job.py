import asyncio
from datetime import datetime
from notiontaskr.application.task_application_service import TaskApplicationService

def run_job():
    service = TaskApplicationService()
    # もし0時0分~0時1分ならdaily_taskを実行
    now = datetime.now()
    if now.hour == 0 and now.minute == 0:
        # 0時00分~0時01分の間に実行
        asyncio.run(service.daily_task())
    else:
        asyncio.run(service.regular_task())
    
def run_deployment_tasks():
    """デプロイ時に実行するタスク"""
    service = TaskApplicationService()
    asyncio.run(service.daily_task())

if __name__ == "__main__":
    run_job()