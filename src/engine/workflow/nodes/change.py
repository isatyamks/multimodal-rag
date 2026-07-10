import uuid
from datetime import datetime
from src.core.entities import LedgerEntry
from src.data.graph import GraphService
from src.engine.change.owners import CodeOwnerService
from src.engine.change.deployments import DeploymentAnalyzer
from src.engine.change.diffs import DiffAnalyzer
from src.engine.change.releases import ReleaseAnalyzer
from src.engine.workflow.nodes.utils import print_phase
from src.engine.workflow.state import InvestigationState

def get_change_node(
    graph_svc: GraphService,
    deploy_analyzer: DeploymentAnalyzer,
    release_analyzer: ReleaseAnalyzer,
    diff_analyzer: DiffAnalyzer,
    code_owner_svc: CodeOwnerService,
):
    def _change_agent(state: InvestigationState):
        from src.engine.workflow.nodes.utils import console
        print_phase("Change Intelligence Agent", style="bold magenta")
        
        ledger = state.get("ledger")
        retrieved_ids = state.get("retrieved_artifacts", [])
        
        diff_data_map = {}
        owners_map = {}
        
        for artifact_id in retrieved_ids:
            node_data = graph_svc.graph.nodes.get(artifact_id, {})
            ntype = node_data.get("type", "")
            
            if ntype == "commit" or "commit" in artifact_id.lower():
                diff_data = diff_analyzer.extract_diff(artifact_id)
                owners = code_owner_svc.extract_owners(artifact_id)
                
                diff_data_map[artifact_id] = diff_data
                owners_map[artifact_id] = owners
                
                if ledger:
                    ledger.add_entry(LedgerEntry(
                        id=str(uuid.uuid4())[:8],
                        fact=f"Commit {artifact_id} modified files. Diff: {str(diff_data)[:100]}... Owners: {owners}",
                        source_type="commit_diff",
                        source_id=artifact_id,
                        timestamp=datetime.utcnow(),
                        confidence=0.95,
                        agent="ChangeAgent",
                        tags=["change", "commit", "diff"]
                    ))
                    
            elif ntype == "deployment":
                assoc = deploy_analyzer.analyze(artifact_id)
                if ledger:
                    ledger.add_entry(LedgerEntry(
                        id=str(uuid.uuid4())[:8],
                        fact=f"Deployment {artifact_id} includes: {assoc}",
                        source_type="deployment",
                        source_id=artifact_id,
                        timestamp=datetime.utcnow(),
                        confidence=0.98,
                        agent="ChangeAgent",
                        tags=["change", "deployment"]
                    ))

        console.print(f"  [green]Change Agent added diffs & deployments to ledger.[/green]")
        
        completed = state.get("completed_agents", [])
        if "change_agent" not in completed:
            completed.append("change_agent")

        return {
            "ledger": ledger,
            "completed_agents": completed,
            "diff_data": diff_data_map,
            "owners": owners_map
        }

    return _change_agent
