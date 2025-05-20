# 動作確認用
import asyncio
from datetime import datetime
from notiontaskr.application.task_application_service import TaskApplicationService

from notiontaskr.util.converter import dt_to_month_start_end


if __name__ == "__main__":
    service = TaskApplicationService()
    start, end = dt_to_month_start_end(datetime(year=2025, month=5, day=1))
    uptime_data_by_tag = asyncio.run(
        service.get_uptime(
            from_=start,
            to=end,
            tags=["notion-api", "お小遣いクエストボード"],
        )
    )
    print(uptime_data_by_tag.to_json())
