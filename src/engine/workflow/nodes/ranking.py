from typing import Dict, Any
from src.engine.workflow.state import InvestigationState
from src.engine.workflow.nodes.utils import print_phase, console

def get_ranking_node():
    def ranking(state: InvestigationState) -> Dict[str, Any]:
        print_phase("Evidence Ranking", style="bold yellow")
        console.print("[yellow]Ranking and filtering evidence...[/yellow]")
        return {"ranked_evidence": []}
    return ranking
