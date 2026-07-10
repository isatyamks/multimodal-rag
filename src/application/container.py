from typing import Dict, Any
from pathlib import Path

from src.application.context import ApplicationContext
from src.infra.groq import GroqProvider
from src.infra.impls import FileSystemDatasetReader, CrossEncoderReranker, NetworkXExporter
from src.infra.retriever import BM25Retriever, DenseRetriever, HybridRetriever
from src.infra.messaging.file_bus import FileEventBus
from src.engine.ingestion.registry import EventRegistry
from src.engine.ingestion.translators.slack import SlackMessageTranslator
from src.engine.ingestion.service import EventIngestionService
from src.engine.triage.agent import TriageAgent
from src.engine.workflow.engine import InvestigationWorkflowEngine
from src.engine.analysis.impact import ImpactService
from src.data.graph import GraphService
from src.data.retrieval import RetrievalService

class ApplicationContainer:
    """
    Dependency injection container and application builder.
    Responsible for executing the heavy lifting of startup (loading data, building indexes)
    and returning a frozen ApplicationContext.
    """
    def __init__(self, settings: Dict[str, Any]):
        self.settings = settings

    def build(self) -> ApplicationContext:
        tenant_id = self.settings.get("tenant_id", "tenant_default")
        
        # 1. Base Infrastructure
        llm = GroqProvider()
        
        # 2. Dataset Loading (Simulating a DB/Storage layer)
        data_path = self.settings.get("data_path", "data")
        reader = FileSystemDatasetReader()
        dataset = reader.load(str(data_path))
        
        # 3. Graph Service
        # In a real system, we might load the cached graphml here
        graph_svc = GraphService(dataset)
        
        # 4. Retrieval Service
        bm25 = BM25Retriever()
        dense = DenseRetriever()
        reranker = CrossEncoderReranker()
        retriever = HybridRetriever(bm25, dense, reranker)
        retriever.index(dataset)
        retrieval_svc = RetrievalService(retriever)
        
        # 5. Core Engine Services
        impact_svc = ImpactService(graph_svc)
        workflow_engine = InvestigationWorkflowEngine(
            llm=llm,
            retrieval_svc=retrieval_svc,
            graph_svc=graph_svc,
            impact_svc=impact_svc
        )
        triage_agent = TriageAgent(llm)
        
        # 6. Event Ingestion Pipeline
        registry = EventRegistry()
        registry.register("SLACK_MESSAGE", SlackMessageTranslator())
        
        ingestion_svc = EventIngestionService(registry, dataset, graph_svc)
        event_bus = FileEventBus(data_dir="data/events")
        
        return ApplicationContext(
            tenant_id=tenant_id,
            settings=self.settings,
            llm=llm,
            triage_agent=triage_agent,
            workflow_engine=workflow_engine,
            event_bus=event_bus,
            ingestion_svc=ingestion_svc,
            graph_svc=graph_svc,
            retrieval_svc=retrieval_svc
        )
