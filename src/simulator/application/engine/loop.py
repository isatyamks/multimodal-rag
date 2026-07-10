from typing import List
from datetime import datetime, timedelta
from src.simulator.domain.actor.models import Actor
from src.simulator.domain.decision.models import Context, Decision
from src.simulator.domain.world.models import WorldState
from src.simulator.application.interfaces.observer import PlatformObserver

class SimulationEngine:
    def __init__(
        self,
        world_state: WorldState,
        actors: List[Actor],
        observers: List[PlatformObserver],
        start_time: datetime,
        tick_duration: timedelta = timedelta(minutes=1)
    ):
        self.world_state = world_state
        self.actors = actors
        self.observers = observers
        self.current_time = start_time
        self.tick_duration = tick_duration
        
    def _gather_contexts(self) -> List[tuple[Actor, Context]]:
        from src.simulator.domain.actor.engineers import PullRequestReviewContext
        
        # Stub implementation: give the first actor a PR to review
        if not self.actors:
            return []
            
        actor = self.actors[0]
        context = PullRequestReviewContext(
            pr_id="pr-402",
            author_id="eng-999", # Someone else
            files_changed=12,
            lines_changed=450,
            complexity_score=1.8,
            data={}
        )
        return [(actor, context)]

    def tick(self) -> None:
        """
        Advances the simulation by one time step.
        """
        self.current_time += self.tick_duration
        
        # 1. Identify what needs deciding
        actor_contexts = self._gather_contexts()
        
        # 2. Gather decisions
        decisions: List[Decision] = []
        for actor, context in actor_contexts:
            decision = actor.evaluate(context)
            decisions.append(decision)
            
        # 3. Apply actions to the world state and observe events
        for decision in decisions:
            print(f"Actor {decision.actor_id} decided to {decision.action.action_type}. Rationale: {decision.rationale}")
            events = self.world_state.apply_action(decision.action)
            
            # 4. Notify observers (Adapters) so they can emit to Kafka
            for event in events:
                for observer in self.observers:
                    observer.on_domain_event(event, decision)
