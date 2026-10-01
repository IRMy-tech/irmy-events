from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel


class SecurityPrincipal(BaseModel):
    """Who was authenticated, who attempted to authenticate, or who performed
    a credential operation.

    Unlike audit's actorContext, this is a single flat shape reused across
    every principal type -- nullability of the identifying fields depends on
    whether the platform could resolve/match the principal, not on `type`
    alone (e.g. a failed password login with an unknown email still carries
    `type: "user"` and the attempted `email`, with `id` left null).
    """

    type: Literal["user", "serviceAccount", "system"]
    method: Optional[Literal["password", "saml", "oidc", "serviceAccountSecret"]] = None
    id: Optional[str] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    email: Optional[str] = None
    name: Optional[str] = None


class SecurityRequestContext(BaseModel):
    """Network-level metadata about the request that produced the event.

    `ipAddress` is always present; `userAgent` is opportunistic since not
    every client sends one.
    """

    ipAddress: str
    userAgent: Optional[str] = None


class SecurityEventBase(BaseModel):
    """Base for all security events.

    Security events describe authentication-related activity and credential
    operations -- who logged in/failed to log in, who changed or reset a
    password, who rotated a service account secret. Unlike audit events they
    have no `before`/`after`: each event is a discrete fact, not a state
    change of an entity. `eventData` is typed per concrete subclass since its
    shape is event-specific.
    """

    event: str
    principal: SecurityPrincipal
    requestContext: SecurityRequestContext
    failureReason: Optional[str] = None
    occurredAt: datetime
