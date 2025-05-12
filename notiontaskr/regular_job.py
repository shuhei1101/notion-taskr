import asyncio
from notiontaskr.application.task_application_service import TaskApplicationService


def main():
    """一分ごとに実行する処理"""
    service = TaskApplicationService()

    asyncio.run(service.regular_task())


if __name__ == "__main__":
    main()
