from src.application.context import ApplicationContext
from src.application.lifecycle import Lifecycle

class RealtimeRuntime(Lifecycle):
    """
    Isolates background infrastructure startup, specifically the Event Bus
    subscriptions and background consumers.
    """
    def __init__(self, context: ApplicationContext):
        self.context = context
        
    def initialize(self) -> None:
        # Pre-flight checks could go here
        pass
        
    def start(self) -> None:
        print("[RealtimeRuntime] Subscribing to Event Bus...")
        self.context.event_bus.subscribe(
            "simulator.events.raw", 
            self.context.ingestion_svc.process_event
        )
        print("[RealtimeRuntime] Event Ingestion Pipeline started.")
        
    def stop(self) -> None:
        # In a real implementation, we would unsubscribe or stop the bus
        print("[RealtimeRuntime] Stopping event consumers...")
        
    def shutdown(self) -> None:
        print("[RealtimeRuntime] RealtimeRuntime shut down.")
