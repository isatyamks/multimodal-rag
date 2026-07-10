from src.engine.workflow.nodes.utils import print_phase
from src.engine.workflow.state import InvestigationState

def get_confidence_node():
    def _confidence_engine(state: InvestigationState):
        from src.engine.workflow.nodes.utils import console
        print_phase("Confidence Engine", style="bold magenta")
        
        hypotheses = state.get("hypotheses", [])
        ledger = state.get("ledger")
        
        if not hypotheses or not ledger:
            console.print("  [bold yellow]No hypotheses to score.[/bold yellow]")
            return {"confidence_score": 0.0}

        survivors = [h for h in hypotheses if not h.get("verification", {}).get("is_disproved", False)]
        
        loop_count = state.get("loop_count", 0) + 1

        if not survivors:
            console.print("  [bold red]All hypotheses were disproved![/bold red]")
            next_action = "ESCALATE"
            if loop_count > 2:
                console.print("  [bold yellow]Max loops reached. Forcing remediation.[/bold yellow]")
                next_action = "REMEDIATE"
            return {"confidence_score": 0.1, "next_action": next_action, "loop_count": loop_count}
            
        best_hypothesis = survivors[0]
        
        evidence_ids = best_hypothesis.get("supporting_evidence_ids", [])
        supporting_entries = [e for e in ledger.entries if str(e.id) in evidence_ids]
        
        has_graph = any("graph" in e.tags for e in supporting_entries)
        has_observability = any("observability" in e.tags for e in supporting_entries)
        has_change = any("change" in e.tags for e in supporting_entries)
        
        verification_critique = best_hypothesis.get("verification", {}).get("critique", "")
        verification_score = 0.9 if "strong" in verification_critique.lower() else 0.7
        
        evidence_strength = min(1.0, len(supporting_entries) * 0.2)
        graph_support = 1.0 if has_graph else 0.0
        observability_support = 1.0 if has_observability else 0.0
        historical_match = 0.0
        
        confidence = (
            (0.35 * evidence_strength) +
            (0.25 * graph_support) +
            (0.20 * observability_support) +
            (0.10 * historical_match) +
            (0.10 * verification_score)
        )
        
        console.print(f"  [cyan]Calculated Confidence: {confidence:.2f}[/cyan]")
        
        
        
        next_action = "REMEDIATE"
        if loop_count > 2:
            console.print("  [bold yellow]Max loops reached. Forcing remediation.[/bold yellow]")
            next_action = "REMEDIATE"
        elif confidence < 0.6:
            next_action = "INVESTIGATE_MORE"
            console.print("  [bold yellow]Confidence low (<0.6). Need more investigation.[/bold yellow]")
        elif confidence < 0.8:
            next_action = "ESCALATE"
            console.print("  [bold yellow]Confidence moderate (0.6-0.8). Escalating to human.[/bold yellow]")
        else:
            console.print("  [bold green]Confidence high (>0.8). Proceeding to remediation.[/bold green]")
            
        return {
            "confidence_score": confidence,
            "next_action": next_action,
            "loop_count": loop_count
        }

    return _confidence_engine
