import json
from typing import Union, List, Dict
from src.core.llm import AgentMessage, llmProvider
from src.config.prompt import TRIAGE_AGENT_PROMPT
from src.engine.triage.models import InvestigationRequest

class TriageAgent:
    """
    Triage Agent that clarifies the user's intent and scope.
    Stateless and UI-agnostic.
    """
    def __init__(self, llm: llmProvider):
        self.llm = llm

    def refine_query(self, messages: List[AgentMessage], initial_query: str) -> Union[InvestigationRequest, str]:
        """
        Takes the current conversation history.
        Returns an InvestigationRequest if triage is complete,
        or a string response if further clarification is needed.
        """
        response_text = self.llm.generate(messages).content
            
        clean_text = response_text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:-3].strip()
        elif clean_text.startswith("```"):
            clean_text = clean_text[3:-3].strip()
            
        try:
            parsed = json.loads(clean_text)
            if parsed.get("status") == "ready":
                final_query = parsed.get("final_query", initial_query)
                
                # Convert AgentMessages to dicts for the InvestigationRequest
                conv = [{"role": m.role, "content": m.content} for m in messages]
                
                return InvestigationRequest(
                    original_query=initial_query,
                    refined_query=final_query,
                    conversation=conv
                )
        except json.JSONDecodeError:
            pass
            
        return response_text
