from typing import Any, Dict, List, TypedDict

from src.core.entities import EvidenceLedger, CapabilityPlan, Evidence


class InvestigationState(TypedDict):
    query: str
    tenant_id: str
    investigation_id: str
    
    # Rule Router & Planner
    intent: str
    capability_plan: CapabilityPlan
    
    # Core Data
    ledger: EvidenceLedger
    
    # Artifacts & Context
    raw_context: Dict[str, Any]
    normalized_evidence: List[Evidence]
    ranked_evidence: List[Evidence]
    
    # Hypothesis & Verification
    hypotheses: List[Dict[str, Any]]
    confidence_score: float
    
    # Remediation & Reporting
    blast_radius: Dict[str, Any]
    remediation_plan: List[Dict[str, Any]]
    report: str
    final_response: str
    
    # Control Flow
    loop_count: int
    next_action: str
    human_feedback: List[str]

