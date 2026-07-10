from src.core.llm import AgentMessage, llmProvider
from src.engine.workflow.nodes.utils import print_phase
from src.engine.workflow.state import InvestigationState
from src.config.prompt import RULE_ROUTER_PROMPT

def get_rule_router_node(llm: llmProvider):
    def _rule_router(state: InvestigationState):
        from src.engine.workflow.nodes.utils import console
        print_phase("Rule Router", style="bold yellow")
        
        query = state.get("query", "").lower()
        
        incident_keywords = ["outage", "500", "error", "latency", "failing", "fail", "failure", "crash", "incident", "alert", "down", "broke", "issue", "bug"]
        
        intent = "GENERAL_QA"
        for kw in incident_keywords:
            if kw in query:
                intent = "INVESTIGATION"
                break
                
        if intent == "GENERAL_QA":
            prompt = RULE_ROUTER_PROMPT.format(query=query)
            with console.status("[yellow]Determining intent...[/yellow]", spinner="dots"):
                msg = llm.generate([AgentMessage(role="system", content=prompt)])
            if "INVESTIGATION" in msg.content.upper():
                intent = "INVESTIGATION"

        console.print(f"  [yellow]Routed Intent:[/yellow] [bold]{intent}[/bold]")
        
        return {
            "intent": intent,
            "required_agents": [],
            "completed_agents": [],
            "hypotheses": [],
            "human_feedback": []
        }

    return _rule_router
