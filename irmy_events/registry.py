"""Centralized event registry for IRMy.

Maps every routing key in :class:`RoutingKeys` to its static metadata:
category, human-readable name, description, plugin permissions, and the
Pydantic ``payload_model`` for the key's body. This makes the registry the
single source of truth for routing-key -> payload deserialization:
``EVENT_REGISTRY[key].payload_model.model_validate(body)``.

Consumers:
  - UI event picker — groups by category, renders display_name/description
  - plugin_management — validates plugin manifests; deserializes event bodies
  - irmy_sdk — manifest-side runtime validators
  - audit log viewer, event explorer, debug tooling

``payload_model`` is ``None`` only for internal keys whose body has no single
model (e.g. ``SCHEDULER_REQUEST`` is a discriminated union); resolve those at
the call site.

Tests in ``tests/test_registry.py`` assert every RoutingKeys member has an
entry and that every plugin-facing key has a payload_model. CI runs them on
every change.
"""
from enum import Enum
from pydantic import BaseModel, ConfigDict

from .routing_keys import RoutingKeys
from .alert import AlertActionUpdate, AlertAssigneeModify, AlertCommandAcknowledge, AlertCommandAddNote, AlertCommandClose, AlertCommandCreate, AlertCommandReassign, AlertNoteAdd, AlertRequestProcess, AlertStateAcknowledge, AlertStateClose, AlertStateOpen
from .application import ApplicationStateAlertLevelDecreased, ApplicationStateAlertLevelIncreased, ApplicationStateAlerted, ApplicationStateRecovered
from .audit import AuditApplicationCreate, AuditApplicationDelete, AuditApplicationModify, AuditConnectionCreate, AuditConnectionDelete, AuditConnectionModify, AuditConnectionTemplateCreate, AuditConnectionTemplateDelete, AuditConnectionTemplateModify, AuditEnvironmentCreate, AuditEnvironmentDelete, AuditEnvironmentModify, AuditEscalationCreate, AuditEscalationDelete, AuditEscalationModify, AuditEscalationOverrideCreate, AuditEscalationOverrideDelete, AuditEscalationOverrideModify, AuditGroupCreate, AuditGroupDelete, AuditGroupMembersModify, AuditGroupModify, AuditIncidentRuleCreate, AuditIncidentRuleDelete, AuditIncidentRuleModify, AuditOnCallRotationCreate, AuditOnCallRotationDelete, AuditOnCallRotationOverrideCreate, AuditOnCallRotationOverrideDelete, AuditRoleCreate, AuditRoleDelete, AuditRoleModify, AuditServiceAccountCreate, AuditServiceAccountDelete, AuditServiceAclModify, AuditServiceCreate, AuditServiceDelete, AuditServiceModify, AuditSilenceRuleCreate, AuditSilenceRuleDelete, AuditSilenceRuleModify, AuditUserCreate, AuditUserDelete, AuditUserModify, AuditPluginInstall, AuditPluginUninstall, AuditPluginEnable, AuditPluginDisable, AuditPluginUpdate, AuditPluginConfigModify, AuditPluginRuleCreate, AuditPluginRuleModify, AuditPluginRuleDelete
from .incident import IncidentActionItemCreated, IncidentActionItemDone, IncidentActionItemUpdated, IncidentCommandAddActionItem, IncidentCommandAddComment, IncidentCommandAddParticipant, IncidentCommandAssignRole, IncidentCommandChangeSeverity, IncidentCommandChangeState, IncidentCommandCompleteActionItem, IncidentCommandCreate, IncidentCommandUpdate, IncidentCommandUpdateActionItem, IncidentCommentAdded, IncidentCreated, IncidentParticipantAdded, IncidentRoleAssigned, IncidentSeverityDeescalated, IncidentSeverityEscalated, IncidentStateAcknowledged, IncidentStateClosed, IncidentStateConfirmed, IncidentStateInvestigating, IncidentStateReopened, IncidentStateResolved, IncidentUpdated
from .oncall import OncallCommandExtend, OncallCommandCheck, OnCallChanged
from .postmortem import PostmortemCommandChangeState, PostmortemCommandCreateDraft, PostmortemDraftCreated, PostmortemDraftDeleted, PostmortemDraftUpdated, PostmortemStateApproved, PostmortemStateBackToDraft, PostmortemStateCompleted, PostmortemStateSubmitted
from .user import UserPasswordResetInitiated, UserPasswordResetRequested
from .security import SecurityLoginSuccess, SecurityLoginFailed, SecurityPasswordChange, SecurityPasswordReset, SecurityOwnPasswordReset, SecurityServiceAccountTokenRotated


# ─── Categories ───────────────────────────────────────────────────────────────


class EventCategory(str, Enum):
    """High-level grouping for UI navigation."""

    ALERT = "alert"
    APPLICATION = "application"
    INCIDENT = "incident"
    POSTMORTEM = "postmortem"
    ON_CALL = "on_call"
    SCHEDULER = "scheduler"
    USER_MANAGEMENT = "user_management"
    AUDIT = "audit"
    SECURITY = "security"


# ─── Metadata model ───────────────────────────────────────────────────────────


class EventMetadata(BaseModel):
    """Static metadata about a single routing key."""

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    routing_key: RoutingKeys
    category: EventCategory
    display_name: str
    description: str
    plugin_subscribable: bool
    plugin_publishable: bool
    payload_model: type[BaseModel] | None


# ─── Registry ─────────────────────────────────────────────────────────────────


EVENT_REGISTRY: dict[RoutingKeys, EventMetadata] = {

    # ── Alert: commands ──────────────────────────────────────────────────────
    RoutingKeys.ALERT_COMMAND_CREATE: EventMetadata(
        routing_key=RoutingKeys.ALERT_COMMAND_CREATE,
        payload_model=AlertCommandCreate,
        category=EventCategory.ALERT,
        display_name="Create alert",
        description="Command to create a new alert.",
        plugin_subscribable=False,
        plugin_publishable=True,
    ),
    RoutingKeys.ALERT_COMMAND_ACKNOWLEDGE: EventMetadata(
        routing_key=RoutingKeys.ALERT_COMMAND_ACKNOWLEDGE,
        payload_model=AlertCommandAcknowledge,
        category=EventCategory.ALERT,
        display_name="Acknowledge alert",
        description="Command to acknowledge an alert.",
        plugin_subscribable=False,
        plugin_publishable=True,
    ),
    RoutingKeys.ALERT_COMMAND_CLOSE: EventMetadata(
        routing_key=RoutingKeys.ALERT_COMMAND_CLOSE,
        payload_model=AlertCommandClose,
        category=EventCategory.ALERT,
        display_name="Close alert",
        description="Command to close an alert.",
        plugin_subscribable=False,
        plugin_publishable=True,
    ),
    RoutingKeys.ALERT_COMMAND_ADD_NOTE: EventMetadata(
        routing_key=RoutingKeys.ALERT_COMMAND_ADD_NOTE,
        payload_model=AlertCommandAddNote,
        category=EventCategory.ALERT,
        display_name="Add note to alert",
        description="Command to add a note to an alert.",
        plugin_subscribable=False,
        plugin_publishable=True,
    ),
    RoutingKeys.ALERT_COMMAND_REASSIGN: EventMetadata(
        routing_key=RoutingKeys.ALERT_COMMAND_REASSIGN,
        payload_model=AlertCommandReassign,
        category=EventCategory.ALERT,
        display_name="Reassign alert",
        description="Command to reassign an alert to a different user.",
        plugin_subscribable=False,
        plugin_publishable=True,
    ),
    RoutingKeys.ALERT_REQUEST_PROCESS: EventMetadata(
        routing_key=RoutingKeys.ALERT_REQUEST_PROCESS,
        payload_model=AlertRequestProcess,
        category=EventCategory.ALERT,
        display_name="Process incoming alert",
        description="Internal request to process an alert received by alert_listener.",
        plugin_subscribable=False,
        plugin_publishable=False,
    ),

    # ── Alert: events ────────────────────────────────────────────────────────
    RoutingKeys.ALERT_STATE_OPEN: EventMetadata(
        routing_key=RoutingKeys.ALERT_STATE_OPEN,
        payload_model=AlertStateOpen,
        category=EventCategory.ALERT,
        display_name="Alert opened",
        description="Published when a new alert is opened.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.ALERT_STATE_CLOSE: EventMetadata(
        routing_key=RoutingKeys.ALERT_STATE_CLOSE,
        payload_model=AlertStateClose,
        category=EventCategory.ALERT,
        display_name="Alert closed",
        description="Published when an alert is closed.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.ALERT_STATE_ACKNOWLEDGE: EventMetadata(
        routing_key=RoutingKeys.ALERT_STATE_ACKNOWLEDGE,
        payload_model=AlertStateAcknowledge,
        category=EventCategory.ALERT,
        display_name="Alert acknowledged",
        description="Published when an alert is acknowledged.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.ALERT_ACTION_UPDATE: EventMetadata(
        routing_key=RoutingKeys.ALERT_ACTION_UPDATE,
        payload_model=AlertActionUpdate,
        category=EventCategory.ALERT,
        display_name="Alert updated",
        description="Published when an alert is updated with new data.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.ALERT_ASSIGNEE_MODIFY: EventMetadata(
        routing_key=RoutingKeys.ALERT_ASSIGNEE_MODIFY,
        payload_model=AlertAssigneeModify,
        category=EventCategory.ALERT,
        display_name="Alert assignee modified",
        description="Published when an alert is assigned to a user.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.ALERT_NOTE_ADD: EventMetadata(
        routing_key=RoutingKeys.ALERT_NOTE_ADD,
        payload_model=AlertNoteAdd,
        category=EventCategory.ALERT,
        display_name="Note added to alert",
        description="Published when a note is added to an alert.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),

    # ── Application: state events ────────────────────────────────────────────
    RoutingKeys.APPLICATION_STATE_ALERTED: EventMetadata(
        routing_key=RoutingKeys.APPLICATION_STATE_ALERTED,
        payload_model=ApplicationStateAlerted,
        category=EventCategory.APPLICATION,
        display_name="Application entered alerted state",
        description="Published when an application transitions from no-alert to in-alert state.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.APPLICATION_STATE_RECOVERED: EventMetadata(
        routing_key=RoutingKeys.APPLICATION_STATE_RECOVERED,
        payload_model=ApplicationStateRecovered,
        category=EventCategory.APPLICATION,
        display_name="Application recovered",
        description="Published when an application transitions from in-alert to no-alert state.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.APPLICATION_STATE_ALERT_LEVEL_INCREASED: EventMetadata(
        routing_key=RoutingKeys.APPLICATION_STATE_ALERT_LEVEL_INCREASED,
        payload_model=ApplicationStateAlertLevelIncreased,
        category=EventCategory.APPLICATION,
        display_name="Application alert level increased",
        description="Published when the highest alert priority for an application increases.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.APPLICATION_STATE_ALERT_LEVEL_DECREASED: EventMetadata(
        routing_key=RoutingKeys.APPLICATION_STATE_ALERT_LEVEL_DECREASED,
        payload_model=ApplicationStateAlertLevelDecreased,
        category=EventCategory.APPLICATION,
        display_name="Application alert level decreased",
        description="Published when the highest alert priority for an application decreases.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),

    # ── On-call: commands ────────────────────────────────────────────────────
    RoutingKeys.ONCALL_COMMAND_EXTEND: EventMetadata(
        routing_key=RoutingKeys.ONCALL_COMMAND_EXTEND,
        payload_model=OncallCommandExtend,
        category=EventCategory.ON_CALL,
        display_name="Extend on-call shift",
        description="Command to extend a user's current on-call shift.",
        plugin_subscribable=False,
        plugin_publishable=False,
    ),
    RoutingKeys.ONCALL_COMMAND_CHECK: EventMetadata(
        routing_key=RoutingKeys.ONCALL_COMMAND_CHECK,
        payload_model=OncallCommandCheck,
        category=EventCategory.ON_CALL,
        display_name="Check on-call identity",
        description=(
            "Internal, self-scheduled command that triggers application_management to "
            "recompute who is effectively on call for a rotation and publish oncall.changed "
            "if it moved."
        ),
        plugin_subscribable=False,
        plugin_publishable=False,
    ),

    # ── On-call: events ──────────────────────────────────────────────────────
    RoutingKeys.ONCALL_CHANGED: EventMetadata(
        routing_key=RoutingKeys.ONCALL_CHANGED,
        payload_model=OnCallChanged,
        category=EventCategory.ON_CALL,
        display_name="On-call identity changed",
        description=(
            "Published when the effective on-call person/group for a service or an "
            "application+environment changes, regardless of cause (shift handoff, "
            "override start/end, rotation enabled/disabled)."
        ),
        plugin_subscribable=True,
        plugin_publishable=False,
    ),

    # ── Scheduler: infrastructure ────────────────────────────────────────────
    RoutingKeys.SCHEDULER_REQUEST: EventMetadata(
        routing_key=RoutingKeys.SCHEDULER_REQUEST,
        payload_model=None,
        category=EventCategory.SCHEDULER,
        display_name="Scheduled job trigger",
        description="Internal scheduler infrastructure event; not exposed to plugins.",
        plugin_subscribable=False,
        plugin_publishable=False,
    ),

    # ── Incident: commands ───────────────────────────────────────────────────
    RoutingKeys.INCIDENT_COMMAND_CREATE: EventMetadata(
        routing_key=RoutingKeys.INCIDENT_COMMAND_CREATE,
        payload_model=IncidentCommandCreate,
        category=EventCategory.INCIDENT,
        display_name="Create incident",
        description="Command to create a new incident.",
        plugin_subscribable=False,
        plugin_publishable=True,
    ),
    RoutingKeys.INCIDENT_COMMAND_UPDATE: EventMetadata(
        routing_key=RoutingKeys.INCIDENT_COMMAND_UPDATE,
        payload_model=IncidentCommandUpdate,
        category=EventCategory.INCIDENT,
        display_name="Update incident",
        description="Command to update an incident's details.",
        plugin_subscribable=False,
        plugin_publishable=True,
    ),
    RoutingKeys.INCIDENT_COMMAND_CHANGE_SEVERITY: EventMetadata(
        routing_key=RoutingKeys.INCIDENT_COMMAND_CHANGE_SEVERITY,
        payload_model=IncidentCommandChangeSeverity,
        category=EventCategory.INCIDENT,
        display_name="Change incident severity",
        description="Command to change an incident's severity level.",
        plugin_subscribable=False,
        plugin_publishable=True,
    ),
    RoutingKeys.INCIDENT_COMMAND_CHANGE_STATE: EventMetadata(
        routing_key=RoutingKeys.INCIDENT_COMMAND_CHANGE_STATE,
        payload_model=IncidentCommandChangeState,
        category=EventCategory.INCIDENT,
        display_name="Change incident state",
        description="Command to transition an incident to a new state.",
        plugin_subscribable=False,
        plugin_publishable=True,
    ),
    RoutingKeys.INCIDENT_COMMAND_ASSIGN_ROLE: EventMetadata(
        routing_key=RoutingKeys.INCIDENT_COMMAND_ASSIGN_ROLE,
        payload_model=IncidentCommandAssignRole,
        category=EventCategory.INCIDENT,
        display_name="Assign incident role",
        description="Command to assign a role within an incident to a user.",
        plugin_subscribable=False,
        plugin_publishable=True,
    ),
    RoutingKeys.INCIDENT_COMMAND_ADD_PARTICIPANT: EventMetadata(
        routing_key=RoutingKeys.INCIDENT_COMMAND_ADD_PARTICIPANT,
        payload_model=IncidentCommandAddParticipant,
        category=EventCategory.INCIDENT,
        display_name="Add incident participant",
        description="Command to add a participant to an incident.",
        plugin_subscribable=False,
        plugin_publishable=True,
    ),
    RoutingKeys.INCIDENT_COMMAND_ADD_COMMENT: EventMetadata(
        routing_key=RoutingKeys.INCIDENT_COMMAND_ADD_COMMENT,
        payload_model=IncidentCommandAddComment,
        category=EventCategory.INCIDENT,
        display_name="Add incident comment",
        description="Command to add a comment to an incident.",
        plugin_subscribable=False,
        plugin_publishable=True,
    ),
    RoutingKeys.INCIDENT_COMMAND_ADD_ACTION_ITEM: EventMetadata(
        routing_key=RoutingKeys.INCIDENT_COMMAND_ADD_ACTION_ITEM,
        payload_model=IncidentCommandAddActionItem,
        category=EventCategory.INCIDENT,
        display_name="Add incident action item",
        description="Command to add an action item to an incident.",
        plugin_subscribable=False,
        plugin_publishable=True,
    ),
    RoutingKeys.INCIDENT_COMMAND_COMPLETE_ACTION_ITEM: EventMetadata(
        routing_key=RoutingKeys.INCIDENT_COMMAND_COMPLETE_ACTION_ITEM,
        payload_model=IncidentCommandCompleteActionItem,
        category=EventCategory.INCIDENT,
        display_name="Complete incident action item",
        description="Command to mark an incident action item as completed.",
        plugin_subscribable=False,
        plugin_publishable=True,
    ),
    RoutingKeys.INCIDENT_COMMAND_UPDATE_ACTION_ITEM: EventMetadata(
        routing_key=RoutingKeys.INCIDENT_COMMAND_UPDATE_ACTION_ITEM,
        payload_model=IncidentCommandUpdateActionItem,
        category=EventCategory.INCIDENT,
        display_name="Update incident action item",
        description="Command to reassign and/or reschedule an incident action item.",
        plugin_subscribable=False,
        plugin_publishable=True,
    ),

    # ── Incident: events ─────────────────────────────────────────────────────
    RoutingKeys.INCIDENT_CREATED: EventMetadata(
        routing_key=RoutingKeys.INCIDENT_CREATED,
        payload_model=IncidentCreated,
        category=EventCategory.INCIDENT,
        display_name="Incident created",
        description="Published when a new incident is opened.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.INCIDENT_UPDATED: EventMetadata(
        routing_key=RoutingKeys.INCIDENT_UPDATED,
        payload_model=IncidentUpdated,
        category=EventCategory.INCIDENT,
        display_name="Incident updated",
        description="Published when an incident's details are updated.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.INCIDENT_STATE_ACKNOWLEDGED: EventMetadata(
        routing_key=RoutingKeys.INCIDENT_STATE_ACKNOWLEDGED,
        payload_model=IncidentStateAcknowledged,
        category=EventCategory.INCIDENT,
        display_name="Incident acknowledged",
        description="Published when an incident transitions to the acknowledged state.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.INCIDENT_STATE_INVESTIGATING: EventMetadata(
        routing_key=RoutingKeys.INCIDENT_STATE_INVESTIGATING,
        payload_model=IncidentStateInvestigating,
        category=EventCategory.INCIDENT,
        display_name="Incident under investigation",
        description="Published when an incident transitions to the investigating state.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.INCIDENT_STATE_CONFIRMED: EventMetadata(
        routing_key=RoutingKeys.INCIDENT_STATE_CONFIRMED,
        payload_model=IncidentStateConfirmed,
        category=EventCategory.INCIDENT,
        display_name="Incident confirmed",
        description="Published when an incident transitions to the confirmed state.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.INCIDENT_STATE_RESOLVED: EventMetadata(
        routing_key=RoutingKeys.INCIDENT_STATE_RESOLVED,
        payload_model=IncidentStateResolved,
        category=EventCategory.INCIDENT,
        display_name="Incident resolved",
        description="Published when an incident transitions to the resolved state.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.INCIDENT_STATE_CLOSED: EventMetadata(
        routing_key=RoutingKeys.INCIDENT_STATE_CLOSED,
        payload_model=IncidentStateClosed,
        category=EventCategory.INCIDENT,
        display_name="Incident closed",
        description="Published when an incident transitions to the closed state.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.INCIDENT_STATE_REOPENED: EventMetadata(
        routing_key=RoutingKeys.INCIDENT_STATE_REOPENED,
        payload_model=IncidentStateReopened,
        category=EventCategory.INCIDENT,
        display_name="Incident reopened",
        description="Published when a closed incident is reopened.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.INCIDENT_SEVERITY_ESCALATED: EventMetadata(
        routing_key=RoutingKeys.INCIDENT_SEVERITY_ESCALATED,
        payload_model=IncidentSeverityEscalated,
        category=EventCategory.INCIDENT,
        display_name="Incident severity escalated",
        description="Published when an incident's severity is increased.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.INCIDENT_SEVERITY_DEESCALATED: EventMetadata(
        routing_key=RoutingKeys.INCIDENT_SEVERITY_DEESCALATED,
        payload_model=IncidentSeverityDeescalated,
        category=EventCategory.INCIDENT,
        display_name="Incident severity deescalated",
        description="Published when an incident's severity is decreased.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.INCIDENT_ROLE_ASSIGNED: EventMetadata(
        routing_key=RoutingKeys.INCIDENT_ROLE_ASSIGNED,
        payload_model=IncidentRoleAssigned,
        category=EventCategory.INCIDENT,
        display_name="Incident role assigned",
        description="Published when a role within an incident is assigned to a user.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.INCIDENT_PARTICIPANT_ADDED: EventMetadata(
        routing_key=RoutingKeys.INCIDENT_PARTICIPANT_ADDED,
        payload_model=IncidentParticipantAdded,
        category=EventCategory.INCIDENT,
        display_name="Incident participant added",
        description="Published when a participant is added to an incident.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.INCIDENT_COMMENT_ADDED: EventMetadata(
        routing_key=RoutingKeys.INCIDENT_COMMENT_ADDED,
        payload_model=IncidentCommentAdded,
        category=EventCategory.INCIDENT,
        display_name="Incident comment added",
        description="Published when a comment is added to an incident.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.INCIDENT_ACTION_ITEM_CREATED: EventMetadata(
        routing_key=RoutingKeys.INCIDENT_ACTION_ITEM_CREATED,
        payload_model=IncidentActionItemCreated,
        category=EventCategory.INCIDENT,
        display_name="Incident action item created",
        description="Published when an action item is created on an incident.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.INCIDENT_ACTION_ITEM_DONE: EventMetadata(
        routing_key=RoutingKeys.INCIDENT_ACTION_ITEM_DONE,
        payload_model=IncidentActionItemDone,
        category=EventCategory.INCIDENT,
        display_name="Incident action item completed",
        description="Published when an action item on an incident is marked as done.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.INCIDENT_ACTION_ITEM_UPDATED: EventMetadata(
        routing_key=RoutingKeys.INCIDENT_ACTION_ITEM_UPDATED,
        payload_model=IncidentActionItemUpdated,
        category=EventCategory.INCIDENT,
        display_name="Incident action item updated",
        description="Published when an action item's assignee and/or due date is changed.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),

    # ── Postmortem: commands ─────────────────────────────────────────────────
    RoutingKeys.POSTMORTEM_COMMAND_CREATE_DRAFT: EventMetadata(
        routing_key=RoutingKeys.POSTMORTEM_COMMAND_CREATE_DRAFT,
        payload_model=PostmortemCommandCreateDraft,
        category=EventCategory.POSTMORTEM,
        display_name="Create postmortem draft",
        description="Command to create a postmortem draft for an incident.",
        plugin_subscribable=False,
        plugin_publishable=True,
    ),
    RoutingKeys.POSTMORTEM_COMMAND_CHANGE_STATE: EventMetadata(
        routing_key=RoutingKeys.POSTMORTEM_COMMAND_CHANGE_STATE,
        payload_model=PostmortemCommandChangeState,
        category=EventCategory.POSTMORTEM,
        display_name="Change postmortem state",
        description="Command to transition a postmortem to a new state.",
        plugin_subscribable=False,
        plugin_publishable=True,
    ),

    # ── Postmortem: events ───────────────────────────────────────────────────
    RoutingKeys.POSTMORTEM_DRAFT_CREATED: EventMetadata(
        routing_key=RoutingKeys.POSTMORTEM_DRAFT_CREATED,
        payload_model=PostmortemDraftCreated,
        category=EventCategory.POSTMORTEM,
        display_name="Postmortem draft created",
        description="Published when a postmortem draft is created.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.POSTMORTEM_DRAFT_UPDATED: EventMetadata(
        routing_key=RoutingKeys.POSTMORTEM_DRAFT_UPDATED,
        payload_model=PostmortemDraftUpdated,
        category=EventCategory.POSTMORTEM,
        display_name="Postmortem draft updated",
        description="Published when a postmortem draft is updated.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.POSTMORTEM_DRAFT_DELETED: EventMetadata(
        routing_key=RoutingKeys.POSTMORTEM_DRAFT_DELETED,
        payload_model=PostmortemDraftDeleted,
        category=EventCategory.POSTMORTEM,
        display_name="Postmortem draft deleted",
        description="Published when a postmortem draft is deleted.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.POSTMORTEM_STATE_SUBMITTED: EventMetadata(
        routing_key=RoutingKeys.POSTMORTEM_STATE_SUBMITTED,
        payload_model=PostmortemStateSubmitted,
        category=EventCategory.POSTMORTEM,
        display_name="Postmortem submitted",
        description="Published when a postmortem is submitted for approval.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.POSTMORTEM_STATE_BACK_TO_DRAFT: EventMetadata(
        routing_key=RoutingKeys.POSTMORTEM_STATE_BACK_TO_DRAFT,
        payload_model=PostmortemStateBackToDraft,
        category=EventCategory.POSTMORTEM,
        display_name="Postmortem returned to draft",
        description="Published when a submitted postmortem is sent back to draft state.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.POSTMORTEM_STATE_APPROVED: EventMetadata(
        routing_key=RoutingKeys.POSTMORTEM_STATE_APPROVED,
        payload_model=PostmortemStateApproved,
        category=EventCategory.POSTMORTEM,
        display_name="Postmortem approved",
        description="Published when a postmortem is approved.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.POSTMORTEM_STATE_COMPLETED: EventMetadata(
        routing_key=RoutingKeys.POSTMORTEM_STATE_COMPLETED,
        payload_model=PostmortemStateCompleted,
        category=EventCategory.POSTMORTEM,
        display_name="Postmortem completed",
        description="Published when a postmortem is marked as completed.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),

    # ── User: events (operational) ───────────────────────────────────────────
    RoutingKeys.USER_PASSWORD_RESET_REQUESTED: EventMetadata(
        routing_key=RoutingKeys.USER_PASSWORD_RESET_REQUESTED,
        payload_model=UserPasswordResetRequested,
        category=EventCategory.USER_MANAGEMENT,
        display_name="Password reset requested",
        description=(
            "Published when a user restores their own forgotten password "
            "(self-service). Carries an encrypted reset link."
        ),
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.USER_PASSWORD_RESET_INITIATED: EventMetadata(
        routing_key=RoutingKeys.USER_PASSWORD_RESET_INITIATED,
        payload_model=UserPasswordResetInitiated,
        category=EventCategory.USER_MANAGEMENT,
        display_name="Password reset initiated by admin",
        description=(
            "Published when an administrator triggers a password reset for "
            "another user. Carries an encrypted reset link."
        ),
        plugin_subscribable=True,
        plugin_publishable=False,
    ),

    # ── Audit: user_management ───────────────────────────────────────────────
    RoutingKeys.AUDIT_USER_CREATE: EventMetadata(
        routing_key=RoutingKeys.AUDIT_USER_CREATE,
        payload_model=AuditUserCreate,
        category=EventCategory.AUDIT,
        display_name="User created",
        description="Published when a user account is created.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.AUDIT_USER_MODIFY: EventMetadata(
        routing_key=RoutingKeys.AUDIT_USER_MODIFY,
        payload_model=AuditUserModify,
        category=EventCategory.AUDIT,
        display_name="User modified",
        description="Published when a user account is modified.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.AUDIT_USER_DELETE: EventMetadata(
        routing_key=RoutingKeys.AUDIT_USER_DELETE,
        payload_model=AuditUserDelete,
        category=EventCategory.AUDIT,
        display_name="User deleted",
        description="Published when a user account is deleted.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.AUDIT_SERVICE_ACCOUNT_CREATE: EventMetadata(
        routing_key=RoutingKeys.AUDIT_SERVICE_ACCOUNT_CREATE,
        payload_model=AuditServiceAccountCreate,
        category=EventCategory.AUDIT,
        display_name="Service account created",
        description="Published when a service account is created.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.AUDIT_SERVICE_ACCOUNT_DELETE: EventMetadata(
        routing_key=RoutingKeys.AUDIT_SERVICE_ACCOUNT_DELETE,
        payload_model=AuditServiceAccountDelete,
        category=EventCategory.AUDIT,
        display_name="Service account deleted",
        description="Published when a service account is deleted.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.AUDIT_ROLE_CREATE: EventMetadata(
        routing_key=RoutingKeys.AUDIT_ROLE_CREATE,
        payload_model=AuditRoleCreate,
        category=EventCategory.AUDIT,
        display_name="Role created",
        description="Published when a role is created.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.AUDIT_ROLE_MODIFY: EventMetadata(
        routing_key=RoutingKeys.AUDIT_ROLE_MODIFY,
        payload_model=AuditRoleModify,
        category=EventCategory.AUDIT,
        display_name="Role modified",
        description="Published when a role is modified.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.AUDIT_ROLE_DELETE: EventMetadata(
        routing_key=RoutingKeys.AUDIT_ROLE_DELETE,
        payload_model=AuditRoleDelete,
        category=EventCategory.AUDIT,
        display_name="Role deleted",
        description="Published when a role is deleted.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.AUDIT_GROUP_CREATE: EventMetadata(
        routing_key=RoutingKeys.AUDIT_GROUP_CREATE,
        payload_model=AuditGroupCreate,
        category=EventCategory.AUDIT,
        display_name="Group created",
        description="Published when a user group is created.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.AUDIT_GROUP_MODIFY: EventMetadata(
        routing_key=RoutingKeys.AUDIT_GROUP_MODIFY,
        payload_model=AuditGroupModify,
        category=EventCategory.AUDIT,
        display_name="Group modified",
        description="Published when a user group is modified (name or description).",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.AUDIT_GROUP_MEMBERS_MODIFY: EventMetadata(
        routing_key=RoutingKeys.AUDIT_GROUP_MEMBERS_MODIFY,
        payload_model=AuditGroupMembersModify,
        category=EventCategory.AUDIT,
        display_name="Group members modified",
        description="Published when a user group's membership is modified.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.AUDIT_GROUP_DELETE: EventMetadata(
        routing_key=RoutingKeys.AUDIT_GROUP_DELETE,
        payload_model=AuditGroupDelete,
        category=EventCategory.AUDIT,
        display_name="Group deleted",
        description="Published when a user group is deleted.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),

    # ── Audit: application_management ────────────────────────────────────────
    RoutingKeys.AUDIT_APPLICATION_CREATE: EventMetadata(
        routing_key=RoutingKeys.AUDIT_APPLICATION_CREATE,
        payload_model=AuditApplicationCreate,
        category=EventCategory.AUDIT,
        display_name="Application created",
        description="Published when an application is created.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.AUDIT_APPLICATION_MODIFY: EventMetadata(
        routing_key=RoutingKeys.AUDIT_APPLICATION_MODIFY,
        payload_model=AuditApplicationModify,
        category=EventCategory.AUDIT,
        display_name="Application modified",
        description="Published when an application is modified.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.AUDIT_APPLICATION_DELETE: EventMetadata(
        routing_key=RoutingKeys.AUDIT_APPLICATION_DELETE,
        payload_model=AuditApplicationDelete,
        category=EventCategory.AUDIT,
        display_name="Application deleted",
        description="Published when an application is deleted.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.AUDIT_SERVICE_CREATE: EventMetadata(
        routing_key=RoutingKeys.AUDIT_SERVICE_CREATE,
        payload_model=AuditServiceCreate,
        category=EventCategory.AUDIT,
        display_name="Service created",
        description="Published when a service is created.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.AUDIT_SERVICE_MODIFY: EventMetadata(
        routing_key=RoutingKeys.AUDIT_SERVICE_MODIFY,
        payload_model=AuditServiceModify,
        category=EventCategory.AUDIT,
        display_name="Service modified",
        description="Published when a service is modified.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.AUDIT_SERVICE_DELETE: EventMetadata(
        routing_key=RoutingKeys.AUDIT_SERVICE_DELETE,
        payload_model=AuditServiceDelete,
        category=EventCategory.AUDIT,
        display_name="Service deleted",
        description="Published when a service is deleted.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.AUDIT_ENVIRONMENT_CREATE: EventMetadata(
        routing_key=RoutingKeys.AUDIT_ENVIRONMENT_CREATE,
        payload_model=AuditEnvironmentCreate,
        category=EventCategory.AUDIT,
        display_name="Environment created",
        description="Published when an environment is created.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.AUDIT_ENVIRONMENT_MODIFY: EventMetadata(
        routing_key=RoutingKeys.AUDIT_ENVIRONMENT_MODIFY,
        payload_model=AuditEnvironmentModify,
        category=EventCategory.AUDIT,
        display_name="Environment modified",
        description="Published when an environment is modified.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.AUDIT_ENVIRONMENT_DELETE: EventMetadata(
        routing_key=RoutingKeys.AUDIT_ENVIRONMENT_DELETE,
        payload_model=AuditEnvironmentDelete,
        category=EventCategory.AUDIT,
        display_name="Environment deleted",
        description="Published when an environment is deleted.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.AUDIT_SILENCE_RULE_CREATE: EventMetadata(
        routing_key=RoutingKeys.AUDIT_SILENCE_RULE_CREATE,
        payload_model=AuditSilenceRuleCreate,
        category=EventCategory.AUDIT,
        display_name="Silence rule created",
        description="Published when a silence rule is created.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.AUDIT_SILENCE_RULE_MODIFY: EventMetadata(
        routing_key=RoutingKeys.AUDIT_SILENCE_RULE_MODIFY,
        payload_model=AuditSilenceRuleModify,
        category=EventCategory.AUDIT,
        display_name="Silence rule modified",
        description="Published when a silence rule is modified.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.AUDIT_SILENCE_RULE_DELETE: EventMetadata(
        routing_key=RoutingKeys.AUDIT_SILENCE_RULE_DELETE,
        payload_model=AuditSilenceRuleDelete,
        category=EventCategory.AUDIT,
        display_name="Silence rule deleted",
        description="Published when a silence rule is deleted.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.AUDIT_ESCALATION_CREATE: EventMetadata(
        routing_key=RoutingKeys.AUDIT_ESCALATION_CREATE,
        payload_model=AuditEscalationCreate,
        category=EventCategory.AUDIT,
        display_name="Escalation created",
        description="Published when an escalation chain is created.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.AUDIT_ESCALATION_MODIFY: EventMetadata(
        routing_key=RoutingKeys.AUDIT_ESCALATION_MODIFY,
        payload_model=AuditEscalationModify,
        category=EventCategory.AUDIT,
        display_name="Escalation modified",
        description="Published when an escalation chain is modified.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.AUDIT_ESCALATION_DELETE: EventMetadata(
        routing_key=RoutingKeys.AUDIT_ESCALATION_DELETE,
        payload_model=AuditEscalationDelete,
        category=EventCategory.AUDIT,
        display_name="Escalation deleted",
        description="Published when an escalation chain is deleted.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.AUDIT_ESCALATION_OVERRIDE_CREATE: EventMetadata(
        routing_key=RoutingKeys.AUDIT_ESCALATION_OVERRIDE_CREATE,
        payload_model=AuditEscalationOverrideCreate,
        category=EventCategory.AUDIT,
        display_name="Escalation override created",
        description="Published when an escalation override is created.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.AUDIT_ESCALATION_OVERRIDE_MODIFY: EventMetadata(
        routing_key=RoutingKeys.AUDIT_ESCALATION_OVERRIDE_MODIFY,
        payload_model=AuditEscalationOverrideModify,
        category=EventCategory.AUDIT,
        display_name="Escalation override modified",
        description="Published when an escalation override is modified.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.AUDIT_ESCALATION_OVERRIDE_DELETE: EventMetadata(
        routing_key=RoutingKeys.AUDIT_ESCALATION_OVERRIDE_DELETE,
        payload_model=AuditEscalationOverrideDelete,
        category=EventCategory.AUDIT,
        display_name="Escalation override deleted",
        description="Published when an escalation override is deleted.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.AUDIT_ON_CALL_ROTATION_CREATE: EventMetadata(
        routing_key=RoutingKeys.AUDIT_ON_CALL_ROTATION_CREATE,
        payload_model=AuditOnCallRotationCreate,
        category=EventCategory.AUDIT,
        display_name="On-call rotation created",
        description="Published when an on-call rotation is created.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.AUDIT_ON_CALL_ROTATION_DELETE: EventMetadata(
        routing_key=RoutingKeys.AUDIT_ON_CALL_ROTATION_DELETE,
        payload_model=AuditOnCallRotationDelete,
        category=EventCategory.AUDIT,
        display_name="On-call rotation deleted",
        description="Published when an on-call rotation is deleted.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.AUDIT_ON_CALL_ROTATION_OVERRIDE_CREATE: EventMetadata(
        routing_key=RoutingKeys.AUDIT_ON_CALL_ROTATION_OVERRIDE_CREATE,
        payload_model=AuditOnCallRotationOverrideCreate,
        category=EventCategory.AUDIT,
        display_name="On-call rotation override created",
        description="Published when an on-call rotation override is created.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.AUDIT_ON_CALL_ROTATION_OVERRIDE_DELETE: EventMetadata(
        routing_key=RoutingKeys.AUDIT_ON_CALL_ROTATION_OVERRIDE_DELETE,
        payload_model=AuditOnCallRotationOverrideDelete,
        category=EventCategory.AUDIT,
        display_name="On-call rotation override deleted",
        description="Published when an on-call rotation override is deleted.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.AUDIT_SERVICE_ACL_MODIFY: EventMetadata(
        routing_key=RoutingKeys.AUDIT_SERVICE_ACL_MODIFY,
        payload_model=AuditServiceAclModify,
        category=EventCategory.AUDIT,
        display_name="Service ACL modified",
        description="Published when a service's ACL is modified.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),

    # ── Audit: incident_management ───────────────────────────────────────────
    RoutingKeys.AUDIT_INCIDENT_RULE_CREATE: EventMetadata(
        routing_key=RoutingKeys.AUDIT_INCIDENT_RULE_CREATE,
        payload_model=AuditIncidentRuleCreate,
        category=EventCategory.AUDIT,
        display_name="Incident rule created",
        description="Published when an incident rule is created.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.AUDIT_INCIDENT_RULE_MODIFY: EventMetadata(
        routing_key=RoutingKeys.AUDIT_INCIDENT_RULE_MODIFY,
        payload_model=AuditIncidentRuleModify,
        category=EventCategory.AUDIT,
        display_name="Incident rule modified",
        description="Published when an incident rule is modified.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.AUDIT_INCIDENT_RULE_DELETE: EventMetadata(
        routing_key=RoutingKeys.AUDIT_INCIDENT_RULE_DELETE,
        payload_model=AuditIncidentRuleDelete,
        category=EventCategory.AUDIT,
        display_name="Incident rule deleted",
        description="Published when an incident rule is deleted.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),

    # ── Audit: connection_management ─────────────────────────────────────────
    RoutingKeys.AUDIT_CONNECTION_CREATE: EventMetadata(
        routing_key=RoutingKeys.AUDIT_CONNECTION_CREATE,
        payload_model=AuditConnectionCreate,
        category=EventCategory.AUDIT,
        display_name="Connection created",
        description="Published when a connection is created.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.AUDIT_CONNECTION_MODIFY: EventMetadata(
        routing_key=RoutingKeys.AUDIT_CONNECTION_MODIFY,
        payload_model=AuditConnectionModify,
        category=EventCategory.AUDIT,
        display_name="Connection modified",
        description="Published when a connection is modified.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.AUDIT_CONNECTION_DELETE: EventMetadata(
        routing_key=RoutingKeys.AUDIT_CONNECTION_DELETE,
        payload_model=AuditConnectionDelete,
        category=EventCategory.AUDIT,
        display_name="Connection deleted",
        description="Published when a connection is deleted.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.AUDIT_CONNECTION_TEMPLATE_CREATE: EventMetadata(
        routing_key=RoutingKeys.AUDIT_CONNECTION_TEMPLATE_CREATE,
        payload_model=AuditConnectionTemplateCreate,
        category=EventCategory.AUDIT,
        display_name="Connection template created",
        description="Published when a connection template is created.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.AUDIT_CONNECTION_TEMPLATE_MODIFY: EventMetadata(
        routing_key=RoutingKeys.AUDIT_CONNECTION_TEMPLATE_MODIFY,
        payload_model=AuditConnectionTemplateModify,
        category=EventCategory.AUDIT,
        display_name="Connection template modified",
        description="Published when a connection template is modified.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.AUDIT_CONNECTION_TEMPLATE_DELETE: EventMetadata(
        routing_key=RoutingKeys.AUDIT_CONNECTION_TEMPLATE_DELETE,
        payload_model=AuditConnectionTemplateDelete,
        category=EventCategory.AUDIT,
        display_name="Connection template deleted",
        description="Published when a connection template is deleted.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),

    # ------------------------------------------------------------------
    # Audit events — plugin_management
    # ------------------------------------------------------------------
    RoutingKeys.AUDIT_PLUGIN_INSTALL: EventMetadata(
        routing_key=RoutingKeys.AUDIT_PLUGIN_INSTALL,
        payload_model=AuditPluginInstall,
        category=EventCategory.AUDIT,
        display_name="Plugin installed",
        description="Published when a plugin package is installed (disabled by default).",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.AUDIT_PLUGIN_UNINSTALL: EventMetadata(
        routing_key=RoutingKeys.AUDIT_PLUGIN_UNINSTALL,
        payload_model=AuditPluginUninstall,
        category=EventCategory.AUDIT,
        display_name="Plugin uninstalled",
        description="Published when a plugin is uninstalled and removed.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.AUDIT_PLUGIN_ENABLE: EventMetadata(
        routing_key=RoutingKeys.AUDIT_PLUGIN_ENABLE,
        payload_model=AuditPluginEnable,
        category=EventCategory.AUDIT,
        display_name="Plugin enabled",
        description="Published when a plugin is enabled.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.AUDIT_PLUGIN_DISABLE: EventMetadata(
        routing_key=RoutingKeys.AUDIT_PLUGIN_DISABLE,
        payload_model=AuditPluginDisable,
        category=EventCategory.AUDIT,
        display_name="Plugin disabled",
        description="Published when a plugin is disabled.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.AUDIT_PLUGIN_UPDATE: EventMetadata(
        routing_key=RoutingKeys.AUDIT_PLUGIN_UPDATE,
        payload_model=AuditPluginUpdate,
        category=EventCategory.AUDIT,
        display_name="Plugin updated",
        description="Published when a plugin is updated in place to a new version.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.AUDIT_PLUGIN_CONFIG_MODIFY: EventMetadata(
        routing_key=RoutingKeys.AUDIT_PLUGIN_CONFIG_MODIFY,
        payload_model=AuditPluginConfigModify,
        category=EventCategory.AUDIT,
        display_name="Plugin config modified",
        description="Published when a plugin's config is changed at any scope (secrets redacted).",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.AUDIT_PLUGIN_RULE_CREATE: EventMetadata(
        routing_key=RoutingKeys.AUDIT_PLUGIN_RULE_CREATE,
        payload_model=AuditPluginRuleCreate,
        category=EventCategory.AUDIT,
        display_name="Plugin rule created",
        description="Published when a user-configured plugin event-reaction rule is created.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.AUDIT_PLUGIN_RULE_MODIFY: EventMetadata(
        routing_key=RoutingKeys.AUDIT_PLUGIN_RULE_MODIFY,
        payload_model=AuditPluginRuleModify,
        category=EventCategory.AUDIT,
        display_name="Plugin rule modified",
        description="Published when a user-configured plugin event-reaction rule is modified.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.AUDIT_PLUGIN_RULE_DELETE: EventMetadata(
        routing_key=RoutingKeys.AUDIT_PLUGIN_RULE_DELETE,
        payload_model=AuditPluginRuleDelete,
        category=EventCategory.AUDIT,
        display_name="Plugin rule deleted",
        description="Published when a user-configured plugin event-reaction rule is deleted.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),

    # ------------------------------------------------------------------
    # Security events — usermanagement
    # ------------------------------------------------------------------
    RoutingKeys.SECURITY_LOGIN_SUCCESS: EventMetadata(
        routing_key=RoutingKeys.SECURITY_LOGIN_SUCCESS,
        payload_model=SecurityLoginSuccess,
        category=EventCategory.SECURITY,
        display_name="Login succeeded",
        description="Published when a user or service account authenticates successfully.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.SECURITY_LOGIN_FAILED: EventMetadata(
        routing_key=RoutingKeys.SECURITY_LOGIN_FAILED,
        payload_model=SecurityLoginFailed,
        category=EventCategory.SECURITY,
        display_name="Login failed",
        description="Published when an authentication attempt fails.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.SECURITY_PASSWORD_CHANGE: EventMetadata(
        routing_key=RoutingKeys.SECURITY_PASSWORD_CHANGE,
        payload_model=SecurityPasswordChange,
        category=EventCategory.SECURITY,
        display_name="Password changed",
        description="Published when a user changes their own password (self-service).",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.SECURITY_PASSWORD_RESET: EventMetadata(
        routing_key=RoutingKeys.SECURITY_PASSWORD_RESET,
        payload_model=SecurityPasswordReset,
        category=EventCategory.SECURITY,
        display_name="Password reset by administrator",
        description="Published when an administrator resets another user's password.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.SECURITY_OWN_PASSWORD_RESET: EventMetadata(
        routing_key=RoutingKeys.SECURITY_OWN_PASSWORD_RESET,
        payload_model=SecurityOwnPasswordReset,
        category=EventCategory.SECURITY,
        display_name="Own password reset",
        description="Published when a user resets their own password via the \"Forgot password\" flow.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
    RoutingKeys.SECURITY_SERVICE_ACCOUNT_TOKEN_ROTATED: EventMetadata(
        routing_key=RoutingKeys.SECURITY_SERVICE_ACCOUNT_TOKEN_ROTATED,
        payload_model=SecurityServiceAccountTokenRotated,
        category=EventCategory.SECURITY,
        display_name="Service account secret rotated",
        description="Published when an administrator rotates a service account's secret.",
        plugin_subscribable=True,
        plugin_publishable=False,
    ),
}
