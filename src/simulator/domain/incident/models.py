from typing import List
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field
from src.simulator.domain.shared.value_objects import (
    EngineerID,
    IncidentID,
    ServiceID,
    Timestamp,
)

class IncidentState(str, Enum):
    DETECTED = "detected"
    INVESTIGATING = "investigating"
    MITIGATING = "mitigating"
    RESOLVED = "resolved"

class Incident(BaseModel):
    """
    An ongoing anomaly or outage within the World State.
    """
    model_config = ConfigDict(frozen=True)
    
    id: IncidentID
    title: str
    state: IncidentState = IncidentState.DETECTED
    started_at: Timestamp
    resolved_at: Timestamp | None = None
    affected_services: List[ServiceID] = Field(default_factory=list)
    responders: List[EngineerID] = Field(default_factory=list)
