from src.core.llm import AgentMessage, llmProvider
from src.engine.workflow.nodes.utils import print_phase
from src.engine.workflow.state import InvestigationState
from src.config.prompt import UNDERSTAND_PROMPT

def get_understand_node(llm: llmProvider):
    def _understand(state: InvestigationState):
        print_phase("Query Understanding")
        prompt = UNDERSTAND_PROMPT.format(query=state['query'])
        msg = llm.generate([AgentMessage(role="system", content=prompt)])

        intent = "INVESTIGATION"
        if "[GENERAL_QA]" in msg.content:
            intent = "GENERAL_QA"

        print(f"  \033[93mIntent: {intent}\033[0m")
        print(f"  \033[90m{msg.content}\033[0m")
        return {"intent": intent, "understanding": msg.content}

    return _understand
