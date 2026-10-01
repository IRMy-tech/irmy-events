from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, TypeAdapter, field_validator
from ..shared.actors import EventBase, PluginActorContext

_DATETIME = TypeAdapter(datetime)


class IncidentCreateInput(BaseModel):
    applicationId: str
    environmentId: str
    title: str
    description: str
    severity: Literal["critical", "high", "medium", "low"]
    incidentRoles: dict[str, str] = {}
    participants: list[str] = []


class IncidentCommandCreate(EventBase):
    """incident.command.create — plugin requests creation of a new incident."""

    actorType: Literal["plugin"]
    actorContext: PluginActorContext
    incident: IncidentCreateInput


class IncidentCommandUpdate(EventBase):
    """incident.command.update — plugin updates incident title and/or description."""

    actorType: Literal["plugin"]
    actorContext: PluginActorContext
    incidentId: str
    title: Optional[str] = None
    description: Optional[str] = None


class IncidentCommandChangeSeverity(EventBase):
    """incident.command.changeSeverity — plugin changes incident severity."""

    actorType: Literal["plugin"]
    actorContext: PluginActorContext
    incidentId: str
    newSeverity: Literal["critical", "high", "medium", "low"]


class IncidentCommandChangeState(EventBase):
    """incident.command.changeState — plugin transitions incident state.
    Plugins may only transition to acknowledged, investigating, or confirmed."""

    actorType: Literal["plugin"]
    actorContext: PluginActorContext
    incidentId: str
    newState: Literal["acknowledged", "investigating", "confirmed"]


class IncidentCommandAssignRole(EventBase):
    """incident.command.assignRole — plugin assigns a user to an incident role."""

    actorType: Literal["plugin"]
    actorContext: PluginActorContext
    incidentId: str
    roleLabel: str
    userId: str


class IncidentCommandAddParticipant(EventBase):
    """incident.command.addParticipant — plugin adds a participant to an incident."""

    actorType: Literal["plugin"]
    actorContext: PluginActorContext
    incidentId: str
    userId: str


class IncidentNoteInput(BaseModel):
    type: Literal["update", "note", "actionTaken"]
    content: str


class IncidentCommandAddComment(EventBase):
    """incident.command.addComment — plugin adds a typed comment to the timeline."""

    actorType: Literal["plugin"]
    actorContext: PluginActorContext
    incidentId: str
    note: IncidentNoteInput


class ActionItemInput(BaseModel):
    summary: str
    description: Optional[str] = None
    assignedTo: Optional[str] = None
    dueDate: Optional[datetime] = None


class IncidentCommandAddActionItem(EventBase):
    """incident.command.addActionItem — plugin adds an action item to an incident."""

    actorType: Literal["plugin"]
    actorContext: PluginActorContext
    incidentId: str
    actionItem: ActionItemInput


class IncidentCommandCompleteActionItem(EventBase):
    """incident.command.completeActionItem — plugin marks an action item as done."""

    actorType: Literal["plugin"]
    actorContext: PluginActorContext
    incidentId: str
    actionItemId: str


class IncidentCommandUpdateActionItem(EventBase):
    """incident.command.updateActionItem — plugin edits an action item's
    summary, description, assignee, and/or due date.

    `description`/`assignedTo`/`dueDate` use tri-state semantics on the wire:
    absent or `null` = leave unchanged, `""` = clear the field, any other value
    = set it. `summary` cannot be cleared (it's required on the entity), so it
    is plain optional: absent/`null` = unchanged, any value = set it.
    The service rejects the command if every field ends up unchanged."""

    actorType: Literal["plugin"]
    actorContext: PluginActorContext
    incidentId: str
    actionItemId: str
    summary: Optional[str] = None
    description: Optional[str] = None
    assignedTo: Optional[str] = None
    dueDate: Optional[str] = None

    @field_validator("dueDate")
    @classmethod
    def _validate_due_date(cls, value: Optional[str]) -> Optional[str]:
        # Stays a string on the wire ("" means "clear"), but a set value must be a
        # parseable ISO-8601 datetime so the consumer never receives garbage.
        if value:
            try:
                _DATETIME.validate_python(value)
            except ValueError:
                raise ValueError(f"dueDate must be an ISO-8601 datetime or \"\" to clear, got {value!r}")
        return value
