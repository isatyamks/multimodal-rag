from typing import Dict, Any
from src.engine.workflow.state import InvestigationState
from src.engine.workflow.nodes.utils import print_phase, console

def get_evidence_ledger_node():
    def ledger_node(state: InvestigationState) -> Dict[str, Any]:
        print_phase("Evidence Ledger (Deterministic)", style="bold white")
        console.print("[white]Deduplicating and inserting ranked evidence...[/white]")
        return {}
    return ledger_node
