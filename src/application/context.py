from dataclasses import dataclass
from typing import Dict, Any

from src.core.llm import llmProvider
from src.core.messaging import EventBus
from src.engine.triage.agent import TriageAgent
from src.engine.workflow.engine import InvestigationWorkflowEngine
from src.engine.ingestion.service import EventIngestionService
from src.data.graph import GraphService
from src.data.retrieval import RetrievalService

@dataclass(frozen=True)
class ApplicationContext:
    """
    Frozen data structure holding initialized dependencies.
    """
    tenant_id: str
    settings: Dict[str, Any]
    
    llm: llmProvider
    triage_agent: TriageAgent
    workflow_engine: InvestigationWorkflowEngine
    
    event_bus: EventBus
    ingestion_svc: EventIngestionService
    
    graph_svc: GraphService
    retrieval_svc: RetrievalService
