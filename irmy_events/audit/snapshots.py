from datetime import datetime
from typing import Any, Literal, Optional
from pydantic import BaseModel
from ..shared.refs import UserRef, NamedRef


# ---------------------------------------------------------------------------
# Shared person / group refs used only in audit snapshots
# ---------------------------------------------------------------------------


class AuditOwnerRef(BaseModel):
    """techOwner / productOwner reference inside AuditApplicationSnapshot
    and AuditServiceSnapshot."""

    id: str
    firstName: str
    lastName: str
    email: str


# ---------------------------------------------------------------------------
# user_management snapshots
# ---------------------------------------------------------------------------


class AuditUserSnapshot(BaseModel):
    id: str
    firstName: str
    lastName: str
    email: str
    isBlocked: bool
    role: NamedRef
    groups: list[NamedRef]


class AuditServiceAccountSnapshot(BaseModel):
    id: str
    name: str
    role: NamedRef
    expirationDate: Optional[datetime] = None


class AuditRoleSnapshot(BaseModel):
    id: str
    name: str
    description: str
    permissions: list[str]
    permissionsBitMask: int


class AuditGroupSnapshot(BaseModel):
    id: str
    name: str
    description: str
    members: list[UserRef]


# ---------------------------------------------------------------------------
# application_management snapshots
# ---------------------------------------------------------------------------


class AuditApplicationSnapshot(BaseModel):
    """Full application snapshot used in audit events.
    Different from the lightweight ApplicationSnapshot used in operational events."""

    id: str
    name: str
    description: str
    tags: dict[str, str]
    techOwner: Optional[AuditOwnerRef] = None
    productOwner: Optional[AuditOwnerRef] = None


class AuditServiceSnapshot(BaseModel):
    """Full service snapshot used in audit events.
    Different from the lightweight ServiceSnapshot used in operational events."""

    id: str
    name: str
    description: str
    tags: dict[str, str]
    techOwner: Optional[AuditOwnerRef] = None
    productOwner: Optional[AuditOwnerRef] = None


class AuditEnvironmentSnapshot(BaseModel):
    id: str
    name: str
    description: str


class AuditEscalationStepSnapshot(BaseModel):
    """One escalation step. `delaySeconds` is relative to alert creation time."""
    delaySeconds: int
    user: UserRef


class AuditOnCallParticipant(BaseModel):
    order: int
    shiftDurationSeconds: int
    user: Optional[UserRef] = None
    group: Optional[NamedRef] = None


class AuditOnCallRotationSnapshot(BaseModel):
    id: str
    participants: list[AuditOnCallParticipant]
    startedAt: datetime


class AuditOnCallRotationOverrideSnapshot(BaseModel):
    id: str
    parentRotation: AuditOnCallRotationSnapshot
    user: Optional[UserRef] = None
    group: Optional[NamedRef] = None
    startedAt: datetime
    endedAt: datetime


class AuditSilenceRuleSnapshot(BaseModel):
    id: str
    name: str
    action: Literal["skipNotification", "drop"]
    condition: dict[str, Any]
    enabled: bool
    order: int


class AuditServiceAclEntry(BaseModel):
    user: Optional[UserRef] = None
    group: Optional[NamedRef] = None
    aclLevel: Literal["Participant", "Manager"]


class AuditServiceAclSnapshot(BaseModel):
    entries: list[AuditServiceAclEntry]


# ---------------------------------------------------------------------------
# incident_management snapshots
# ---------------------------------------------------------------------------


class AuditIncidentRoleAssignment(BaseModel):
    roleLabel: str
    assigneeType: Literal["productOwner", "techOwner", "user", "none"]
    user: Optional[UserRef] = None


class AuditIncidentRuleSnapshot(BaseModel):
    id: str
    name: str
    condition: dict[str, Any]
    incidentSeverity: Literal["critical", "high", "medium", "low"]
    enabled: bool
    roleAssignments: list[AuditIncidentRoleAssignment]
    createdAt: datetime


# ---------------------------------------------------------------------------
# connection_management snapshots
# ---------------------------------------------------------------------------


class AuditPipelinesSnapshot(BaseModel):
    """Pipeline trees per alert action. Each tree is a full JSON snapshot of the
    pipeline configuration; its shape is owned by connection_management and is
    not validated here. `open` is always present; `close` / `update` are null
    when the connection or template has no logic for that action."""

    open: dict[str, Any]
    close: Optional[dict[str, Any]] = None
    update: Optional[dict[str, Any]] = None


class AuditKeywordSnapshot(BaseModel):
    name: str
    macro: str


class AuditConnectionSnapshot(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    enabled: bool
    source: str
    # null if the template the connection was created from has been deleted
    template: Optional[NamedRef] = None
    pipelines: AuditPipelinesSnapshot


class AuditConnectionTemplateSnapshot(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    source: str
    instruction: Optional[str] = None
    # true only for the system-level Blank template, which is never deleted
    isBlank: bool
    pipelines: AuditPipelinesSnapshot
    keywords: list[AuditKeywordSnapshot]


# ---------------------------------------------------------------------------
# plugin_management snapshots
#
# Plugins are organisation-scoped like connections. Scoped config / reactions
# reference services/apps/envs by id only — plugin_management is the emitter and
# does not own those entities' names, so context envelopes here carry ids, not
# full AuditService/Application/Environment snapshots.
# ---------------------------------------------------------------------------


class AuditPluginRef(BaseModel):
    """Identifies the plugin a config / rule change belongs to.

    Deliberately no ``version`` -- it's operational detail, not audit-worthy
    anywhere in the plugin domain."""

    id: str
    name: str


class AuditPluginSnapshot(BaseModel):
    """Full plugin state for install / uninstall / enable / disable before-after."""

    id: str
    name: str
    version: str
    displayName: str
    enabled: bool
    isSystem: bool
    license: Optional[str] = None


class AuditPluginConfigFieldSnapshot(BaseModel):
    """One config field's audited state. Secret values are never recorded — only
    whether one is set (``isSet``); ``value`` stays null for secrets."""

    key: str
    type: str
    isSecret: bool
    isSet: bool
    value: Optional[Any] = None


class AuditPluginConfigSnapshot(BaseModel):
    """A plugin's config at one scope, secrets redacted. The scope and its
    service/application/environment context live on the event."""

    fields: list[AuditPluginConfigFieldSnapshot]


class AuditPluginRuleBlockSnapshot(BaseModel):
    """One reaction block within a rule's per-plugin ordered sequence.
    ``fields`` is safe to record in full -- a capability's config schema can
    never declare a secret field, unlike plugin config (see
    AuditPluginConfigFieldSnapshot)."""

    pluginId: str
    pluginName: str
    stepOrder: int
    capability: str
    stopOnError: bool
    fields: dict[str, Any]


class AuditPluginRuleSnapshot(BaseModel):
    """A rule's own fields. ``owner`` and (iff ``owner == "service"``) the
    service it belongs to are carried on the event, not here -- see
    AuditPluginRuleCreate/Modify/Delete. No separate envelope for
    ``owner == "user"``: only the owning user may ever create/modify/delete
    their own rule, so the event's ``actorContext`` already identifies them."""

    id: str
    owner: Literal["global", "service", "user"]
    eventDomain: str
    events: list[str]  # routing keys, or the literal "--all--" sentinel
    conditionTree: dict[str, Any]
    reactionBlocks: list[AuditPluginRuleBlockSnapshot]
