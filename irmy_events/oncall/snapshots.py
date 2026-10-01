from typing import Literal, Optional
from pydantic import BaseModel

from ..shared.refs import NamedRef, UserRef


class OnCallIdentitySnapshot(BaseModel):
    """Who is on call, as attached to oncall.changed. Mirrors application_management's
    CurrentOnCallView: a group resolves to the group plus its current members, never to
    one arbitrary member."""

    memberType: Literal["user", "group"]
    user: Optional[UserRef] = None
    group: Optional[NamedRef] = None
    groupMembers: Optional[list[UserRef]] = None
