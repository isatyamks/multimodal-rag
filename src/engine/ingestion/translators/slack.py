from datetime import datetime
from src.engine.ingestion.translators.base import PlatformEventTranslator
from src.simulator.domain.events.base import BasePlatformEvent
from src.core.entities import SlackMessage

class SlackMessageTranslator(PlatformEventTranslator):
    def translate(self, event: BasePlatformEvent) -> SlackMessage:
        payload = event.payload
        return SlackMessage(
            id=f"{event.tenant_id}::{event.event_id}",
            tenant_id=event.tenant_id,
            channel=payload.get("channel", "unknown"),
            text=payload.get("text", ""),
            user_id=event.actor_id,
            timestamp=event.occurred_at
        )
