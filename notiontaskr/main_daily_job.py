import asyncio
from notiontaskr.application.task_application_service import TaskApplicationService


def main():
    """デプロイ時に実行する処理"""
    service = TaskApplicationService()
    asyncio.run(service.daily_task())


if __name__ == "__main__":
    main()
