from typing import Dict, Any
from src.engine.workflow.state import InvestigationState
from src.engine.workflow.nodes.utils import print_phase, console

def get_root_cause_analysis_node():
    def root_cause(state: InvestigationState) -> Dict[str, Any]:
        print_phase("Root Cause Analysis", style="bold red")
        console.print("[red]Determining probable root cause and blast radius...[/red]")
        return {}
    return root_cause
