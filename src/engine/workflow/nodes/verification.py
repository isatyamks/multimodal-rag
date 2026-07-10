import json
from src.core.llm import AgentMessage, llmProvider
from src.engine.workflow.nodes.utils import print_phase
from src.engine.workflow.state import InvestigationState
from src.config.prompt import VERIFICATION_AGENT_PROMPT

def get_verification_node(llm: llmProvider):
    def _verification_agent(state: InvestigationState):
        from src.engine.workflow.nodes.utils import console
        print_phase("Verification Agent", style="bold magenta")
        
        ledger = state.get("ledger")
        hypotheses = state.get("hypotheses", [])
        
        if not hypotheses or not ledger:
            console.print("  [bold yellow]No hypotheses or ledger found to verify.[/bold yellow]")
            return {"hypotheses": hypotheses}

        evidence_str = ledger.format_for_prompt()
        
        verified_hypotheses = []
        for i, hyp in enumerate(hypotheses):
            prompt = VERIFICATION_AGENT_PROMPT.format(
                title=hyp.get("title", ""),
                description=hyp.get("description", ""),
                evidence_str=evidence_str
            )
            
            with console.status(f"[magenta]Verifying hypothesis {i+1}/{len(hypotheses)}...[/magenta]", spinner="dots"):
                msg = llm.generate([AgentMessage(role="system", content=prompt)])
            
            try:
                content = msg.content
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                
                verification_result = json.loads(content.strip())
            except Exception:
                verification_result = {"is_disproved": False, "critique": "Failed to parse verification."}
                
            hyp["verification"] = verification_result
            verified_hypotheses.append(hyp)
            
            if verification_result.get("is_disproved"):
                console.print(f"  [bold red][REJECTED][/bold red] Hypothesis '{hyp.get('title')}' disproved.")
            else:
                console.print(f"  [bold green][SURVIVED][/bold green] Hypothesis '{hyp.get('title')}' survived verification.")

        return {"hypotheses": verified_hypotheses}

    return _verification_agent
