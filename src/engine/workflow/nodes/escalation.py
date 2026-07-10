from src.engine.workflow.nodes.utils import print_phase
from src.engine.workflow.state import InvestigationState

def get_escalation_node():
    def _escalation_agent(state: InvestigationState):
        from src.engine.workflow.nodes.utils import console
        print_phase("Human Escalation Agent", style="bold magenta")
        
        confidence = state.get("confidence_score", 0.0)
        hypotheses = state.get("hypotheses", [])
        
        console.print(f"  [bold yellow]Investigation reached low confidence ({confidence:.2f}). Escalating to human.[/bold yellow]")
        
        if hypotheses:
            console.print(f"  [dim]Top Hypothesis: {hypotheses[0].get('title')}[/dim]")
            
        console.print("  [cyan][SIMULATION] Human provides missing evidence to continue...[/cyan]")
        
        simulated_feedback = "I checked Datadog, the DB CPU spiked to 100% at the exact same time."
        
        feedback_list = state.get("human_feedback", [])
        feedback_list.append(simulated_feedback)
        
        return {
            "human_feedback": feedback_list,
            "next_action": "REPLAN",
            "required_agents": [],
            "completed_agents": []
        }

    return _escalation_agent
