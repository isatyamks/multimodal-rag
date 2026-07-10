from abc import ABC, abstractmethod

class Lifecycle(ABC):
    """
    Formal interface for managing application or component lifecycles.
    """
    @abstractmethod
    def initialize(self) -> None:
        pass
        
    @abstractmethod
    def start(self) -> None:
        pass
        
    @abstractmethod
    def stop(self) -> None:
        pass
        
    @abstractmethod
    def shutdown(self) -> None:
        pass
