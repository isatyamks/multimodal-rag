from src.core.messaging import EventEnvelope
from src.engine.ingestion.registry import EventRegistry
from src.core.entities import Dataset, SlackMessage
from src.data.graph import GraphService
from rich.console import Console

console = Console()

class EventIngestionService:
    """
    Coordinates the translation and ingestion of events from the EventBus
    into the Dataset and GraphService.
    """
    def __init__(self, registry: EventRegistry, dataset: Dataset, graph_svc: GraphService):
        self.registry = registry
        self.dataset = dataset
        self.graph_svc = graph_svc

    def process_event(self, envelope: EventEnvelope) -> None:
        event = envelope.event
        translator = self.registry.get_translator(event.event_type)
        
        if not translator:
            console.print(f"[bold yellow]⚠️ No translator registered for event type: {event.event_type}[/bold yellow]")
            return
            
        try:
            entity = translator.translate(event)
            
            # Simple dispatcher for now. In reality, we'd use DatasetUpdater/GraphUpdater abstractions.
            if isinstance(entity, SlackMessage):
                self.dataset.slack_messages[entity.id] = entity
                if self.graph_svc and self.graph_svc.graph:
                    self.graph_svc.graph.add_node(entity.id, type="slack_message", obj=entity)
                    console.print(f"[bold green]✔ Ingested SlackMessage:[/bold green] {entity.id}")
            
        except Exception as e:
            console.print(f"[bold red]❌ Failed to ingest event {event.event_id}: {e}[/bold red]")
