from typing import Dict, Any
from src.simulator.application.interfaces.observer import PlatformObserver
from src.simulator.domain.decision.models import Decision
from src.simulator.domain.events.base import DomainEvent, BasePlatformEvent, PlatformEnum
from src.core.messaging import EventBus

class SlackAdapter(PlatformObserver):
    """
    Observes domain events and translates them into Slack PlatformEvents.
    """
    def __init__(self, event_bus: EventBus, topic: str = "simulator.events.raw", simulation_id: str = "sim_1", tick_number: int = 1):
        self.event_bus = event_bus
        self.topic = topic
        self.simulation_id = simulation_id
        self.tick_number = tick_number

    def on_domain_event(self, event: DomainEvent, causal_decision: Decision | None) -> None:
        # In a real implementation, we would filter which domain events we care about
        # e.g., if not isinstance(event, IncidentEscalatedEvent): return
        
        payload: Dict[str, Any] = {
            "channel": "#incidents",
            "text": f"Simulation Event Occurred: {event.event_id}"
        }
        
        platform_event = BasePlatformEvent(
            event_id=event.event_id,
            tenant_id=event.tenant_id,
            simulation_id=self.simulation_id,
            tick_number=self.tick_number,
            occurred_at=event.timestamp,
            event_type="SLACK_MESSAGE",
            actor_id=causal_decision.actor_id if causal_decision else "system",
            correlation_id=event.correlation_id,
            causation_id=None, # Extract from domain event if causal chain exists
            payload=payload,
            metadata={"source_platform": PlatformEnum.SLACK.value}
        )
        
        self.event_bus.publish(self.topic, platform_event)
