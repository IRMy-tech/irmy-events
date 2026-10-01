from typing import Literal
from ..shared.actors import EventBase, SystemActorContext


class OncallCommandExtend(EventBase):
    """oncall.command.extend — published by scheduler to extend rotation shifts."""

    actorType: Literal["system"]
    actorContext: SystemActorContext
    oncallId: str
    days: int


class OncallCommandCheck(EventBase):
    """oncall.command.check — self-scheduled by application_management (via scheduler)
    to fire shortly after the next known shift/override boundary for a rotation, so it
    can recompute the effective on-call identity and publish oncall.changed if it moved."""

    actorType: Literal["system"]
    actorContext: SystemActorContext
    rotationId: str
    isService: bool
