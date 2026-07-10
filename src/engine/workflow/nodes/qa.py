from src.core.llm import AgentMessage, llmProvider
from src.data.graph import GraphService
from src.engine.workflow.nodes.utils import print_phase
from src.engine.workflow.state import InvestigationState
from src.config.prompt import QA_AGENT_PROMPT

def get_qa_node(llm: llmProvider, graph_svc: GraphService):
    def _qa_generation(state: InvestigationState):
        from src.engine.workflow.nodes.utils import console
        print_phase("General QA Generation", style="bold magenta")

        context_parts = []
        for a_id in state.get("expanded_artifacts", []):
            node_data = graph_svc.get_node(a_id)
            if node_data:
                obj = node_data.get("obj")
                if obj and hasattr(obj, "model_dump"):
                    context_parts.append(str(obj.model_dump()))
                else:
                    context_parts.append(str(node_data))

        context_str = "\n---\n".join(context_parts[:20])

        prompt = QA_AGENT_PROMPT.format(query=state['query'], context_str=context_str)

        with console.status("[magenta]Generating answer...[/magenta]", spinner="dots"):
            msg = llm.generate([AgentMessage(role="system", content=prompt)])
            
        console.print(f"  [green]{msg.content}[/green]")

        report = f"Issue: {state['query']}\n\nAnswer:\n{msg.content}"
        return {
            "technical_explanation": msg.content,
            "report": report,
            "final_response": report,
        }

    return _qa_generation
