from abc import ABC, abstractmethod


class Notifiable(ABC):

    @abstractmethod
    async def notify(self, message: str) -> None:
        raise NotImplementedError("Subclasses must implement this method.")
