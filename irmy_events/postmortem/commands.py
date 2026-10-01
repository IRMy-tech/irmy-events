from typing import Literal
from ..shared.actors import EventBase, PluginActorContext


class PostmortemCommandCreateDraft(EventBase):
    """postmortem.command.createDraft — plugin creates a postmortem draft."""

    actorType: Literal["plugin"]
    actorContext: PluginActorContext
    incidentId: str
    summary: str
    rootCause: str
    transitionToReview: bool = False


class PostmortemCommandChangeState(EventBase):
    """postmortem.command.changeState — plugin transitions postmortem state.
    Plugins may only transition to draft or inReview."""

    actorType: Literal["plugin"]
    actorContext: PluginActorContext
    incidentId: str
    newState: Literal["draft", "inReview"]
