from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel
from ..shared.refs import UserRef


class AlertCoreFields(BaseModel):
    """Fields present in every alert state snapshot."""

    id: str
    externalAlertId: str
    subject: Optional[str] = None
    description: Optional[str] = None
    labels: list[str]
    priority: int
    customFields: dict[str, Any]
    createdAt: datetime


class AlertOpenSnapshot(AlertCoreFields):
    """Used in alert.state.open, application.state.alerted,
    application.state.alertLevelIncreased, and incident.created causedByAlert."""

    shouldNotify: bool
    assignedToUser: Optional[UserRef] = None


class AlertCloseSnapshot(AlertCoreFields):
    """Used in alert.state.close, application.state.recovered,
    and application.state.alertLevelDecreased."""

    closedAt: datetime
    closeReason: str
    shouldNotify: bool
    assignedToUser: Optional[UserRef] = None


class AlertAckSnapshot(AlertCoreFields):
    """Used in alert.state.acknowledge."""

    acknowledgedAt: datetime
    shouldNotify: bool
    assignedToUser: Optional[UserRef] = None


class AlertUpdateSnapshot(AlertCoreFields):
    """Used in alert.action.update, and in application.state.alertLevelDecreased when an
    update lowered an open alert's severity (the alert is not closed, so it has no
    closedAt/closeReason and cannot be an AlertCloseSnapshot)."""

    updatedAt: datetime
    shouldNotify: bool
    assignedToUser: Optional[UserRef] = None


class AlertAssigneeSnapshot(AlertCoreFields):
    """Used in alert.assignee.modify.
    Replaces assignedToUser with previousAssignee / newAssignee."""

    assignedAt: datetime
    shouldNotify: bool
    previousAssignee: Optional[UserRef] = None
    newAssignee: UserRef


class AlertNoteSnapshot(AlertCoreFields):
    """Used in alert.note.add."""

    shouldNotify: bool
    assignedToUser: Optional[UserRef] = None


class AlertCommandInput(BaseModel):
    """Alert payload sent inside alert.command.create (incoming command)."""

    externalAlertId: str
    subject: Optional[str] = None
    description: Optional[str] = None
    labels: list[str] = []
    priority: int
    customFields: dict[str, Any] = {}
    applicationId: str
    environmentId: str
