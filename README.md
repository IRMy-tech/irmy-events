# irmy-events

Shared Pydantic v2 models for all RabbitMQ event payloads in the IRMy platform.

Covers every incoming command, outgoing operational event, and audit event across `application_management`, `incident_management`, `connection_management`, and `user_management`. Intended for use by internal Python services and the public SDK.

---

## Installation

```bash
pip install irmy-events
```

Requires Python 3.12+ and `pydantic` 2.11. The import package is `irmy_events`.

---

## Package layout

```
irmy_events/
├── routing_keys.py          # RoutingKeys — all 112 routing key constants
├── conditions.py            # ConditionTree = dict[str, Any]
│
├── shared/
│   ├── refs.py              # UserRef, NamedRef
│   └── actors.py            # actor context models + EventBase
│
├── alert/
│   ├── snapshots.py         # AlertOpenSnapshot, AlertCloseSnapshot, …
│   ├── commands.py          # AlertCommandCreate, AlertRequestProcess, …
│   └── events.py            # AlertStateOpen, AlertStateClose, …
│
├── application/
│   ├── snapshots.py         # ApplicationSnapshot, ServiceSnapshot, EnvironmentSnapshot
│   └── events.py            # ApplicationStateAlerted, …
│
├── oncall/
│   └── commands.py          # OncallCommandExtend
│
├── scheduler/
│   └── events.py            # SchedulerRequestCreate, SchedulerRequestCancel, …
│
├── user/
│   └── events.py            # UserPasswordResetRequested, UserPasswordResetInitiated
│
├── incident/
│   ├── snapshots.py         # IncidentSnapshot, ActionItemSnapshot
│   ├── commands.py          # IncidentCommand* (9 commands, incl. action items)
│   └── events.py            # IncidentCreated, IncidentState*, IncidentActionItemCreated/Done, …
│
├── postmortem/
│   ├── snapshots.py         # PostmortemSnapshot, PostmortemCompletedSnapshot
│   ├── commands.py          # PostmortemCommand* (2 commands: createDraft, changeState)
│   └── events.py            # PostmortemDraft*, PostmortemState*
│
├── audit/
│   ├── base.py              # AuditEventBase
│   ├── snapshots.py         # full audit snapshots (different from operational ones)
│   ├── user_management.py   # AuditUser*, AuditRole*, AuditGroup*, …
│   ├── application_management.py  # AuditApplication*, AuditSilenceRule*, …
│   ├── incident_management.py     # AuditIncidentRule*
│   ├── connection_management.py   # AuditConnection*, AuditConnectionTemplate*
│   └── plugin_management.py       # AuditPlugin*, AuditPluginConfig*, AuditPluginRule*
│
└── security/
    ├── base.py              # SecurityEventBase, SecurityPrincipal, SecurityRequestContext
    ├── snapshots.py         # SecurityLoginEventData, SecurityTargetUserEventData, …
    └── events.py            # SecurityLoginSuccess, SecurityLoginFailed, …
```

Everything is re-exported from the top-level package, so most imports only need one line.

---

## Quick start

### Deserializing an incoming message

```python
import json
from irmy_events import AlertStateOpen, RoutingKeys

raw = json.loads(message.body)

if message.routing_key == RoutingKeys.ALERT_STATE_OPEN:
    event = AlertStateOpen.model_validate(raw)
    print(event.alert.subject)
    print(event.application.name)
```

### Building and publishing an outgoing event

```python
from datetime import datetime, timezone
from irmy_events import (
    AlertStateOpen, AlertOpenSnapshot, ApplicationSnapshot,
    ServiceSnapshot, EnvironmentSnapshot, PluginActorContext,
)

event = AlertStateOpen(
    actorType="plugin",
    actorContext=PluginActorContext(id="...", name="datadog-bridge"),
    alert=AlertOpenSnapshot(
        id="55555555-...",
        externalAlertId="prometheus-cpu-high-12345",
        subject="High CPU on web-server-01",
        description=None,
        tags=["cpu", "production"],
        priority=2,
        customFields={"region": "us-east-1"},
        createdAt=datetime.now(timezone.utc),
        shouldNotify=True,
        assignedToUser=None,
    ),
    application=ApplicationSnapshot(id="...", name="billing-api", tags=["production"]),
    service=ServiceSnapshot(id="...", name="Billing", tags=[]),
    environment=EnvironmentSnapshot(id="...", name="production"),
)

payload = event.model_dump(mode="json")
```

### Using routing key constants

```python
from irmy_events import RoutingKeys

channel.basic_publish(
    exchange="irmy",
    routing_key=RoutingKeys.ALERT_STATE_OPEN,
    body=event.model_dump_json(),
)
```

---

## Actor envelope

Every event carries `actorType` and `actorContext`. `EventBase` contains a `model_validator` that automatically parses `actorContext` into the correct typed model based on `actorType` — no manual switching required.

| `actorType`      | `actorContext` type          | When used                                        |
|------------------|------------------------------|--------------------------------------------------|
| `user`           | `UserActorContext`           | HTTP request from a logged-in user               |
| `serviceAccount` | `ServiceAccountActorContext` | HTTP request from a service account JWT          |
| `plugin`         | `PluginActorContext`         | Commands from an external plugin                 |
| `system`         | `SystemActorContext`         | Internal platform logic (timers, derivations)    |
| `rule`           | `RuleActorContext`           | `incident.created` triggered by an IncidentRule  |
| `idp`            | `IdpActorContext`            | Audit events: JIT SSO provisioning               |

```python
from irmy_events import AlertStateOpen, UserActorContext, PluginActorContext

event = AlertStateOpen.model_validate(raw)

match event.actorType:
    case "user":
        ctx: UserActorContext = event.actorContext  # type: ignore[assignment]
        print(ctx.email)
    case "plugin":
        ctx: PluginActorContext = event.actorContext  # type: ignore[assignment]
        print(ctx.name)
```

---

## Alert snapshots

The `alert` field shape differs between events. Each variant extends `AlertCoreFields`:

| Snapshot class         | Extra fields                                      | Used in                                                           |
|------------------------|---------------------------------------------------|-------------------------------------------------------------------|
| `AlertOpenSnapshot`    | `shouldNotify`, `assignedToUser`                  | `alert.state.open`, `application.state.alerted`, `alertLevelIncreased`, `incident.created` (`causedByAlert`) |
| `AlertCloseSnapshot`   | `closedAt`, `closeReason`, `assignedToUser`       | `alert.state.close`, `application.state.recovered`, `alertLevelDecreased` |
| `AlertAckSnapshot`     | `acknowledgedAt`, `assignedToUser`                | `alert.state.acknowledge`                                         |
| `AlertUpdateSnapshot`  | `updatedAt`, `shouldNotify`, `assignedToUser`     | `alert.action.update`                                             |
| `AlertAssigneeSnapshot`| `assignedAt`, `previousAssignee`, `newAssignee`   | `alert.assignee.modify`                                           |
| `AlertNoteSnapshot`    | `assignedToUser`                                  | `alert.note.add`                                                  |
| `AlertCommandInput`    | `applicationId`, `environmentId` (no `id`)        | `alert.command.create` (incoming command)                         |

---

## Operational vs audit snapshots

The same entity has **two distinct snapshot shapes** depending on context.

### `ApplicationSnapshot` (operational)

Used in `alert.*`, `application.state.*`, `incident.*`, and `postmortem.*` events. Lightweight — only what consumers need for routing and display.

```python
class ApplicationSnapshot(BaseModel):
    id: str
    name: str
    tags: list[str]
```

### `AuditApplicationSnapshot` (audit)

Used in `audit.application.*` events. Full state for compliance trails.

```python
class AuditApplicationSnapshot(BaseModel):
    id: str
    name: str
    description: str
    tags: list[str]
    techOwner: AuditOwnerRef | None
    productOwner: AuditOwnerRef | None
```

The same distinction applies to `ServiceSnapshot` / `AuditServiceSnapshot` and `EnvironmentSnapshot` / `AuditEnvironmentSnapshot`.

---

## Audit events

Audit events use `AuditEventBase`, which restricts `actorType` to `user | serviceAccount | system | idp` (no `plugin` or `rule`).

`before` and `after` are typed per event class:

```python
from irmy_events import AuditUserCreate, AuditUserSnapshot

event = AuditUserCreate.model_validate(raw)
# event.before is always None for create events
# event.after is AuditUserSnapshot
print(event.after.email)
print(event.occurredAt)
```

Context envelopes (`service`, `application`, `environment`) on audit events express **scope**. Their presence depends on the entity:

| Entity              | `service` | `application` | `environment` |
|---------------------|-----------|---------------|---------------|
| `application`       | always    | —             | —             |
| `service`           | —         | —             | —             |
| `environment`       | —         | —             | —             |
| `silenceRule`       | always    | optional      | optional      |
| `escalation`        | always    | —             | —             |
| `escalationOverride`| always    | always        | always        |
| `onCallRotation`    | always    | optional      | optional      |
| `onCallRotationOverride` | always | optional   | optional      |
| `serviceAcl`        | always    | —             | —             |
| `incidentRule`      | optional  | optional      | optional      |
| `connection`        | —         | —             | —             |
| `connectionTemplate`| —         | —             | —             |

---

## Security events

Security events (`security/`) describe authentication activity and credential operations -- logins, failed logins, password changes/resets, service account secret rotations. They are deliberately **not** audit events: there is no `before`/`after`, each event is a discrete fact rather than a state change of an entity. Full spec: [`md/security-events.md`](md/security-events.md).

```python
from irmy_events import SecurityLoginFailed, RoutingKeys

if message.routing_key == RoutingKeys.SECURITY_LOGIN_FAILED:
    event = SecurityLoginFailed.model_validate(raw)
    print(event.principal.email, event.failureReason)
```

`principal` (`SecurityPrincipal`) is a single flat shape shared by every principal type -- nullability of `id`/`firstName`/`lastName`/`email`/`name` depends on whether the platform could resolve the principal, not on `principal.type` alone. `principal.method` is populated only for `login.*` events.

---

## Scheduler events

`SchedulerRequest*` models do **not** extend `EventBase` — the `scheduler.request` infrastructure contract has no actor envelope. The actor envelope lives inside `sendEvent.eventData` (the callback payload).

```python
from irmy_events import SchedulerRequestCreate, SchedulerSendEvent

request = SchedulerRequestCreate(
    internalScheduleId="escalation-55555555-...",
    action="create",
    scheduleType="oneShot",
    executeAt=1719849600,
    sendEvent=SchedulerSendEvent(
        routingKey="alert.command.reassign",
        eventData={...},  # AlertCommandReassign payload
    ),
)
```

---

## Condition trees

`silenceRule.condition` and `incidentRule.condition` are kept as `dict[str, Any]` (`ConditionTree`). The recursive `SimpleCondition` / `ComplexCondition` structure is defined by the platform and evaluated at runtime; this library does not validate it further.

```python
from irmy_events import ConditionTree

condition: ConditionTree = {
    "type": "complex",
    "operator": "and",
    "children": [
        {"type": "simple", "field": "tags", "operator": "contains", "value": "disk"},
        {"type": "simple", "field": "priority", "operator": "less_or_equal", "value": 2},
    ],
}
```

---

## All routing keys

```python
from irmy_events import RoutingKeys

# Alert commands (incoming to application_management)
RoutingKeys.ALERT_COMMAND_CREATE           # "alert.command.create"
RoutingKeys.ALERT_COMMAND_ACKNOWLEDGE      # "alert.command.acknowledge"
RoutingKeys.ALERT_COMMAND_CLOSE            # "alert.command.close"
RoutingKeys.ALERT_COMMAND_ADD_NOTE         # "alert.command.addNote"
RoutingKeys.ALERT_COMMAND_REASSIGN         # "alert.command.reassign"
RoutingKeys.ALERT_REQUEST_PROCESS          # "alert.request.process"

# Alert events (outgoing from application_management)
RoutingKeys.ALERT_STATE_OPEN               # "alert.state.open"
RoutingKeys.ALERT_STATE_CLOSE              # "alert.state.close"
RoutingKeys.ALERT_STATE_ACKNOWLEDGE        # "alert.state.acknowledge"
RoutingKeys.ALERT_ACTION_UPDATE            # "alert.action.update"
RoutingKeys.ALERT_ASSIGNEE_MODIFY          # "alert.assignee.modify"
RoutingKeys.ALERT_NOTE_ADD                 # "alert.note.add"

# Application state events
RoutingKeys.APPLICATION_STATE_ALERTED                  # "application.state.alerted"
RoutingKeys.APPLICATION_STATE_RECOVERED                # "application.state.recovered"
RoutingKeys.APPLICATION_STATE_ALERT_LEVEL_INCREASED    # "application.state.alertLevelIncreased"
RoutingKeys.APPLICATION_STATE_ALERT_LEVEL_DECREASED    # "application.state.alertLevelDecreased"

# On-call / scheduler
RoutingKeys.ONCALL_COMMAND_EXTEND          # "oncall.command.extend"
RoutingKeys.SCHEDULER_REQUEST              # "scheduler.request"

# Incident commands (incoming to incident_management)
RoutingKeys.INCIDENT_COMMAND_CREATE
RoutingKeys.INCIDENT_COMMAND_UPDATE
RoutingKeys.INCIDENT_COMMAND_CHANGE_SEVERITY
RoutingKeys.INCIDENT_COMMAND_CHANGE_STATE
RoutingKeys.INCIDENT_COMMAND_ASSIGN_ROLE
RoutingKeys.INCIDENT_COMMAND_ADD_PARTICIPANT
RoutingKeys.INCIDENT_COMMAND_ADD_COMMENT
RoutingKeys.INCIDENT_COMMAND_ADD_ACTION_ITEM
RoutingKeys.INCIDENT_COMMAND_COMPLETE_ACTION_ITEM

# Postmortem commands
RoutingKeys.POSTMORTEM_COMMAND_CREATE_DRAFT
RoutingKeys.POSTMORTEM_COMMAND_CHANGE_STATE

# Incident events (outgoing from incident_management)
RoutingKeys.INCIDENT_CREATED
RoutingKeys.INCIDENT_UPDATED
RoutingKeys.INCIDENT_STATE_ACKNOWLEDGED
RoutingKeys.INCIDENT_STATE_INVESTIGATING
RoutingKeys.INCIDENT_STATE_CONFIRMED
RoutingKeys.INCIDENT_STATE_RESOLVED
RoutingKeys.INCIDENT_STATE_CLOSED
RoutingKeys.INCIDENT_STATE_REOPENED
RoutingKeys.INCIDENT_SEVERITY_ESCALATED
RoutingKeys.INCIDENT_SEVERITY_DEESCALATED
RoutingKeys.INCIDENT_ROLE_ASSIGNED
RoutingKeys.INCIDENT_PARTICIPANT_ADDED
RoutingKeys.INCIDENT_COMMENT_ADDED
RoutingKeys.INCIDENT_ACTION_ITEM_CREATED
RoutingKeys.INCIDENT_ACTION_ITEM_DONE

# Postmortem events
RoutingKeys.POSTMORTEM_STATE_SUBMITTED
RoutingKeys.POSTMORTEM_STATE_BACK_TO_DRAFT
RoutingKeys.POSTMORTEM_STATE_APPROVED
RoutingKeys.POSTMORTEM_STATE_COMPLETED

# Audit events — user_management
RoutingKeys.AUDIT_USER_CREATE
RoutingKeys.AUDIT_USER_MODIFY
RoutingKeys.AUDIT_USER_DELETE
RoutingKeys.AUDIT_SERVICE_ACCOUNT_CREATE
RoutingKeys.AUDIT_SERVICE_ACCOUNT_DELETE
RoutingKeys.AUDIT_ROLE_CREATE
RoutingKeys.AUDIT_ROLE_MODIFY
RoutingKeys.AUDIT_ROLE_DELETE
RoutingKeys.AUDIT_GROUP_CREATE
RoutingKeys.AUDIT_GROUP_MODIFY
RoutingKeys.AUDIT_GROUP_MEMBERS_MODIFY
RoutingKeys.AUDIT_GROUP_DELETE

# Audit events — application_management
RoutingKeys.AUDIT_APPLICATION_CREATE
RoutingKeys.AUDIT_APPLICATION_MODIFY
RoutingKeys.AUDIT_APPLICATION_DELETE
RoutingKeys.AUDIT_SERVICE_CREATE
RoutingKeys.AUDIT_SERVICE_MODIFY
RoutingKeys.AUDIT_SERVICE_DELETE
RoutingKeys.AUDIT_ENVIRONMENT_CREATE
RoutingKeys.AUDIT_ENVIRONMENT_MODIFY
RoutingKeys.AUDIT_ENVIRONMENT_DELETE
RoutingKeys.AUDIT_SILENCE_RULE_CREATE
RoutingKeys.AUDIT_SILENCE_RULE_MODIFY
RoutingKeys.AUDIT_SILENCE_RULE_DELETE
RoutingKeys.AUDIT_ESCALATION_CREATE
RoutingKeys.AUDIT_ESCALATION_MODIFY
RoutingKeys.AUDIT_ESCALATION_DELETE
RoutingKeys.AUDIT_ESCALATION_OVERRIDE_CREATE
RoutingKeys.AUDIT_ESCALATION_OVERRIDE_MODIFY
RoutingKeys.AUDIT_ESCALATION_OVERRIDE_DELETE
RoutingKeys.AUDIT_ON_CALL_ROTATION_CREATE
RoutingKeys.AUDIT_ON_CALL_ROTATION_DELETE
RoutingKeys.AUDIT_ON_CALL_ROTATION_OVERRIDE_CREATE
RoutingKeys.AUDIT_ON_CALL_ROTATION_OVERRIDE_DELETE
RoutingKeys.AUDIT_SERVICE_ACL_MODIFY

# Audit events — incident_management
RoutingKeys.AUDIT_INCIDENT_RULE_CREATE
RoutingKeys.AUDIT_INCIDENT_RULE_MODIFY
RoutingKeys.AUDIT_INCIDENT_RULE_DELETE

# Audit events — connection_management
RoutingKeys.AUDIT_CONNECTION_CREATE
RoutingKeys.AUDIT_CONNECTION_MODIFY
RoutingKeys.AUDIT_CONNECTION_DELETE
RoutingKeys.AUDIT_CONNECTION_TEMPLATE_CREATE
RoutingKeys.AUDIT_CONNECTION_TEMPLATE_MODIFY
RoutingKeys.AUDIT_CONNECTION_TEMPLATE_DELETE

# Audit events — plugin_management
RoutingKeys.AUDIT_PLUGIN_INSTALL
RoutingKeys.AUDIT_PLUGIN_UNINSTALL
RoutingKeys.AUDIT_PLUGIN_ENABLE
RoutingKeys.AUDIT_PLUGIN_DISABLE
RoutingKeys.AUDIT_PLUGIN_UPDATE
RoutingKeys.AUDIT_PLUGIN_CONFIG_MODIFY
RoutingKeys.AUDIT_PLUGIN_RULE_CREATE
RoutingKeys.AUDIT_PLUGIN_RULE_MODIFY
RoutingKeys.AUDIT_PLUGIN_RULE_DELETE

# Security events — usermanagement
RoutingKeys.SECURITY_LOGIN_SUCCESS                     # "security.login.success"
RoutingKeys.SECURITY_LOGIN_FAILED                      # "security.login.failed"
RoutingKeys.SECURITY_PASSWORD_CHANGE                   # "security.passwordChange"
RoutingKeys.SECURITY_PASSWORD_RESET                    # "security.passwordReset"
RoutingKeys.SECURITY_OWN_PASSWORD_RESET                # "security.ownPasswordReset"
RoutingKeys.SECURITY_SERVICE_ACCOUNT_TOKEN_ROTATED     # "security.serviceAccount.tokenRotated"
```
