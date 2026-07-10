from abc import ABC, abstractmethod
from src.simulator.domain.events.base import BasePlatformEvent

class PlatformEventTranslator(ABC):
    """
    Translates a BasePlatformEvent into a Core Domain Entity.
    """
    @abstractmethod
    def translate(self, event: BasePlatformEvent) -> any:
        pass
