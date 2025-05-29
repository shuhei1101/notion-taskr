from abc import ABC, abstractmethod


class Notifiable(ABC):

    @abstractmethod
    def notify(self, message: str) -> None:
        raise NotImplementedError("Subclasses must implement this method.")
