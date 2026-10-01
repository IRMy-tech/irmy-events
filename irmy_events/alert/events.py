from datetime import datetime
from typing import Literal
from pydantic import BaseModel
from ..shared.actors import EventBase, SystemActorContext, ActorContext
from ..application.snapshots import ApplicationSnapshot, ServiceSnapshot, EnvironmentSnapshot
from .snapshots import (
    AlertOpenSnapshot,
    AlertCloseSnapshot,
    AlertAckSnapshot,
    AlertUpdateSnapshot,
    AlertAssigneeSnapshot,
    AlertNoteSnapshot,
)


class AlertStateOpen(EventBase):
    """alert.state.open — new alert created and persisted (not dropped by silence rules)."""

    actorType: Literal["user", "serviceAccount", "plugin", "system"]
    actorContext: ActorContext
    alert: AlertOpenSnapshot
    application: ApplicationSnapshot
    service: ServiceSnapshot
    environment: EnvironmentSnapshot


class AlertStateClose(EventBase):
    """alert.state.close — alert (and its full deduplication chain) closed."""

    actorType: Literal["user", "serviceAccount", "plugin", "system"]
    actorContext: ActorContext
    alert: AlertCloseSnapshot
    application: ApplicationSnapshot
    service: ServiceSnapshot
    environment: EnvironmentSnapshot


class AlertStateAcknowledge(EventBase):
    """alert.state.acknowledge — alert acknowledged; pending escalation cancelled."""

    actorType: Literal["user", "serviceAccount", "plugin", "system"]
    actorContext: ActorContext
    alert: AlertAckSnapshot
    application: ApplicationSnapshot
    service: ServiceSnapshot
    environment: EnvironmentSnapshot


class AlertActionUpdate(EventBase):
    """alert.action.update — alert updated (connection_management pipeline, or a user/serviceAccount/plugin via API)."""

    actorType: Literal["user", "serviceAccount", "plugin", "system"]
    actorContext: ActorContext
    alert: AlertUpdateSnapshot
    application: ApplicationSnapshot
    service: ServiceSnapshot
    environment: EnvironmentSnapshot


class AlertAssigneeModify(EventBase):
    """alert.assignee.modify — alert reassigned to a different user."""

    actorType: Literal["user", "serviceAccount", "plugin", "system"]
    actorContext: ActorContext
    alert: AlertAssigneeSnapshot
    application: ApplicationSnapshot
    service: ServiceSnapshot
    environment: EnvironmentSnapshot


class NoteRecord(BaseModel):
    id: str
    content: str
    createdAt: datetime


class AlertNoteAdd(EventBase):
    """alert.note.add — note added to an alert.
    The note author is the event actor (actorContext); no separate author field."""

    actorType: Literal["user", "serviceAccount", "plugin"]
    actorContext: ActorContext
    alert: AlertNoteSnapshot
    note: NoteRecord
    application: ApplicationSnapshot
    service: ServiceSnapshot
    environment: EnvironmentSnapshot
