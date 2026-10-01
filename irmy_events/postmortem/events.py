from datetime import datetime
from typing import Literal, Optional
from ..shared.actors import EventBase, ActorContext
from ..application.snapshots import ApplicationSnapshot, ServiceSnapshot, EnvironmentSnapshot
from ..incident.snapshots import IncidentSnapshot
from .snapshots import PostmortemSnapshot


class PostmortemDraftCreated(EventBase):
    """postmortem.draft.created — a postmortem draft was created for an incident."""

    actorType: Literal["user", "serviceAccount", "plugin"]
    actorContext: ActorContext
    incident: IncidentSnapshot
    postmortem: PostmortemSnapshot
    application: ApplicationSnapshot
    service: ServiceSnapshot
    environment: EnvironmentSnapshot


class PostmortemDraftUpdated(EventBase):
    """postmortem.draft.updated — a draft postmortem's summary and/or rootCause changed.
    At least one of previousSummary / previousRootCause is non-null."""

    actorType: Literal["user", "serviceAccount", "plugin"]
    actorContext: ActorContext
    incident: IncidentSnapshot
    postmortem: PostmortemSnapshot
    previousSummary: Optional[str] = None
    previousRootCause: Optional[str] = None
    updatedAt: datetime
    application: ApplicationSnapshot
    service: ServiceSnapshot
    environment: EnvironmentSnapshot


class PostmortemStateSubmitted(EventBase):
    """postmortem.state.submitted — postmortem draft submitted for review (draft → inReview)."""

    actorType: Literal["user", "serviceAccount", "plugin"]
    actorContext: ActorContext
    incident: IncidentSnapshot
    postmortem: PostmortemSnapshot
    application: ApplicationSnapshot
    service: ServiceSnapshot
    environment: EnvironmentSnapshot


class PostmortemStateBackToDraft(EventBase):
    """postmortem.state.backToDraft — postmortem recalled to draft so it can be
    edited again. Actor is whoever recalled it (user, serviceAccount or plugin)."""

    actorType: Literal["user", "serviceAccount", "plugin"]
    actorContext: ActorContext
    incident: IncidentSnapshot
    postmortem: PostmortemSnapshot
    application: ApplicationSnapshot
    service: ServiceSnapshot
    environment: EnvironmentSnapshot


class PostmortemStateApproved(EventBase):
    """postmortem.state.approved — postmortem approved (inReview → approved).
    Users and service accounts (equal rights) can approve; plugins cannot."""

    actorType: Literal["user", "serviceAccount"]
    actorContext: ActorContext
    incident: IncidentSnapshot
    postmortem: PostmortemSnapshot
    application: ApplicationSnapshot
    service: ServiceSnapshot
    environment: EnvironmentSnapshot


class PostmortemStateCompleted(EventBase):
    """postmortem.state.completed — postmortem completed.
    Users and service accounts (equal rights) can complete; plugins cannot.
    A separate incident.state.closed (actorType=system) is also published."""

    actorType: Literal["user", "serviceAccount"]
    actorContext: ActorContext
    incident: IncidentSnapshot
    postmortem: PostmortemSnapshot
    application: ApplicationSnapshot
    service: ServiceSnapshot
    environment: EnvironmentSnapshot


class PostmortemDraftDeleted(EventBase):
    """postmortem.draft.deleted — a postmortem draft was deleted.

    Only users and service accounts may delete a draft (plugins cannot).
    The postmortem snapshot carries the state as it was at the moment of
    deletion (state always "draft"). After deletion the incident can be
    reopened (resolved → confirmed).
    """

    actorType: Literal["user", "serviceAccount"]
    actorContext: ActorContext
    incident: IncidentSnapshot
    postmortem: PostmortemSnapshot
    application: ApplicationSnapshot
    service: ServiceSnapshot
    environment: EnvironmentSnapshot
