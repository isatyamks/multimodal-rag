import json
from typing import Dict, Any

from src.core.llm import AgentMessage, llmProvider
from src.engine.workflow.nodes.utils import print_phase
from src.engine.workflow.state import InvestigationState
from src.core.entities import CapabilityPlan, Capability

def get_planner_node(llm: llmProvider):
    def _planner(state: InvestigationState) -> Dict[str, Any]:
        from src.engine.workflow.nodes.utils import console
        print_phase("Planner Agent (Execution Planner)", style="bold magenta")
        
        # In a full implementation, we'd prompt the LLM to output Capabilities.
        # For this prototype we will mock the CapabilityPlan based on query keywords.
        plan = CapabilityPlan()
        plan.capabilities.append(Capability(name="Historical Deployments", description="Search historical deployment index", source_type="internal"))
        plan.capabilities.append(Capability(name="Recent PRs", description="Fetch PRs via GitHub MCP", source_type="external"))
        
        console.print(f"[magenta]Generated Capability Plan with {len(plan.capabilities)} capabilities.[/magenta]")
        return {"capability_plan": plan}

    return _planner
