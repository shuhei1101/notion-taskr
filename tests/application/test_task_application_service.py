import asyncio
from datetime import datetime
from notiontaskr.application.task_application_service import TaskApplicationService
from notiontaskr.util.converter import dt_to_month_start_end
from pytest import fixture


class Test_get_uptime:
    @fixture
    def service(self):
        # TaskApplicationServiceのインスタンスを作成
        return TaskApplicationService()

    def test_結合試験(self, service: TaskApplicationService):
        """タグ`notion-api`の2024/12は1:22の稼働実績がある"""
        dt = datetime(year=2024, month=12, day=1)
        start, end = dt_to_month_start_end(dt)
        uptime_data_by_tag = asyncio.run(
            service.get_uptime(
                from_=start,
                to=end,
                tags=["notion-api"],
            )
        )
        data = uptime_data_by_tag.get_data("notion-api")
        assert data.tag == "notion-api"
        assert data.uptime == 1.3666666666666667
