from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel
from ..shared.refs import UserRef, NamedRef


class ReviewedByUser(BaseModel):
    """Identity reference of the reviewer in PostmortemSnapshot.reviewedBy — a
    snapshot field, so identity only (no role/permissions; roles live only in the
    event actor). A postmortem can be approved by a user or a service account
    (equal rights); plugins cannot approve."""

    actorType: Literal["user", "serviceAccount"]
    user: Optional[UserRef] = None             # set when actorType == "user"
    serviceAccount: Optional[NamedRef] = None  # set when actorType == "serviceAccount"


class PostmortemSnapshot(BaseModel):
    id: str
    summary: str
    rootCause: str
    state: Literal["draft", "inReview", "approved", "completed"]
    submittedAt: Optional[datetime] = None
    approvedAt: Optional[datetime] = None
    completedAt: Optional[datetime] = None
    reviewedBy: Optional[ReviewedByUser] = None
