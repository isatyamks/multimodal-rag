from typing import List, Dict
from pydantic import BaseModel, ConfigDict
from src.core.llm import AgentMessage

class InvestigationRequest(BaseModel):
    """
    Represents a finalized request for an investigation,
    after triage and refinement are complete.
    """
    model_config = ConfigDict(frozen=True)
    
    original_query: str
    refined_query: str
    conversation: List[Dict[str, str]] # e.g. [{"role": "user", "content": "..."}]
