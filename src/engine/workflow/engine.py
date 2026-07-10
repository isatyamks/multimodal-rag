from src.core.llm import llmProvider
from src.core.entities import EvidenceLedger
from src.data.graph import GraphService
from src.data.retrieval import RetrievalService
from src.engine.analysis.impact import ImpactService
from src.engine.change.owners import CodeOwnerService
from src.engine.change.commits import CommitAnalyzer
from src.engine.change.deployments import DeploymentAnalyzer
from src.engine.change.diffs import DiffAnalyzer
from src.engine.change.releases import ReleaseAnalyzer
from src.engine.workflow.builder import build_workflow

class InvestigationWorkflowEngine:
    def __init__(
        self,
        llm: llmProvider,
        retrieval_svc: RetrievalService,
        graph_svc: GraphService,
        impact_svc: ImpactService,
    ):
        self.llm = llm
        self.retrieval_svc = retrieval_svc
        self.graph_svc = graph_svc
        self.impact_svc = impact_svc
        self.deploy_analyzer = DeploymentAnalyzer(graph_svc)
        self.release_analyzer = ReleaseAnalyzer(graph_svc)
        self.commit_analyzer = CommitAnalyzer(graph_svc)
        self.diff_analyzer = DiffAnalyzer(graph_svc)
        self.code_owner_svc = CodeOwnerService(graph_svc)
        self.graph = build_workflow(self)

    def run(self, query: str, tenant_id: str = "tenant_default") -> str:
        print(
            f"\n\033[1mStarting Hub-and-Spoke Investigation for tenant '{tenant_id}' on query:\033[0m '{query}'\n"
        )
        st = {
            "query": query,
            "tenant_id": tenant_id,
            "investigation_id": "inv_test_001",
            "intent": "",
            "capability_plan": None,
            "ledger": EvidenceLedger(),
            "raw_context": {},
            "normalized_evidence": [],
            "ranked_evidence": [],
            "hypotheses": [],
            "confidence_score": 0.0,
            "blast_radius": {},
            "remediation_plan": [],
            "report": "",
            "final_response": "",
            "loop_count": 0,
            "next_action": "",
            "human_feedback": []
        }
        return self.graph.invoke(st)["final_response"]
