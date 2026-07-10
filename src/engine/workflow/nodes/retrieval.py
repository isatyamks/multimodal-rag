import uuid
import hashlib
import json
from datetime import datetime
from src.core.entities import LedgerEntry
from src.core.llm import AgentMessage, llmProvider
from src.data.graph import GraphService
from src.data.retrieval import RetrievalService
from src.engine.workflow.nodes.utils import print_phase
from src.engine.workflow.state import InvestigationState
from src.infra.impls import NetworkXExporter

ENTITY_EXTRACTION_PROMPT = """Extract the top 5 concrete architectural entities (Service names, Databases, Repositories, Deployments, Incidents, or Tickets) mentioned in this text. 
Return ONLY a JSON list of strings representing the entity IDs or names. Example: ["srv-payment", "redis", "INC-123"].

Text:
{text}
"""

def get_retrieval_node(retrieval_svc: RetrievalService, graph_svc: GraphService, llm: llmProvider):
    def _retrieval_agent(state: InvestigationState):
        from src.engine.workflow.nodes.utils import console
        print_phase("Retrieval Agent", style="bold magenta")
        
        search_query = state["query"]
        if state.get("human_feedback"):
            search_query += " " + " ".join(state["human_feedback"])

        with console.status("[cyan]Retrieving relevant artifacts...[/cyan]", spinner="dots"):
            results = retrieval_svc.retriever.search(search_query, state["tenant_id"], top_k=8)
        
        ledger = state.get("ledger")
        
        for r in results:
            entry = LedgerEntry(
                id=str(uuid.uuid4())[:8],
                fact=f"Retrieved content: {r.content[:200]}...",
                source_type=r.artifact_type,
                source_id=r.artifact_id,
                timestamp=datetime.utcnow(),
                confidence=r.score,
                agent="RetrievalAgent",
                tags=["retrieval", r.artifact_type]
            )
            if ledger:
                ledger.add_entry(entry)
                
        console.print(f"  [green]Retrieval Agent added {len(results)} entries to ledger.[/green]")
        
        # Entity Extraction
        seed_nodes = [r.artifact_id for r in results]
        try:
            combined_text = "\n".join([r.content for r in results])
            prompt = ENTITY_EXTRACTION_PROMPT.format(text=combined_text[:3000])
            with console.status("[magenta]Extracting key architectural entities...[/magenta]", spinner="dots"):
                msg = llm.generate([AgentMessage(role="system", content=prompt)])
            content = msg.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            parsed = json.loads(content.strip())
            if isinstance(parsed, list):
                extracted = []
                for e in parsed:
                    if "::" not in str(e):
                        extracted.append(f"{state['tenant_id']}::{e}")
                    else:
                        extracted.append(str(e))
                seed_nodes.extend(extracted)
        except Exception as e:
            console.print(f"  [bold yellow]Entity extraction failed, falling back to artifact IDs. ({str(e)})[/bold yellow]")

        investigation_id = state.get("investigation_id")
        if not investigation_id:
            ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            short_uuid = str(uuid.uuid4())[:5]
            investigation_id = f"investigation_{ts}_{short_uuid}"

        if seed_nodes:
            with console.status("[cyan]Expanding investigation graph...[/cyan]", spinner="dots"):
                query_graph = graph_svc.expand_query_graph(seed_nodes, node_budget=500)
            
            # Export subgraph
            exporter = NetworkXExporter()
            out_dir = f"graph/{state['tenant_id']}/investigations"
            import os
            os.makedirs(out_dir, exist_ok=True)
            
            exporter.export(query_graph, out_dir, f"{investigation_id}.graphml")
            
            # Save investigation metadata
            meta_path = f"{out_dir}/{investigation_id}.json"
            meta_data = {
                "query": search_query,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "seed_nodes": seed_nodes,
                "retrieved_artifacts": [r.artifact_id for r in results],
                "confidence": None
            }
            with open(meta_path, "w") as f:
                json.dump(meta_data, f, indent=2)

            console.print(f"  [dim]Exported query graph and metadata to {out_dir}/{investigation_id}[/dim]")

        completed = state.get("completed_agents", [])
        if "retrieval_agent" not in completed:
            completed.append("retrieval_agent")
            
        return {
            "investigation_id": investigation_id,
            "ledger": ledger,
            "completed_agents": completed,
            "retrieved_artifacts": [r.artifact_id for r in results]
        }

    return _retrieval_agent
