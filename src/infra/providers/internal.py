from typing import Any, Dict

from src.core.entities import Capability
from src.infra.providers.base import CapabilityProvider

class InternalProvider(CapabilityProvider):
    """
    Base class for internal capabilities like historical BM25, Vector, or Knowledge Graph search.
    """
    pass
