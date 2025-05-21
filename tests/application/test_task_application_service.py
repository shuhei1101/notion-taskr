# 動作確認用
import asyncio
from datetime import datetime
from notiontaskr.application.task_application_service import TaskApplicationService

from notiontaskr.util.converter import dt_to_month_start_end

service = TaskApplicationService()


def main():
    # _get_uptime()
    _daily_task()


def _daily_task():
    asyncio.run(service.daily_task())


def _get_uptime():
    start, end = dt_to_month_start_end(datetime(year=2025, month=5, day=1))
    uptime_data_by_tag = asyncio.run(
        service.get_uptime(
            from_=start,
            to=end,
            tags=["notion-api", "お小遣いクエストボード"],
        )
    )
    print(uptime_data_by_tag.to_json())


if __name__ == "__main__":
    main()
