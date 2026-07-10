from typing import Dict, Optional, Type
from src.engine.ingestion.translators.base import PlatformEventTranslator

class EventRegistry:
    """
    Registry mapping event types to their specific translators.
    """
    def __init__(self):
        self._translators: Dict[str, PlatformEventTranslator] = {}

    def register(self, event_type: str, translator: PlatformEventTranslator) -> None:
        self._translators[event_type] = translator

    def get_translator(self, event_type: str) -> Optional[PlatformEventTranslator]:
        return self._translators.get(event_type)
