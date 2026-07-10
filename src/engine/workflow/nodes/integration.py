from typing import Dict, Any
from src.engine.workflow.state import InvestigationState
from src.engine.workflow.nodes.utils import print_phase, console

def get_integration_node():
    def integration(state: InvestigationState) -> Dict[str, Any]:
        print_phase("Integration Layer", style="bold cyan")
        console.print("[cyan]Executing Capability Providers (Internal + MCP)...[/cyan]")
        return {"raw_context": {"data": "Mock raw data from providers"}}
    return integration
