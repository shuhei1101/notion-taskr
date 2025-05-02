from domain.scheduled_task import ScheduledTask
from domain.value_objects.page_id import PageId
from infrastructure.id_findable import IdFindable
from infrastructure.scheduled_task_repository import ScheduledTaskRepository


class ScheduledTaskCache(IdFindable):
    def __init__(self, repo: ScheduledTaskRepository):
        self.repo = repo
        self._cache: dict[str, ScheduledTask] = {}

    async def find_by_page_id(self, page_id: PageId) -> ScheduledTask:
        if str(page_id) in self._cache:
            return self._cache[str(page_id)]

        task = await self.repo.find_by_page_id(page_id)
        self._cache[str(page_id)] = task
        return task
