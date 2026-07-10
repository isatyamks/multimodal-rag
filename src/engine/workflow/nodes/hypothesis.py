import json
from src.core.llm import AgentMessage, llmProvider
from src.engine.workflow.nodes.utils import print_phase
from src.engine.workflow.state import InvestigationState
from src.config.prompt import HYPOTHESIS_AGENT_PROMPT

def get_hypothesis_generation_node(llm: llmProvider):
    def _hypothesis_agent(state: InvestigationState):
        from src.engine.workflow.nodes.utils import console
        print_phase("Hypothesis Agent", style="bold magenta")
        
        ledger = state.get("ledger")
        query = state.get("query", "")
        
        if not ledger or not ledger.entries:
            console.print("  [bold yellow]No evidence found. Cannot generate hypotheses.[/bold yellow]")
            return {"hypotheses": []}

        evidence_str = ledger.format_for_prompt()
        
        prompt = HYPOTHESIS_AGENT_PROMPT.format(query=query, evidence_str=evidence_str)
        
        with console.status("[magenta]Generating hypotheses based on ledger evidence...[/magenta]", spinner="dots"):
            msg = llm.generate([AgentMessage(role="system", content=prompt)])
        
        try:
            content = msg.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            hypotheses = json.loads(content.strip())
        except Exception as e:
            console.print(f"  [bold red]Failed to parse hypotheses JSON: {e}[/bold red]")
            hypotheses = []
            
        console.print(f"  [cyan]Generated {len(hypotheses)} hypotheses.[/cyan]")
        return {"hypotheses": hypotheses}

    return _hypothesis_agent
