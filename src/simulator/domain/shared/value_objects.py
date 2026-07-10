from typing import NewType
from uuid import UUID
from datetime import datetime

# Identifiers
TenantID = NewType("TenantID", str)
EventID = NewType("EventID", UUID)
CorrelationID = NewType("CorrelationID", str)
DecisionID = NewType("DecisionID", UUID)
ActorID = NewType("ActorID", str)
IncidentID = NewType("IncidentID", str)
TeamID = NewType("TeamID", str)
EngineerID = NewType("EngineerID", str)
ServiceID = NewType("ServiceID", str)
RepositoryID = NewType("RepositoryID", str)
InfrastructureID = NewType("InfrastructureID", str)

# Time
Timestamp = NewType("Timestamp", datetime)
