from typing import List

from src.core.contracts import IRetriever, SearchResult
from src.infra.telemetry import instrument


class RetrievalService:
    def __init__(self, retriever: IRetriever):
        self.retriever = retriever

    @instrument(span_name="retrieval_initial")
    def initial_retrieval(self, query: str, tenant_id: str) -> List[SearchResult]:
        """Blind search to give the Planner context before planning."""
        return self.retriever.search(query, tenant_id, top_k=5)

    @instrument(span_name="retrieval_deep")
    def deep_retrieval(
        self, planned_queries: List[str], tenant_id: str
    ) -> List[SearchResult]:
        """Targeted searches based on the generated investigation plan."""
        results = []
        for q in planned_queries:
            results.extend(self.retriever.search(q, tenant_id, top_k=5))
        return results
