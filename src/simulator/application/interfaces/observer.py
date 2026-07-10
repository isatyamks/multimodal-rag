from abc import ABC, abstractmethod
from src.simulator.domain.decision.models import Decision
from src.simulator.domain.events.base import DomainEvent

class PlatformObserver(ABC):
    """
    Interface for adapters to observe state changes and emit platform events.
    """
    @abstractmethod
    def on_domain_event(self, event: DomainEvent, causal_decision: Decision | None) -> None:
        """
        Called when a domain event occurs in the World.
        """
        pass
