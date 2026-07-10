from typing import Optional, Any
from uuid import uuid4
from datetime import datetime, timezone
from src.simulator.domain.actor.models import HumanActor
from src.simulator.domain.decision.models import Decision, Context, Action
from src.simulator.domain.shared.value_objects import DecisionID, ActorID

class PullRequestReviewContext(Context):
    """
    Context specifically for PR Review decisions.
    """
    context_type: str = "pull_request_review"
    pr_id: str
    author_id: ActorID
    files_changed: int
    lines_changed: int
    complexity_score: float

class SoftwareEngineerActor(HumanActor):
    """
    A HumanActor that behaves like a software engineer.
    It uses its internal state (e.g., fatigue) and the context to make decisions.
    """
    strictness: float = 0.5  # 0.0 = accepts anything, 1.0 = extremely rigorous
    
    def evaluate(self, context: Context) -> Decision:
        if isinstance(context, PullRequestReviewContext):
            return self._decide_on_pr_review(context)
            
        # Default behavior for unknown contexts
        return Decision(
            id=DecisionID(uuid4()),
            timestamp=datetime.now(timezone.utc),
            actor_id=self.id,
            context=context,
            action=Action(action_type="IGNORE", payload={}),
            rationale="Context not recognized by SoftwareEngineerActor"
        )
        
    def _decide_on_pr_review(self, context: PullRequestReviewContext) -> Decision:
        # Simple heuristic: if fatigued or lines changed is huge, higher chance to just "LGTM" without looking closely
        # Or if strictly rigorous, they might request changes.
        
        cognitive_load = context.lines_changed * context.complexity_score
        
        # If the PR is massive and the engineer is tired, they might just rubber-stamp it
        # (This is an example of human behavioral simulation)
        rubber_stamp_threshold = 1000 * (1.0 - self.fatigue_level)
        
        if cognitive_load > rubber_stamp_threshold:
            rationale = "PR is too large and I am fatigued. Rubber-stamping."
            action_type = "PR_APPROVE"
        elif self.strictness > 0.8 and context.complexity_score > 1.5:
            rationale = "PR is complex and I am strict. Requesting changes."
            action_type = "PR_REQUEST_CHANGES"
        else:
            rationale = "Looks good to me."
            action_type = "PR_APPROVE"
            
        return Decision(
            id=DecisionID(uuid4()),
            timestamp=datetime.now(timezone.utc),
            actor_id=self.id,
            context=context,
            action=Action(action_type=action_type, payload={"pr_id": context.pr_id}),
            rationale=rationale
        )
