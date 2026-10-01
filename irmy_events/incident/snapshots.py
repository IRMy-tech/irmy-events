from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel
from ..shared.refs import UserRef


class IncidentSnapshot(BaseModel):
    """Canonical incident snapshot attached to every incident event.

    incidentRoles maps roleLabel (e.g. "incident_commander") to the assigned UserRef.
    One user may hold multiple roles; each label maps to exactly one user.
    """

    id: str
    title: str
    description: str
    severity: Literal["critical", "high", "medium", "low"]
    state: Literal["open", "acknowledged", "investigating", "confirmed", "resolved", "closed"]
    incidentRoles: dict[str, UserRef]
    participants: list[UserRef]
    createdAt: datetime


class ActionItemSnapshot(BaseModel):
    id: str
    summary: str
    description: Optional[str] = None
    assignedTo: Optional[UserRef] = None
    dueDate: Optional[datetime] = None
    doneAt: Optional[datetime] = None
