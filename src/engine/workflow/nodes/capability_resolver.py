from typing import Dict, Any
from src.engine.workflow.state import InvestigationState
from src.engine.workflow.nodes.utils import print_phase, console

def get_capability_resolver_node():
    def capability_resolver(state: InvestigationState) -> Dict[str, Any]:
        print_phase("Capability Resolver", style="bold blue")
        plan = state.get("capability_plan")
        if plan:
            console.print(f"[blue]Resolving {len(plan.capabilities)} capabilities into tasks...[/blue]")
        return {}
    return capability_resolver
