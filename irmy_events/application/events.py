from datetime import datetime
from typing import Literal
from ..shared.actors import EventBase, SystemActorContext
from .snapshots import ApplicationSnapshot, ServiceSnapshot, EnvironmentSnapshot
from ..alert.snapshots import AlertOpenSnapshot, AlertCloseSnapshot, AlertUpdateSnapshot


class ApplicationStateAlerted(EventBase):
    """application.state.alerted — app+env transitions from noAlert to inAlert.
    Fired after the first unresolved alert for this app+env is opened."""

    actorType: Literal["system"]
    actorContext: SystemActorContext
    changedAt: datetime
    causedByAlert: AlertOpenSnapshot
    application: ApplicationSnapshot
    service: ServiceSnapshot
    environment: EnvironmentSnapshot


class ApplicationStateRecovered(EventBase):
    """application.state.recovered — app+env transitions from inAlert to noAlert.
    Fired after the last unresolved alert for this app+env is closed."""

    actorType: Literal["system"]
    actorContext: SystemActorContext
    changedAt: datetime
    causedByAlert: AlertCloseSnapshot
    application: ApplicationSnapshot
    service: ServiceSnapshot
    environment: EnvironmentSnapshot


class ApplicationStateAlertLevelIncreased(EventBase):
    """application.state.alertLevelIncreased — app+env remains inAlert but its
    highest unresolved priority rises (lower number = higher priority), either because a
    higher-priority alert was opened or because an update raised an open alert's severity.

    causedByAlert stays an AlertOpenSnapshot in both cases: incident_management feeds it
    straight into IncidentRuleTrigger / incident.created, which are typed to that snapshot."""

    actorType: Literal["system"]
    actorContext: SystemActorContext
    changedAt: datetime
    previousAlertLevel: int
    newAlertLevel: int
    causedByAlert: AlertOpenSnapshot
    application: ApplicationSnapshot
    service: ServiceSnapshot
    environment: EnvironmentSnapshot


class ApplicationStateAlertLevelDecreased(EventBase):
    """application.state.alertLevelDecreased — app+env remains inAlert but its
    highest unresolved priority drops, either because the top-priority alert was
    closed (AlertCloseSnapshot) or because an update lowered its severity
    (AlertUpdateSnapshot — the alert is still open, so it has no closedAt/closeReason)."""

    actorType: Literal["system"]
    actorContext: SystemActorContext
    changedAt: datetime
    previousAlertLevel: int
    newAlertLevel: int
    causedByAlert: AlertCloseSnapshot | AlertUpdateSnapshot
    application: ApplicationSnapshot
    service: ServiceSnapshot
    environment: EnvironmentSnapshot
