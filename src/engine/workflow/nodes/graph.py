import uuid
from datetime import datetime
from src.core.entities import LedgerEntry
from src.data.graph import GraphService
from src.engine.workflow.nodes.utils import print_phase
from src.engine.workflow.state import InvestigationState

def get_graph_node(graph_svc: GraphService):
    def _graph_agent(state: InvestigationState):
        print_phase("Graph Agent")
        
        ledger = state.get("ledger")
        retrieved_ids = state.get("retrieved_artifacts", [])
        
        from src.engine.workflow.nodes.utils import console

        
        paths = []
        for a_id in retrieved_ids:
            p = graph_svc.find_causal_paths(a_id, max_depth=3)
            paths.extend(p)

        for path in paths[:5]:
            path_str = " -> ".join([node.get("type", "Unknown") + ":" + node.get("id", "") for node in path])
            
            entry = LedgerEntry(
                id=str(uuid.uuid4())[:8],
                fact=f"Found causal path: {path_str}",
                source_type="graph_traversal",
                source_id="networkx_graph",
                timestamp=datetime.utcnow(),
                confidence=0.85,
                agent="GraphAgent",
                tags=["causal_path", "graph"]
            )
            if ledger:
                ledger.add_entry(entry)
                
        console.print(f"  [green]Graph Agent added {min(len(paths), 5)} causal paths to ledger.[/green]")
        
        completed = state.get("completed_agents", [])
        if "graph_agent" not in completed:
            completed.append("graph_agent")
            
        return {
            "ledger": ledger,
            "completed_agents": completed,
            "evidence_paths": paths
        }

    return _graph_agent
