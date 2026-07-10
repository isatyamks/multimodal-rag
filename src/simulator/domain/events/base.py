from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field
from enum import Enum
from src.simulator.domain.shared.value_objects import (
    CorrelationID,
    DecisionID,
    EventID,
    IncidentID,
    TenantID,
    Timestamp,
)

class PlatformEnum(str, Enum):
    GITHUB = "github"
    SLACK = "slack"
    JIRA = "jira"
    PAGERDUTY = "pagerduty"
    METRICS = "metrics"
    LOGS = "logs"
    DEPLOYMENT = "deployment"
    KUBERNETES = "kubernetes"
    INTERNAL = "internal"

class EntityReference(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    type: str
    id: str

class DomainEvent(BaseModel):
    """
    Base event for state changes occurring purely within the World model.
    """
    model_config = ConfigDict(frozen=True)
    
    event_id: EventID
    timestamp: Timestamp
    tenant_id: TenantID
    correlation_id: CorrelationID
    decision_id: Optional[DecisionID] = None
    incident_id: Optional[IncidentID] = None
    
class BasePlatformEvent(BaseModel):
    """
    The canonical egress event contract for Codentir.
    Every platform adapter translates DomainEvents into these.
    """
    model_config = ConfigDict(frozen=True)
    
    schema_version: int = 1
    event_id: EventID
    tenant_id: TenantID
    simulation_id: str
    tick_number: int
    occurred_at: Timestamp
    event_type: str
    actor_id: str
    correlation_id: CorrelationID
    causation_id: Optional[EventID] = None
    payload: Dict[str, Any]
    metadata: Dict[str, Any] = Field(default_factory=dict)
