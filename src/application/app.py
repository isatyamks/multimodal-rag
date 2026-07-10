from typing import Dict, Any

from src.application.context import ApplicationContext
from src.application.lifecycle import Lifecycle
from src.application.startup import RealtimeRuntime
from src.engine.triage.models import InvestigationRequest

class CodentirApplication(Lifecycle):
    """
    Main orchestration class for the Codentir Engine.
    Coordinates lifecycles and provides entrypoints for execution.
    """
    def __init__(self, context: ApplicationContext):
        self.context = context
        self.realtime = RealtimeRuntime(context)
        
    def initialize(self) -> None:
        print("[App] Initializing Codentir Application...")
        self.realtime.initialize()
        
    def start(self) -> None:
        print("[App] Starting background services...")
        self.realtime.start()
        
    def run(self, request: InvestigationRequest) -> str:
        """
        Executes an investigation based on a strongly-typed InvestigationRequest.
        """
        print(f"[App] Running investigation for query: {request.refined_query}")
        
        # We pass the refined_query to the workflow engine. 
        # In the future, we could pass the entire InvestigationRequest context.
        result = self.context.workflow_engine.run(
            query=request.refined_query, 
            tenant_id=self.context.tenant_id
        )
        return result
        
    def stop(self) -> None:
        print("[App] Stopping application...")
        self.realtime.stop()
        
    def shutdown(self) -> None:
        print("[App] Shutting down...")
        self.realtime.shutdown()
