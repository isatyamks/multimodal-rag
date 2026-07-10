from typing import List, Optional, Dict
from pydantic import BaseModel, ConfigDict, Field
from src.simulator.domain.shared.value_objects import (
    EngineerID,
    InfrastructureID,
    RepositoryID,
    ServiceID,
    TeamID,
    TenantID,
)
from src.simulator.domain.decision.models import Action
from src.simulator.domain.events.base import DomainEvent

class Engineer(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    id: EngineerID
    name: str
    email: str
    roles: List[str] = Field(default_factory=list)
    is_on_call: bool = False

class Repository(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    id: RepositoryID
    name: str
    url: str
    language: str

class Microservice(BaseModel):
    """
    Represents a running service with its health state and dependencies.
    """
    model_config = ConfigDict(frozen=True)
    
    id: ServiceID
    name: str
    repository_id: RepositoryID
    dependencies: List[ServiceID] = Field(default_factory=list)
    health_score: float = 1.0  # 1.0 is perfectly healthy, 0.0 is dead

class Team(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    id: TeamID
    name: str
    engineers: List[Engineer] = Field(default_factory=list)
    owned_services: List[ServiceID] = Field(default_factory=list)

class Organization(BaseModel):
    """
    Represents the entire tenant organization structure.
    """
    model_config = ConfigDict(frozen=True)
    
    tenant_id: TenantID
    name: str
    domain: str
    teams: List[Team] = Field(default_factory=list)

class Infrastructure(BaseModel):
    """
    Base resources like Kubernetes clusters or databases.
    """
    model_config = ConfigDict(frozen=True)
    
    id: InfrastructureID
    type: str
    name: str
    status: str = "running"
    
class WorldState(BaseModel):
    """
    The aggregate root holding the entire canonical state of the simulation.
    """
    model_config = ConfigDict(frozen=False)  # World state is mutable during simulation
    
    organization: Organization
    services: Dict[ServiceID, Microservice] = Field(default_factory=dict)
    infrastructure: Dict[InfrastructureID, Infrastructure] = Field(default_factory=dict)
    
    def apply_action(self, action: Action) -> List[DomainEvent]:
        """
        Executes an action, mutating the world state and returning the resulting domain events.
        """
        events: List[DomainEvent] = []
        from datetime import datetime, timezone
        import uuid
        
        # Example pattern: Route action to specific handler based on action_type
        if action.action_type in ("PR_APPROVE", "PR_REQUEST_CHANGES", "IGNORE"):
            # Mock generating an event
            events.append(DomainEvent(
                event_id=uuid.uuid4(),
                timestamp=datetime.now(timezone.utc),
                tenant_id=self.organization.tenant_id,
                correlation_id="corr-mock",
            ))
        
        return events
