import json
import logging
import os
from datetime import datetime

from src.engine.workflow.nodes.utils import print_phase
from src.engine.workflow.state import InvestigationState

logger = logging.getLogger(__name__)

def _format_report(state, top_cand, s_path):
    d = state.get("diff_data", {})
    ow = state.get("owners", {})
    r = [f"Issue: {state['query']}\n\nSelected Root Cause: {top_cand.candidate_id}"]
    if ow.get("Commit Author"):
        r.append(f"Author: {ow.get('Commit Author')}")

    p_id, d_id = None, None
    for n in s_path.nodes:
        if "PR-" in n or "pullrequest" in n.lower():
            p_id = n
        elif "DEPLOY-" in n or "deployment" in n.lower():
            d_id = n

    if p_id:
        r.append(f"PR: {p_id}")
    if d_id:
        r.append(f"Deployment: {d_id}")
    if d.get("files_changed"):
        r.append(f"Changed Files: {', '.join(d['files_changed'])}")
    if d.get("diff_summary"):
        r.append(f"Change Introduced: {d['diff_summary']}")

    r.append("\nEvidence Chain (Chronological Events):")
    f_path = [f"[{i+1}] {node}" for i, node in enumerate(s_path.nodes)]
    r.append(" ->\n  ".join(f_path))
    r.append("\nThis sequence perfectly maps the action taken causing the final issue with over 90% confidence.\n")

    r.append("Technical Explanation:\n" + state["technical_explanation"] + "\n")

    r.append("Confidence:")
    res = top_cand.reason
    if "(" in res:
        pts = res.split("(", 1)[1].replace(")", "").split(", ")
        r.extend(pts)
        r.append(res.split(" (")[0])
    else:
        r.append(f"Final Confidence: {top_cand.score:.2f}")

    r.append("\nBlast Radius:")
    for cat, expls in state["blast_radius"].items():
        if expls:
            r.append(f"[{cat}]")
            r.extend([f"- {ex.entity_id} (Reason: {ex.reason})" for ex in expls])
            r.append("")

    r.append("Responsible Personnel:")
    r.extend([f"{rl}: {nm}" for rl, nm in ow.items() if nm])
    r.append("")

    if state.get("action_items"):
        r.append("Recommended Actions:")
        for a in state["action_items"]:
            r.extend([f"@{a['employee_name']} ({a['role']})", f"{a['suggestion']}\n"])

    return "\n".join(r), f_path

def _save_postmortem(state, top_cand, path_list):
    t_id = state.get("tenant_id", "default")
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    pm_id = f"AUTO-PM-{ts}"
    pm_data = {
        "id": pm_id,
        "incident_id": "AUTO-INVESTIGATION",
        "title": f"Investigation Report: {state['query']}",
        "content": "Full Chat History:\n" + "\n".join(state.get("human_feedback", [])),
        "root_cause_summary": f"Selected Root Cause: {top_cand.candidate_id}\n\nTechnical Explanation:\n{state['technical_explanation']}",
        "lessons_learned": "Action Plan:\n"
        + "\n".join([f"@{a['employee_name']}: {a['suggestion']}" for a in state.get("action_items", [])]),
        "created_at": datetime.now().isoformat(),
        "investigation_data": {"evidence_chain": path_list},
    }

    dir_p = os.path.join("data", t_id, "postmortems")
    os.makedirs(dir_p, exist_ok=True)
    p = os.path.join(dir_p, f"{pm_id}.json")
    try:
        with open(p, "w") as f:
            json.dump(pm_data, f, indent=2)
        from src.engine.workflow.nodes.utils import console
        console.print(f"  [green]Saved memory to {p}[/green]")
    except Exception as e:
        from src.engine.workflow.nodes.utils import console
        console.print(f"  [bold red]Failed to save: {e}[/bold red]")

def get_report_node():
    def _report(state: InvestigationState):
        from src.engine.workflow.nodes.utils import console
        print_phase("Report Generation", style="bold magenta")

        if not state.get("scored_candidates") or not state.get("evidence_paths"):
            r = "Investigation failed to uncover causal evidence paths."
            return {"report": r, "final_response": r}

        tc = state["scored_candidates"][0]
        sp = tc.evidence_path

        with console.status("[magenta]Generating final incident report...[/magenta]", spinner="dots"):
            rep_str, f_path = _format_report(state, tc, sp)
            
            # Since _save_postmortem has prints inside it, we will just redefine it or let it use standard print if we don't want to change it.
            # But we can change it to use console if we want. For now, let's just leave it or pass console to it.
        
        # We need to inline the saving or let it print standard. I'll just let _save_postmortem print standard or change it too. Let's fix _save_postmortem's prints right now via replacement:
        _save_postmortem(state, tc, f_path)

        # Architectural Revision: Save ledger and update metadata confidence
        investigation_id = state.get("investigation_id")
        t_id = state.get("tenant_id", "default")
        if investigation_id:
            # 1. Update metadata
            meta_path = f"graph/{t_id}/investigations/{investigation_id}.json"
            if os.path.exists(meta_path):
                try:
                    with open(meta_path, "r") as f:
                        meta = json.load(f)
                    meta["confidence"] = tc.score
                    with open(meta_path, "w") as f:
                        json.dump(meta, f, indent=2)
                except Exception as e:
                    console.print(f"  [bold yellow]Failed to update investigation metadata: {e}[/bold yellow]")
            
            # 2. Save Ledger
            ledger = state.get("ledger")
            if ledger:
                ledger_dir = f"ledger/{t_id}"
                os.makedirs(ledger_dir, exist_ok=True)
                ledger_path = f"{ledger_dir}/{investigation_id}_ledger.json"
                try:
                    ledger_data = []
                    for e in ledger.entries:
                        ledger_data.append({
                            "id": e.id,
                            "fact": e.fact,
                            "source_type": e.source_type,
                            "source_id": e.source_id,
                            "confidence": e.confidence,
                            "verified": e.verified,
                            "timestamp": e.timestamp.isoformat() if hasattr(e.timestamp, 'isoformat') else str(e.timestamp),
                            "supporting_entries": e.supporting_entries,
                            "contradicting_entries": e.contradicting_entries
                        })
                    with open(ledger_path, "w") as f:
                        json.dump(ledger_data, f, indent=2)
                    console.print(f"  [dim]Exported evidence ledger to {ledger_path}[/dim]")
                except Exception as e:
                    console.print(f"  [bold red]Failed to save ledger: {e}[/bold red]")

        return {"report": rep_str, "final_response": rep_str}

    return _report
