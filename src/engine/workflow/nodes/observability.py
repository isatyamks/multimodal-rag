import uuid
from datetime import datetime
from src.core.entities import LedgerEntry
from src.data.graph import GraphService
from src.engine.workflow.nodes.utils import print_phase
from src.engine.workflow.state import InvestigationState

def get_observability_node(graph_svc: GraphService):
    def _observability_agent(state: InvestigationState):
        from src.engine.workflow.nodes.utils import console
        print_phase("Observability Agent", style="bold magenta")
        
        ledger = state.get("ledger")
        retrieved_ids = state.get("retrieved_artifacts", [])
        
        observability_data = {}
        
        for artifact_id in retrieved_ids:
            node_data = graph_svc.graph.nodes.get(artifact_id, {})
            ntype = node_data.get("type", "")
            
            if ntype in ["log", "metric", "alert"] or any(x in artifact_id.lower() for x in ["log", "metric", "alert"]):
                content_summary = node_data.get("summary", f"Details for {artifact_id}")
                
                observability_data[artifact_id] = content_summary
                
                if ledger:
                    ledger.add_entry(LedgerEntry(
                        id=str(uuid.uuid4())[:8],
                        fact=f"Observability event {artifact_id}: {content_summary}",
                        source_type=ntype if ntype else "observability",
                        source_id=artifact_id,
                        timestamp=datetime.utcnow(),
                        confidence=0.99,
                        agent="ObservabilityAgent",
                        tags=["observability", ntype]
                    ))

        console.print(f"  [green]Observability Agent added {len(observability_data)} logs/metrics to ledger.[/green]")
        
        completed = state.get("completed_agents", [])
        if "observability_agent" not in completed:
            completed.append("observability_agent")

        return {
            "ledger": ledger,
            "completed_agents": completed,
            "observability_data": observability_data
        }

    return _observability_agent
