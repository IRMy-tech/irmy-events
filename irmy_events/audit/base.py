from datetime import datetime
from typing import Literal, Union
from ..shared.actors import (
    UserActorContext,
    ServiceAccountActorContext,
    SystemActorContext,
    IdpActorContext,
    EventBase,
)

AuditActorContext = Union[
    UserActorContext,
    ServiceAccountActorContext,
    SystemActorContext,
    IdpActorContext,
]


class AuditEventBase(EventBase):
    """Base for all audit events.

    Audit events describe configuration-entity changes (who, when, how).
    The model_validator from EventBase discriminates actorContext automatically.
    Context envelopes (service, application, environment) are defined per
    concrete subclass since their presence depends on the entity's scope.
    """

    actorType: Literal["user", "serviceAccount", "system", "idp"]
    actorContext: AuditActorContext
    entity: str
    action: str
    occurredAt: datetime
