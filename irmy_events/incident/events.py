from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel
from ..shared.actors import EventBase, ActorContext
from ..shared.refs import UserRef
from ..application.snapshots import ApplicationSnapshot, ServiceSnapshot, EnvironmentSnapshot
from ..alert.snapshots import AlertOpenSnapshot
from .snapshots import IncidentSnapshot, ActionItemSnapshot


class IncidentCreated(EventBase):
    """incident.created — new incident created.
    causedByAlert is non-null only when actorType=rule."""

    actorType: Literal["user", "serviceAccount", "plugin", "rule"]
    actorContext: ActorContext
    incident: IncidentSnapshot
    causedByAlert: Optional[AlertOpenSnapshot] = None
    application: ApplicationSnapshot
    service: ServiceSnapshot
    environment: EnvironmentSnapshot


class IncidentUpdated(EventBase):
    """incident.updated — incident title or description changed.
    At least one of previousTitle / previousDescription is non-null."""

    actorType: Literal["user", "serviceAccount", "plugin"]
    actorContext: ActorContext
    incident: IncidentSnapshot
    previousTitle: Optional[str] = None
    previousDescription: Optional[str] = None
    updatedAt: datetime
    application: ApplicationSnapshot
    service: ServiceSnapshot
    environment: EnvironmentSnapshot


class _IncidentStateTransition(EventBase):
    incident: IncidentSnapshot
    previousState: str
    newState: str
    stateChangedAt: datetime
    application: ApplicationSnapshot
    service: ServiceSnapshot
    environment: EnvironmentSnapshot


class IncidentStateAcknowledged(_IncidentStateTransition):
    """incident.state.acknowledged"""

    actorType: Literal["user", "serviceAccount", "plugin"]
    actorContext: ActorContext
    previousState: Literal["open"]
    newState: Literal["acknowledged"]


class IncidentStateInvestigating(_IncidentStateTransition):
    """incident.state.investigating"""

    actorType: Literal["user", "serviceAccount", "plugin"]
    actorContext: ActorContext
    previousState: Literal["open", "acknowledged"]
    newState: Literal["investigating"]


class IncidentStateConfirmed(_IncidentStateTransition):
    """incident.state.confirmed — incident confirmed as real (not a false positive/duplicate)."""

    actorType: Literal["user", "serviceAccount", "plugin"]
    actorContext: ActorContext
    previousState: Literal["investigating"]
    newState: Literal["confirmed"]


class IncidentStateResolved(_IncidentStateTransition):
    """incident.state.resolved — plugins cannot transition to resolved."""

    actorType: Literal["user", "serviceAccount"]
    actorContext: ActorContext
    previousState: Literal["confirmed"]
    newState: Literal["resolved"]


class IncidentStateClosed(_IncidentStateTransition):
    """incident.state.closed — manual fast-close or automatic close after postmortem."""

    actorType: Literal["user", "serviceAccount", "system"]
    actorContext: ActorContext
    previousState: Literal["investigating", "confirmed", "resolved"]
    newState: Literal["closed"]
    closeReason: str


class IncidentStateReopened(_IncidentStateTransition):
    """incident.state.reopened — resolved incident moved back to confirmed."""

    actorType: Literal["user", "serviceAccount", "plugin"]
    actorContext: ActorContext
    previousState: Literal["resolved"]
    newState: Literal["confirmed"]


class _IncidentSeverityChange(EventBase):
    incident: IncidentSnapshot
    previousSeverity: Literal["critical", "high", "medium", "low"]
    newSeverity: Literal["critical", "high", "medium", "low"]
    severityChangedAt: datetime
    application: ApplicationSnapshot
    service: ServiceSnapshot
    environment: EnvironmentSnapshot


class IncidentSeverityEscalated(_IncidentSeverityChange):
    """incident.severity.escalated — severity became more critical."""

    actorType: Literal["user", "serviceAccount", "plugin"]
    actorContext: ActorContext


class IncidentSeverityDeescalated(_IncidentSeverityChange):
    """incident.severity.deescalated — severity became less critical."""

    actorType: Literal["user", "serviceAccount", "plugin"]
    actorContext: ActorContext


class IncidentRoleAssigned(EventBase):
    """incident.roleAssigned — user assigned to an incident role.
    previousUser is null if the role had no assignee before."""

    actorType: Literal["user", "serviceAccount", "plugin"]
    actorContext: ActorContext
    incident: IncidentSnapshot
    roleLabel: str
    user: UserRef
    previousUser: Optional[UserRef] = None
    assignedAt: datetime
    application: ApplicationSnapshot
    service: ServiceSnapshot
    environment: EnvironmentSnapshot


class IncidentParticipantAdded(EventBase):
    """incident.participantAdded — user added as a participant."""

    actorType: Literal["user", "serviceAccount", "plugin"]
    actorContext: ActorContext
    incident: IncidentSnapshot
    user: UserRef
    addedAt: datetime
    application: ApplicationSnapshot
    service: ServiceSnapshot
    environment: EnvironmentSnapshot


class IncidentCommentRecord(BaseModel):
    id: str
    type: Literal["update", "note", "actionTaken"]
    content: str
    createdAt: datetime


class IncidentCommentAdded(EventBase):
    """incident.commentAdded — typed comment added to the incident timeline.
    The comment author is the event actor (actorContext)."""

    actorType: Literal["user", "serviceAccount", "plugin"]
    actorContext: ActorContext
    incident: IncidentSnapshot
    note: IncidentCommentRecord
    application: ApplicationSnapshot
    service: ServiceSnapshot
    environment: EnvironmentSnapshot


class IncidentActionItemCreated(EventBase):
    """incident.actionItemCreated — action item created on an incident."""

    actorType: Literal["user", "serviceAccount", "plugin"]
    actorContext: ActorContext
    incident: IncidentSnapshot
    actionItem: ActionItemSnapshot
    application: ApplicationSnapshot
    service: ServiceSnapshot
    environment: EnvironmentSnapshot


class IncidentActionItemDone(EventBase):
    """incident.actionItemDone — action item marked as done."""

    actorType: Literal["user", "serviceAccount", "plugin"]
    actorContext: ActorContext
    incident: IncidentSnapshot
    actionItem: ActionItemSnapshot
    application: ApplicationSnapshot
    service: ServiceSnapshot
    environment: EnvironmentSnapshot


class IncidentActionItemUpdated(EventBase):
    """incident.actionItemUpdated — action item edited (summary, description,
    assignee, and/or due date). `actionItem` reflects the state after the
    update. `previousSummary`/`previousDescription`/`previousAssignedTo`/
    `previousDueDate` are populated only for the field(s) this update actually
    touched (set or cleared) — same convention as `IncidentUpdated.previousTitle`
    / `previousDescription`."""

    actorType: Literal["user", "serviceAccount", "plugin"]
    actorContext: ActorContext
    incident: IncidentSnapshot
    actionItem: ActionItemSnapshot
    previousSummary: Optional[str] = None
    previousDescription: Optional[str] = None
    previousAssignedTo: Optional[UserRef] = None
    previousDueDate: Optional[datetime] = None
    updatedAt: datetime
    application: ApplicationSnapshot
    service: ServiceSnapshot
    environment: EnvironmentSnapshot
