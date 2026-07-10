from typing import Any, Dict

from src.core.entities import Capability
from src.infra.providers.base import CapabilityProvider

class MCPProvider(CapabilityProvider):
    """
    Base class for MCP-based providers interacting with live systems.
    Currently transport-agnostic, can be upgraded to JSON-RPC MCP later.
    """
    pass

class GitHubProvider(MCPProvider):
    @property
    def name(self) -> str:
        return "github"

    def execute(self, capability: Capability) -> Dict[str, Any]:
        return {"source": "github", "data": "Mock GitHub Data for " + capability.name}

class GrafanaProvider(MCPProvider):
    @property
    def name(self) -> str:
        return "grafana"

    def execute(self, capability: Capability) -> Dict[str, Any]:
        return {"source": "grafana", "data": "Mock Grafana Metrics for " + capability.name}

class JiraProvider(MCPProvider):
    @property
    def name(self) -> str:
        return "jira"

    def execute(self, capability: Capability) -> Dict[str, Any]:
        return {"source": "jira", "data": "Mock Jira Tickets for " + capability.name}
