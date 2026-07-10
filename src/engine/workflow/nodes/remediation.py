import json
from src.core.llm import AgentMessage, llmProvider
from src.engine.workflow.nodes.utils import print_phase
from src.engine.workflow.state import InvestigationState
from src.config.prompt import REMEDIATION_AGENT_PROMPT

def get_remediation_node(llm: llmProvider):
    def _remediation_agent(state: InvestigationState):
        from src.engine.workflow.nodes.utils import console
        print_phase("Remediation Agent", style="bold magenta")
        
        hypotheses = state.get("hypotheses", [])
        survivors = [h for h in hypotheses if not h.get("verification", {}).get("is_disproved", False)]
        
        if not survivors:
            console.print("  [bold yellow]No verified hypotheses available for remediation.[/bold yellow]")
            return {"remediation_plan": []}

        best_hypothesis = survivors[0]
        
        prompt = REMEDIATION_AGENT_PROMPT.format(
            title=best_hypothesis.get('title', ''),
            description=best_hypothesis.get('description', '')
        )
        
        with console.status("[magenta]Generating remediation steps...[/magenta]", spinner="dots"):
            msg = llm.generate([AgentMessage(role="system", content=prompt)])
        
        try:
            content = msg.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            remediation_plan = json.loads(content.strip())
        except Exception as e:
            console.print(f"  [bold red]Failed to parse remediation JSON: {e}[/bold red]")
            remediation_plan = []
            
        console.print(f"  [cyan]Generated {len(remediation_plan)} remediation steps.[/cyan]")
        return {"remediation_plan": remediation_plan}

    return _remediation_agent
