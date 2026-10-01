from typing import Any, Literal, Optional, Union
from pydantic import BaseModel
from ..shared.actors import EventBase, PluginActorContext, SystemActorContext
from .snapshots import AlertCommandInput


class NoteInput(BaseModel):
    content: str


class ParsedAlertData(BaseModel):
    """Parsed alert payload inside alert.request.process."""

    externalAlertId: str
    subject: Optional[str] = None
    description: Optional[str] = None
    labels: list[str] = []
    priority: int
    applicationId: Optional[str] = None
    environmentId: Optional[str] = None
    customFields: dict[str, Any] = {}


class AlertCommandCreate(EventBase):
    """alert.command.create — plugin requests creation of a new alert."""

    actorType: Literal["plugin"]
    actorContext: PluginActorContext
    alert: AlertCommandInput


class AlertCommandAcknowledge(EventBase):
    """alert.command.acknowledge — plugin acknowledges an alert."""

    actorType: Literal["plugin"]
    actorContext: PluginActorContext
    alertId: str


class AlertCommandClose(EventBase):
    """alert.command.close — plugin closes an alert."""

    actorType: Literal["plugin"]
    actorContext: PluginActorContext
    alertId: str
    closeReason: str


class AlertCommandAddNote(EventBase):
    """alert.command.addNote — plugin adds a note to an alert."""

    actorType: Literal["plugin"]
    actorContext: PluginActorContext
    alertId: str
    note: NoteInput


class AlertCommandReassign(EventBase):
    """alert.command.reassign — fired by escalation timer (system) or plugin."""

    actorType: Literal["system", "plugin"]
    actorContext: Union[SystemActorContext, PluginActorContext]
    alertId: str
    userId: str


class AlertRequestProcess(EventBase):
    """alert.request.process — published by connection_management when an external
    monitoring system delivers an alert through a configured connection."""

    actorType: Literal["system"]
    actorContext: SystemActorContext
    action: Literal["open", "update", "close"]
    connectionId: str
    parsedData: ParsedAlertData
