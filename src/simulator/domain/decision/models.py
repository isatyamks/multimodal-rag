from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field
from src.simulator.domain.shared.value_objects import (
    ActorID,
    DecisionID,
    Timestamp,
)

class Context(BaseModel):
    """
    The information available to an actor at the time they make a decision.
    """
    model_config = ConfigDict(frozen=True)
    
    # Examples: pending PR details, current CPU load, active alerts
    context_type: str
    data: Dict[str, Any]

class Action(BaseModel):
    """
    The concrete execution intent stemming from a decision.
    This will be passed to the World Aggregate to mutate state.
    """
    model_config = ConfigDict(frozen=True)
    
    action_type: str
    payload: Dict[str, Any]

class Decision(BaseModel):
    """
    The atomic unit of the simulation. Maps a context to an action via an actor's rationale.
    """
    model_config = ConfigDict(frozen=True)
    
    id: DecisionID
    timestamp: Timestamp
    actor_id: ActorID
    context: Context
    action: Action
    rationale: str = "No rationale provided"
