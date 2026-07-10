from abc import ABC, abstractmethod
from typing import Any
from pydantic import BaseModel, ConfigDict
from src.simulator.domain.decision.models import Context, Decision
from src.simulator.domain.shared.value_objects import ActorID

class Actor(BaseModel, ABC):
    """
    Base class for any entity capable of making decisions.
    """
    model_config = ConfigDict(frozen=True)
    
    id: ActorID
    name: str

    @abstractmethod
    def evaluate(self, context: Context) -> Decision:
        """
        Evaluate the context and produce a decision.
        """
        pass

class HumanActor(Actor):
    """
    An engineer, manager, or other human making decisions.
    Incorporates human factors like fatigue, context switches, or tribal knowledge.
    """
    model_config = ConfigDict(frozen=True)
    
    fatigue_level: float = 0.0  # 0.0 = rested, 1.0 = exhausted
    
    def evaluate(self, context: Context) -> Decision:
        # Implementation will depend on specific human behavior strategies
        raise NotImplementedError()

class SystemActor(Actor):
    """
    An automated system making decisions, e.g., an autoscaler, CI pipeline, or rollout controller.
    """
    model_config = ConfigDict(frozen=True)
    
    thresholds: dict[str, Any] = {}
    
    def evaluate(self, context: Context) -> Decision:
        # Implementation will depend on specific controller logic
        raise NotImplementedError()
