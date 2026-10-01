from datetime import datetime
from typing import Literal, Optional
from ..shared.actors import EventBase, SystemActorContext
from ..application.snapshots import ApplicationSnapshot, ServiceSnapshot, EnvironmentSnapshot
from .snapshots import OnCallIdentitySnapshot


class OnCallChanged(EventBase):
    """oncall.changed — the effective on-call identity for a scope (service, or an
    application+environment) has changed. Fired uniformly regardless of cause (shift
    handoff, override start/end, rotation enabled/disabled); `actorContext.reason`
    carries the cause for diagnostics only, consumers should not branch on it.

    Exactly one of (application+environment) / service-only is set: `application` and
    `environment` are present for an app+env scope, absent for a service scope.
    `inherited` is only meaningful for an app+env scope (whether the value comes from
    the service-level rotation rather than the app+env's own)."""

    actorType: Literal["system"]
    actorContext: SystemActorContext
    changedAt: datetime
    service: ServiceSnapshot
    application: Optional[ApplicationSnapshot] = None
    environment: Optional[EnvironmentSnapshot] = None
    inherited: Optional[bool] = None
    previousOnCall: Optional[OnCallIdentitySnapshot] = None
    newOnCall: Optional[OnCallIdentitySnapshot] = None
