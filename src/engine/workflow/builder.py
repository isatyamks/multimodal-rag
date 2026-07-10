from langgraph.graph import END, StateGraph
from src.engine.workflow.state import InvestigationState

def build_workflow(self_obj):
    wf = StateGraph(InvestigationState)

    from src.engine.workflow.nodes.rule_router import get_rule_router_node
    from src.engine.workflow.nodes.planner import get_planner_node
    from src.engine.workflow.nodes.capability_resolver import get_capability_resolver_node
    from src.engine.workflow.nodes.integration import get_integration_node
    from src.engine.workflow.nodes.normalization import get_evidence_normalization_node
    from src.engine.workflow.nodes.ranking import get_ranking_node
    from src.engine.workflow.nodes.ledger_node import get_evidence_ledger_node
    from src.engine.workflow.nodes.hypothesis import get_hypothesis_generation_node
    from src.engine.workflow.nodes.verification import get_verification_node
    from src.engine.workflow.nodes.confidence import get_confidence_node
    from src.engine.workflow.nodes.root_cause import get_root_cause_analysis_node
    from src.engine.workflow.nodes.remediation import get_remediation_node
    from src.engine.workflow.nodes.report import get_report_node
    from src.engine.workflow.nodes.archive import get_archive_node
    from src.engine.workflow.nodes.qa import get_qa_node

    wf.add_node("rule_router", get_rule_router_node(self_obj.llm))
    wf.add_node("planner", get_planner_node(self_obj.llm))
    wf.add_node("capability_resolver", get_capability_resolver_node())
    wf.add_node("integration", get_integration_node())
    wf.add_node("normalization", get_evidence_normalization_node())
    wf.add_node("ranking", get_ranking_node())
    wf.add_node("ledger", get_evidence_ledger_node())
    wf.add_node("hypothesis", get_hypothesis_generation_node(self_obj.llm))
    wf.add_node("verification", get_verification_node(self_obj.llm))
    wf.add_node("confidence", get_confidence_node())
    wf.add_node("root_cause", get_root_cause_analysis_node())
    wf.add_node("remediation", get_remediation_node(self_obj.llm))
    wf.add_node("report", get_report_node())
    wf.add_node("archive", get_archive_node())
    wf.add_node("qa_generation", get_qa_node(self_obj.llm, self_obj.graph_svc))

    wf.set_entry_point("rule_router")

    def route_after_router(s):
        if s.get("intent") == "GENERAL_QA":
            return "qa_generation"
        return "planner"

    wf.add_conditional_edges("rule_router", route_after_router)

    # Linear flow for the initial phase
    wf.add_edge("planner", "capability_resolver")
    wf.add_edge("capability_resolver", "integration")
    wf.add_edge("integration", "normalization")
    wf.add_edge("normalization", "ranking")
    wf.add_edge("ranking", "ledger")
    wf.add_edge("ledger", "hypothesis")
    
    # Hypothesis -> Verification -> Confidence
    wf.add_edge("hypothesis", "verification")
    wf.add_edge("verification", "confidence")

    # The iterative confidence loop
    def route_after_confidence(s):
        nxt = s.get("next_action")
        if nxt in ["ESCALATE", "INVESTIGATE_MORE"]:
            return "planner" # Iterative loop back to planner
        return "root_cause"

    wf.add_conditional_edges("confidence", route_after_confidence)

    # Root Cause -> Remediation -> Report -> Archive -> END
    wf.add_edge("root_cause", "remediation")
    wf.add_edge("remediation", "report")
    wf.add_edge("report", "archive")
    wf.add_edge("archive", END)
    
    # General QA ends directly
    wf.add_edge("qa_generation", END)

    return wf.compile()
