import time
from abc import ABC, abstractmethod

class TickStrategy(ABC):
    @abstractmethod
    def wait(self) -> None:
        pass

class FixedIntervalStrategy(TickStrategy):
    def __init__(self, interval_seconds: float = 5.0):
        self.interval_seconds = interval_seconds

    def wait(self) -> None:
        time.sleep(self.interval_seconds)

class ManualStepStrategy(TickStrategy):
    def wait(self) -> None:
        input("Press Enter to execute the next tick...")
