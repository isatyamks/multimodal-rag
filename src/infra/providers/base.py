from abc import ABC, abstractmethod
from typing import Any, Dict

from src.core.entities import Capability


class CapabilityProvider(ABC):
    """
    Base abstraction for any system that can satisfy a Capability.
    This separates the 'what we need' from 'where we get it'.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def execute(self, capability: Capability) -> Dict[str, Any]:
        """
        Execute the capability and return raw context.
        """
        pass
