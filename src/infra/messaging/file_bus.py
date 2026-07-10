import json
import time
import threading
from pathlib import Path
from datetime import datetime, timezone
from typing import Callable, Dict

from src.core.messaging import EventBus, EventEnvelope
from src.simulator.domain.events.base import BasePlatformEvent

class FileEventBus(EventBus):
    """
    A local file-based implementation of an EventBus.
    Uses .jsonl files for storage, encapsulating serialization and tailing.
    """
    def __init__(self, data_dir: str = "data/events"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._threads: list[threading.Thread] = []
        self._stop_events: list[threading.Event] = []

    def publish(self, topic: str, event: BasePlatformEvent) -> None:
        file_path = self.data_dir / f"{topic}.jsonl"
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(event.model_dump_json() + "\n")
        print(f"[EventBus] Published {event.event_type} ({event.event_id}) to {topic}")

    def subscribe(self, topic: str, handler: Callable[[EventEnvelope], None]) -> None:
        file_path = self.data_dir / f"{topic}.jsonl"
        stop_event = threading.Event()
        
        def _tail():
            file_path.parent.mkdir(parents=True, exist_ok=True)
            if not file_path.exists():
                file_path.touch()
                
            with open(file_path, "r", encoding="utf-8") as f:
                offset = 0
                while not stop_event.is_set():
                    line = f.readline()
                    if not line:
                        time.sleep(1)
                        continue
                    
                    try:
                        raw_data = json.loads(line)
                        event = BasePlatformEvent(**raw_data)
                        envelope = EventEnvelope(
                            topic=topic,
                            event=event,
                            received_at=datetime.now(timezone.utc),
                            offset=offset,
                            source="file_bus"
                        )
                        handler(envelope)
                        offset += 1
                    except Exception as e:
                        print(f"[EventBus] Failed to process event in {topic}: {e}")

        thread = threading.Thread(target=_tail, daemon=True)
        self._threads.append(thread)
        self._stop_events.append(stop_event)
        thread.start()
        print(f"[EventBus] Subscribed to {topic}")

    def stop_all(self):
        for stop_event in self._stop_events:
            stop_event.set()
        for thread in self._threads:
            thread.join()
