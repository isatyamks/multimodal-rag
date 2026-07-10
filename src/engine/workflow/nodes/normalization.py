from typing import Dict, Any
from src.engine.workflow.state import InvestigationState
from src.engine.workflow.nodes.utils import print_phase, console

def get_evidence_normalization_node():
    def normalization(state: InvestigationState) -> Dict[str, Any]:
        print_phase("Evidence Normalization", style="bold green")
        console.print("[green]Normalizing raw context into Evidence V1 schema...[/green]")
        return {"normalized_evidence": []}
    return normalization
