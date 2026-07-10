from datetime import datetime
from typing import Callable, Optional
from pydantic import BaseModel, ConfigDict
from src.simulator.domain.events.base import BasePlatformEvent

class EventEnvelope(BaseModel):
    """
    Wraps a domain platform event with transport-level metadata.
    This prevents infrastructure concerns (offsets, topics) from leaking into the domain payload.
    """
    model_config = ConfigDict(frozen=True)
    
    topic: str
    event: BasePlatformEvent
    received_at: datetime
    offset: Optional[int] = None
    source: str

class EventBus:
    """
    Abstract interface for publishing and subscribing to events.
    Consumers deal purely in strongly-typed Domain/Platform events and envelopes.
    Serialization and transport details are hidden in the implementations.
    """
    
    def publish(self, topic: str, event: BasePlatformEvent) -> None:
        raise NotImplementedError
        
    def subscribe(self, topic: str, handler: Callable[[EventEnvelope], None]) -> None:
        raise NotImplementedError
