from abc import ABC, abstractmethod

from notiontaskr.domain.scheduled_task import ScheduledTask
from notiontaskr.domain.value_objects.page_id import PageId


class IdFindable(ABC):
    @abstractmethod
    def find_by_page_id(self, page_id: PageId) -> ScheduledTask:
        """ページIDを指定してキャッシュから取得するメソッド"""
        pass