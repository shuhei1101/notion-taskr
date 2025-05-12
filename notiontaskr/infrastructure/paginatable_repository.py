from abc import ABC, abstractmethod
from typing import Any, Callable, Tuple
from notiontaskr.infrastructure.task_search_condition import TaskSearchCondition


class Paginatable(ABC):
    @abstractmethod
    async def find_by_condition_with_cursor(
        self,
        condition: TaskSearchCondition,
        on_error: Callable[[Exception, dict[str]], None],
        start_cursor: str = None,
    ) -> Tuple[list[Any], str, bool]:
        """
        ページネーション対応で条件に合うタスクを取得する
        Returns: (tasks, next_cursor, has_more)
        """
        pass
