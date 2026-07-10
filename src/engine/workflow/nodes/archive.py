from typing import Dict, Any
from src.engine.workflow.state import InvestigationState
from src.engine.workflow.nodes.utils import print_phase, console

def get_archive_node():
    def archive(state: InvestigationState) -> Dict[str, Any]:
        print_phase("Investigation Archive", style="bold green")
        console.print("[green]Storing investigation report to knowledge platform...[/green]")
        return {}
    return archive
