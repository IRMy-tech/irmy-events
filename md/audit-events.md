# Audit Events

This page documents the canonical payload structure for audit RabbitMQ events published by all IRMy services.

- [What audit events are](#what-audit-events-are)
- [Conventions](#conventions)
  - [Routing keys](#routing-keys)
  - [Common payload skeleton](#common-payload-skeleton)
  - [Context envelopes](#context-envelopes)
- [Actor Envelope](#actor-envelope)
  - [actorType: user](#actortype-user)
  - [actorType: serviceAccount](#actortype-serviceaccount)
  - [actorType: system](#actortype-system)
  - [actorType: idp](#actortype-idp)
- [Shared structures](#shared-structures)
  - [user](#user)
  - [serviceAccount](#serviceaccount)
  - [role](#role)
  - [group](#group)
  - [application](#application)
  - [service](#service)
  - [environment](#environment)
  - [silenceRule](#silencerule)
  - [escalation](#escalation)
  - [onCallRotation](#oncallrotation)
  - [onCallRotationOverride](#oncallrotationoverride)
  - [serviceAcl](#serviceacl)
  - [incidentRule](#incidentrule)
  - [pipelineTree](#pipelinetree)
  - [keyword](#keyword)
  - [connection](#connection)
  - [connectionTemplate](#connectiontemplate)
  - [plugin](#plugin)
  - [pluginConfig](#pluginconfig)
  - [pluginRule](#pluginrule)
- [User Management events](#user-management-events)
  - [audit.user.create](#auditusercreate)
  - [audit.user.modify](#auditusermodify)
  - [audit.user.delete](#audituserdelete)
  - [audit.serviceAccount.create](#auditserviceaccountcreate)
  - [audit.serviceAccount.delete](#auditserviceaccountdelete)
  - [audit.role.create](#auditrolecreate)
  - [audit.role.modify](#auditrolemodify)
  - [audit.role.delete](#auditroledelete)
  - [audit.group.create](#auditgroupcreate)
  - [audit.group.modify](#auditgroupmodify)
  - [audit.group.membersModify](#auditgroupmembersmodify)
  - [audit.group.delete](#auditgroupdelete)
- [Application Management events](#application-management-events)
  - [Context envelopes](#context-envelopes)
  - [audit.application.create](#auditapplicationcreate)
  - [audit.application.modify](#auditapplicationmodify)
  - [audit.application.delete](#auditapplicationdelete)
  - [audit.service.create](#auditservicecreate)
  - [audit.service.modify](#auditservicemodify)
  - [audit.service.delete](#auditservicedelete)
  - [audit.environment.create](#auditenvironmentcreate)
  - [audit.environment.modify](#auditenvironmentmodify)
  - [audit.environment.delete](#auditenvironmentdelete)
  - [audit.silenceRule.create](#auditsilencerulecreate)
  - [audit.silenceRule.modify](#auditsilencerulemodify)
  - [audit.silenceRule.delete](#auditsilenceruledelete)
  - [audit.escalation.create](#auditescalationcreate)
  - [audit.escalation.modify](#auditescalationmodify)
  - [audit.escalation.delete](#auditescalationdelete)
  - [audit.escalationOverride.create](#auditescalationoverridecreate)
  - [audit.escalationOverride.modify](#auditescalationoverridemodify)
  - [audit.escalationOverride.delete](#auditescalationoverridedelete)
  - [audit.onCallRotation.create](#auditoncallrotationcreate)
  - [audit.onCallRotation.delete](#auditoncallrotationdelete)
  - [audit.onCallRotationOverride.create](#auditoncallrotationoverridecreate)
  - [audit.onCallRotationOverride.delete](#auditoncallrotationoverridedelete)
  - [audit.serviceAcl.modify](#auditserviceaclmodify)
- [Incident Management events](#incident-management-events)
  - [Context envelopes](#context-envelopes)
  - [audit.incidentRule.create](#auditincidentrulecreate)
  - [audit.incidentRule.modify](#auditincidentrulemodify)
  - [audit.incidentRule.delete](#auditincidentruledelete)
- [Connection Management events](#connection-management-events)
  - [Context envelopes](#context-envelopes)
  - [audit.connection.create](#auditconnectioncreate)
  - [audit.connection.modify](#auditconnectionmodify)
  - [audit.connection.delete](#auditconnectiondelete)
  - [audit.connectionTemplate.create](#auditconnectiontemplatecreate)
  - [audit.connectionTemplate.modify](#auditconnectiontemplatemodify)
  - [audit.connectionTemplate.delete](#auditconnectiontemplatedelete)
- [Plugin Management events](#plugin-management-events)
  - [Context envelopes](#context-envelopes)
  - [audit.plugin.install](#auditplugininstall)
  - [audit.plugin.uninstall](#auditpluginuninstall)
  - [audit.plugin.enable](#auditpluginenable)
  - [audit.plugin.disable](#auditplugindisable)
  - [audit.plugin.update](#auditpluginupdate)
  - [audit.pluginConfig.modify](#auditpluginconfigmodify)
  - [audit.pluginRule.create](#auditpluginrulecreate)
  - [audit.pluginRule.modify](#auditpluginrulemodify)
  - [audit.pluginRule.delete](#auditpluginruledelete)
- [Quick reference](#quick-reference)
  - [User Management](#user-management)
  - [Application Management](#application-management)
  - [Incident Management](#incident-management)
  - [Connection Management](#connection-management)
  - [Plugin Management](#plugin-management)

## What audit events are

Audit events describe **changes to configuration entities** of the IRMy platform — entities such as Application, Service, Connection, IncidentRule, User, Role, Group, etc. They are not part of the operational workflow (alerts arriving, incidents being acknowledged) — that lives in operational events.

The single question an audit event answers is: **who, when, and how changed a configuration entity?**

Audit events are intended for:

- Compliance trails (who deleted a user, who removed an ACL entry)
- Security investigations
- Forensics and configuration recovery
- Push to external systems (e.g. S3 bucket for long-term retention) via plugins

## Conventions

- RabbitMQ event payloads use **camelCase** for all keys.
- Every event includes an actor envelope (`actorType` + `actorContext`) describing who or what triggered the change.
- All UUIDs are RFC 4122 strings; all timestamps are ISO 8601 in UTC.
- Payloads represent state **at the moment of publication**. Consumers must not assume the underlying entities still exist or have the same values when processing the event.
- `before` and `after` always contain a **full snapshot** of the entity. Consumers compute the diff if needed.

### Routing keys

The routing key shape is `audit.{entity}.{action}` in camelCase, e.g. `audit.user.create`, `audit.group.membersModify`.

### Common payload skeleton

```
{
  "actorType": "user | serviceAccount | system | idp",
  "actorContext": { ... },

  "entity": "string",
  "action": "string",

  "before": { ... } | null,
  "after": { ... } | null,

  "occurredAt": "ISO 8601"
}
```

- `entity` mirrors the entity segment of the routing key (e.g. `user`, `group`).
- `action` mirrors the action segment of the routing key (e.g. `create`, `modify`, `delete`, `membersModify`).
- `before` is `null` for `create`. `after` is `null` for `delete`. Both are present for `modify`.

### Context envelopes

Some audit entities live in a scope that does not fully fit inside the entity itself (e.g. a `silenceRule` belongs to a Service and optionally an Application + Environment). For those events, the payload also includes one or more **context envelopes** at the top level: `service`, `application`, `environment`. These are snapshots of the surrounding scope at the moment of publication. They are present only when relevant to the entity's scope.

## Actor Envelope

Audit events recognise four actor types.

### actorType: `user`

A human user authenticated via HTTP + JWT. The actor context includes the user's current role with the full permission list and the bitmask, so consumers can authorise downstream decisions without an additional lookup.

```
{
  "actorType": "user",
  "actorContext": {
    "id": "UUID",
    "firstName": "string",
    "lastName": "string",
    "email": "string",
    "role": {
      "id": "UUID",
      "name": "string",
      "permissions": ["string"],
      "permissionsBitMask": 0
    }
  }
}
```

### actorType: `serviceAccount`

A non-human caller authenticated via service account JWT. The actor context includes the service account's role in the same expanded form.

```
{
  "actorType": "serviceAccount",
  "actorContext": {
    "id": "UUID",
    "name": "string",
    "role": {
      "id": "UUID",
      "name": "string",
      "permissions": ["string"],
      "permissionsBitMask": 0
    }
  }
}
```

### actorType: `system`

The platform itself, when the audit event was produced by internal logic rather than a direct external request.

```
{
  "actorType": "system",
  "actorContext": {
    "reason": "string"
  }
}
```

`reason` is a short stable identifier of the system trigger.

### actorType: `idp`

An Identity Provider configured in the platform (SAML 2.0 or OIDC) acting on behalf of the federation protocol. Used for JIT (Just-In-Time) provisioning and JIT group/role synchronisation when a user logs in through SSO.

```
{
  "actorType": "idp",
  "actorContext": {
    "id": "UUID",
    "name": "string",
    "protocol": "saml | oidc"
  }
}
```

`id` and `name` reference the configured Identity Provider entity in IRMy.

## Shared structures

### `user`

```
{
  "id": "UUID",
  "firstName": "string",
  "lastName": "string",
  "email": "string",
  "isBlocked": false,
  "role": {
    "id": "UUID",
    "name": "string"
  },
  "groups": [
    { "id": "UUID", "name": "string" }
  ]
}
```

### `serviceAccount`

```
{
  "id": "UUID",
  "name": "string",
  "role": {
    "id": "UUID",
    "name": "string"
  },
  "expirationDate": "ISO 8601 | null"
}
```

### `role`

```
{
  "id": "UUID",
  "name": "string",
  "description": "string",
  "permissions": ["string"],
  "permissionsBitMask": 0
}
```

`permissionsBitMask` is an integer composed of powers of two corresponding to the entries in `permissions`.

### `group`

```
{
  "id": "UUID",
  "name": "string",
  "description": "string",
  "members": [
    {
      "id": "UUID",
      "firstName": "string",
      "lastName": "string",
      "email": "string"
    }
  ]
}
```

### `application`

```
{
  "id": "UUID",
  "name": "string",
  "description": "string",
  "tags": {"key": "value"},
  "techOwner": {
    "id": "UUID",
    "firstName": "string",
    "lastName": "string",
    "email": "string"
  },
  "productOwner": {
    "id": "UUID",
    "firstName": "string",
    "lastName": "string",
    "email": "string"
  }
}
```

`techOwner` and `productOwner` are both optional and may be `null`.

### `service`

```
{
  "id": "UUID",
  "name": "string",
  "description": "string",
  "tags": {"key": "value"},
  "techOwner": {
    "id": "UUID",
    "firstName": "string",
    "lastName": "string",
    "email": "string"
  },
  "productOwner": {
    "id": "UUID",
    "firstName": "string",
    "lastName": "string",
    "email": "string"
  }
}
```

`techOwner` and `productOwner` are both optional and may be `null`.

### `environment`

```
{
  "id": "UUID",
  "name": "string",
  "description": "string"
}
```

### `silenceRule`

```
{
  "id": "UUID",
  "name": "string",
  "action": "skipNotification | drop",
  "condition": { ... condition tree ... },
  "enabled": true,
  "order": 1
}
```

`condition` is the full condition tree (`SimpleCondition` / `ComplexCondition`) as stored in the database. The scope of the rule (Service / App / App+Env) is indicated by which context envelopes are present in the payload. `enabled` reflects whether the rule is currently active. `order` is the rule's position in the per-scope evaluation order (starts from 1).

### `escalation`

An escalation is represented as a flat list of steps for the given scope (Service-level or App+Env-level override). There is no top-level policy entity, name, or order field.

```
[
  {
    "delaySeconds": 0,
    "user": {
      "id": "UUID",
      "firstName": "string",
      "lastName": "string",
      "email": "string"
    }
  },
  {
    "delaySeconds": 900,
    "user": { ... }
  }
]
```

Each step targets exactly one user. Groups are not supported as escalation targets. `delaySeconds` is relative to alert creation time.

### `onCallRotation`

```
{
  "id": "UUID",
  "participants": [
    {
      "order": 1,
      "shiftDurationSeconds": 604800,
      "user": {
        "id": "UUID",
        "firstName": "string",
        "lastName": "string",
        "email": "string"
      },
      "group": null
    }
  ],
  "startedAt": "ISO 8601"
}
```

Each participant has either a `user` or a `group` set; the other field is `null`. `shiftDurationSeconds` is per-participant. `order` starts from 1.

Rotations cannot be modified — only created or deleted. There is no `audit.onCallRotation.modify` event.

### `onCallRotationOverride`

```
{
  "id": "UUID",
  "parentRotation": {
    "id": "UUID",
    "participants": [ ... ],
    "startedAt": "ISO 8601"
  },
  "user": {
    "id": "UUID",
    "firstName": "string",
    "lastName": "string",
    "email": "string"
  },
  "group": null,
  "startedAt": "ISO 8601",
  "endedAt": "ISO 8601"
}
```

`parentRotation` is a full snapshot of the on-call rotation that the override is attached to, as it was in the database at the moment of publication. The override targets exactly one participant — either a `user` or a `group` (the other is `null`). Both `startedAt` and `endedAt` are mandatory; overrides cannot be open-ended.

Overrides cannot be modified — only created or deleted. There is no `audit.onCallRotationOverride.modify` event.

### `serviceAcl`

```
{
  "entries": [
    {
      "user": {
        "id": "UUID",
        "firstName": "string",
        "lastName": "string",
        "email": "string"
      },
      "group": null,
      "aclLevel": "Participant | Manager"
    }
  ]
}
```

Each entry has either a `user` or a `group` set; the other field is `null`. `aclLevel` is the ACL-specific level (not to be confused with the user's platform role). The ACL itself always exists for every Service — it is created together with the Service as an empty list. Therefore only `modify` events are published; there is no `create` or `delete` for `serviceAcl`. The `service` context envelope identifies which Service the ACL belongs to.

### `incidentRule`

```
{
  "id": "UUID",
  "name": "string",
  "condition": { ... condition tree ... },
  "incidentSeverity": "critical | high | medium | low",
  "enabled": true,
  "roleAssignments": [
    {
      "roleLabel": "string",
      "assigneeType": "productOwner | techOwner | user | none",
      "user": {
        "id": "UUID",
        "firstName": "string",
        "lastName": "string",
        "email": "string"
      }
    }
  ],
  "createdAt": "ISO 8601"
}
```

A rule defines when an incident should be auto-created in response to alert-driven events. Key fields:

- `condition` — a **synthesised** condition tree (`SimpleCondition` / `ComplexCondition`, same JSON shape as silence rules) that combines the rule's matching inputs into a single auditable expression. It is built as an `and` of:
  - a priority node — `{ "type": "simple", "field": "priority", "operator": "less_or_equal", "value": <minimalAlertPriority> }`;
  - the rule's optional application tag condition, with each field prefixed `application.tags.` ;
  - the rule's optional service tag condition, with each field prefixed `service.tags.` .When only the priority node is present, `condition` is that single simple node rather than an `and` wrapper. The rule fires when this condition evaluates to true against the incoming event payload (e.g. `application.state.alerted`). For example, "priority ≤ 2 AND `application.tags.tier == critical`" is synthesised as:
```
{
  "type": "complex",
  "operator": "and",
  "children": [
    { "type": "simple", "field": "priority", "operator": "less_or_equal", "value": 2 },
    { "type": "simple", "field": "application.tags.tier", "operator": "eq", "value": "critical" }
  ]
}
```
- `incidentSeverity` — the severity assigned to the incident created by this rule.
- `enabled` — whether the rule is active. Flipping this flag is captured as `audit.incidentRule.modify`.
- `roleAssignments` — initial incident roles to be assigned when the rule fires:
  - `roleLabel` is a free-form label drawn from a dynamic dictionary; new labels are added implicitly when first used and are not subject to audit.
  - `assigneeType` selects how the assignee is resolved when the incident is created:
    - `productOwner` / `techOwner` — resolved dynamically from the corresponding owner field of the Service or Application at incident creation time. `user` is `null` for these types.
    - `user` — a specific user is hard-wired into the rule. `user` is the full user snapshot.
    - `none` — no assignee is set for this role.

The rule's scope (`global` / `env` / `app` / `appEnv`) is expressed through the set of context envelopes present in the payload, the same way as for `silenceRule`.

### `pipelineTree`

A pipeline tree is a full JSON snapshot of the pipeline configuration as stored in the database. The detailed shape (nodes, transformations, conditions, terminal assignments) is owned by `connection_management` and not duplicated here.

```
{ "...": "pipeline tree JSON snapshot" }
```

### `keyword`

```
{
  "name": "string",
  "macro": "string"
}
```

### `connection`

```
{
  "id": "UUID",
  "name": "string",
  "description": "string | null",
  "enabled": true,
  "source": "string",
  "template": {
    "id": "UUID",
    "name": "string"
  },
  "pipelines": {
    "open": { "...": "pipelineTree" },
    "close": { "...": "pipelineTree" } | null,
    "update": { "...": "pipelineTree" } | null
  }
}
```

`template` references the template the connection was created from. It is `null` if the template has been deleted (the connection itself keeps living).

`pipelines.open` is always present. `pipelines.close` and `pipelines.update` may be `null` if the connection has no logic for those actions.

### `connectionTemplate`

```
{
  "id": "UUID",
  "name": "string",
  "description": "string | null",
  "source": "string",
  "instruction": "string | null",
  "isBlank": false,
  "pipelines": {
    "open": { "...": "pipelineTree" },
    "close": { "...": "pipelineTree" } | null,
    "update": { "...": "pipelineTree" } | null
  },
  "keywords": [
    { "...": "keyword" }
  ]
}
```

`isBlank: true` identifies the system-level Blank template. The Blank template cannot be deleted, so `audit.connectionTemplate.delete` is never published for it.

### `plugin`

```
{
  "id": "UUID",
  "name": "string",
  "version": "string",
  "displayName": "string",
  "enabled": true,
  "isSystem": false,
  "license": "string | null"
}
```

Full plugin snapshot used as `before` / `after` on the plugin lifecycle events (install / uninstall / enable / disable / update). `isSystem: true` marks a platform-provided plugin (e.g. `email`) that cannot be uninstalled. `enabled` reflects whether the plugin is currently enabled. On `update`, `before`/`after` differ in `version` (and possibly `displayName`/`license` if the new manifest changed them) — `enabled` is preserved across the swap.

On `pluginConfig` events the plugin is instead identified by a lightweight reference (`plugin`) — deliberately **no `version`**, it's operational detail, not audit-worthy anywhere in the plugin domain:

```
{
  "id": "UUID",
  "name": "string"
}
```

### `pluginConfig`

```
{
  "fields": [
    {
      "key": "string",
      "type": "string | text | secret | url | integer | boolean | enum",
      "isSecret": false,
      "isSet": true,
      "value": "any | null"
    }
  ]
}
```

The plugin's **global** config (per-scope service/app/app_env config was retired in the 3.0 rules rework — only global config exists now, so there's no separate scope/context envelope on this event at all). `type` is the field's declared form type from the plugin manifest. **Secrets are never recorded**: for a field with `isSecret: true`, `value` is always `null` and only `isSet` tells whether a secret is stored — so a secret change is visible (`isSet` flips or the field appears) without ever exposing the value.

### `pluginRule`

```
{
  "id": "UUID",
  "owner": "global | service | user",
  "eventDomain": "string",
  "events": ["string, or the literal \"--all--\" sentinel"],
  "conditionTree": {"...": "nested AND/OR condition tree, opaque to the library"},
  "reactionBlocks": [
    {
      "pluginId": "UUID",
      "pluginName": "string",
      "stepOrder": 1,
      "capability": "string",
      "stopOnError": true,
      "fields": {"key": "value"}
    }
  ]
}
```

A user-configured rule: an event (or several, or `--all--` within one domain) plus an optional condition tree, driving an ordered sequence of plugin capability calls (`reactionBlocks`) when it matches. A rule can span **multiple different plugins** — that's why there's no single top-level plugin reference the way `pluginConfig` has one; each block carries its own `pluginId`/`pluginName`. `fields` is safe to record in full: unlike plugin config, a capability's declared fields can never include a secret. The `service` the rule belongs to (present iff `owner: "service"`) is carried as a context envelope on the event — see below. No envelope is carried for `owner: "user"`: only the owning user may ever create, modify, or delete their own rule, so the event's `actorContext` already identifies them unambiguously; nobody, not even a global admin, can act on their behalf.

* * *

## User Management events

### `audit.user.create`

Published when a new user is created.

**Allowed actors:** `user`, `serviceAccount`, `idp` (JIT provisioning on first SSO login).

```
{
  "actorType": "idp",
  "actorContext": {
    "id": "ad000000-1111-2222-3333-444455556666",
    "name": "Okta-prod",
    "protocol": "saml"
  },

  "entity": "user",
  "action": "create",

  "before": null,
  "after": {
    "id": "33333333-3333-3333-3333-333333333333",
    "firstName": "Ivan",
    "lastName": "Petrenko",
    "email": "ivan@example.com",
    "isBlocked": false,
    "role": {
      "id": "aaaa1111-bbbb-2222-cccc-3333dddd4444",
      "name": "Engineer"
    },
    "groups": [
      { "id": "bbbb2222-cccc-3333-dddd-4444eeee5555", "name": "Backend" }
    ]
  },

  "occurredAt": "2026-05-18T12:34:56Z"
}
```

### `audit.user.modify`

Published when any field of an existing user is changed. This includes name, email, blocked status (`isBlocked` flip), role change, and group membership change — all from the user's perspective.

**Allowed actors:** `user`, `serviceAccount`, `idp` (JIT group / role sync on subsequent SSO logins).

```
{
  "actorType": "user",
  "actorContext": {
    "id": "99999999-9999-9999-9999-999999999999",
    "firstName": "Olha",
    "lastName": "Kovalenko",
    "email": "olha@example.com",
    "role": {
      "id": "dddd4444-eeee-5555-ffff-6666aaaa7777",
      "name": "Administrator",
      "permissions": [
        "user.read",
        "user.modify",
        "user.delete",
        "role.modify"
      ],
      "permissionsBitMask": 23
    }
  },

  "entity": "user",
  "action": "modify",

  "before": {
    "id": "33333333-3333-3333-3333-333333333333",
    "firstName": "Ivan",
    "lastName": "Petrenko",
    "email": "ivan@example.com",
    "isBlocked": false,
    "role": {
      "id": "aaaa1111-bbbb-2222-cccc-3333dddd4444",
      "name": "Engineer"
    },
    "groups": [
      { "id": "bbbb2222-cccc-3333-dddd-4444eeee5555", "name": "Backend" }
    ]
  },
  "after": {
    "id": "33333333-3333-3333-3333-333333333333",
    "firstName": "Ivan",
    "lastName": "Petrenko",
    "email": "ivan@example.com",
    "isBlocked": false,
    "role": {
      "id": "cccc3333-dddd-4444-eeee-5555ffff6666",
      "name": "Team Lead"
    },
    "groups": [
      { "id": "bbbb2222-cccc-3333-dddd-4444eeee5555", "name": "Backend" }
    ]
  },

  "occurredAt": "2026-05-18T14:00:00Z"
}
```

### `audit.user.delete`

Published when a user is removed.

**Allowed actors:** `user`, `serviceAccount`.

```
{
  "actorType": "user",
  "actorContext": {
    "id": "99999999-9999-9999-9999-999999999999",
    "firstName": "Olha",
    "lastName": "Kovalenko",
    "email": "olha@example.com",
    "role": {
      "id": "dddd4444-eeee-5555-ffff-6666aaaa7777",
      "name": "Administrator",
      "permissions": [
        "user.read",
        "user.modify",
        "user.delete",
        "role.modify"
      ],
      "permissionsBitMask": 23
    }
  },

  "entity": "user",
  "action": "delete",

  "before": {
    "id": "33333333-3333-3333-3333-333333333333",
    "firstName": "Ivan",
    "lastName": "Petrenko",
    "email": "ivan@example.com",
    "isBlocked": false,
    "role": {
      "id": "aaaa1111-bbbb-2222-cccc-3333dddd4444",
      "name": "Engineer"
    },
    "groups": []
  },
  "after": null,

  "occurredAt": "2026-05-20T09:00:00Z"
}
```

* * *

### `audit.serviceAccount.create`

Published when a service account is created.

**Allowed actors:** `user`, `serviceAccount`.

```
{
  "actorType": "user",
  "actorContext": {
    "id": "99999999-9999-9999-9999-999999999999",
    "firstName": "Olha",
    "lastName": "Kovalenko",
    "email": "olha@example.com",
    "role": {
      "id": "dddd4444-eeee-5555-ffff-6666aaaa7777",
      "name": "Administrator",
      "permissions": [
        "user.read",
        "user.modify",
        "user.delete",
        "role.modify"
      ],
      "permissionsBitMask": 23
    }
  },

  "entity": "serviceAccount",
  "action": "create",

  "before": null,
  "after": {
    "id": "5c2a9e0d-9f1b-4e1a-9d6b-2a8c2d8e7b41",
    "name": "datadog-bridge",
    "role": {
      "id": "aaaa1111-bbbb-2222-cccc-3333dddd4444",
      "name": "Integrations"
    },
    "expirationDate": "2027-05-18T00:00:00Z"
  },

  "occurredAt": "2026-05-18T11:00:00Z"
}
```

### `audit.serviceAccount.delete`

Published when a service account is removed.

**Allowed actors:** `user`, `serviceAccount`.

```
{
  "actorType": "user",
  "actorContext": {
    "id": "99999999-9999-9999-9999-999999999999",
    "firstName": "Olha",
    "lastName": "Kovalenko",
    "email": "olha@example.com",
    "role": {
      "id": "dddd4444-eeee-5555-ffff-6666aaaa7777",
      "name": "Administrator",
      "permissions": [
        "user.read",
        "user.modify",
        "user.delete",
        "role.modify"
      ],
      "permissionsBitMask": 23
    }
  },

  "entity": "serviceAccount",
  "action": "delete",

  "before": {
    "id": "5c2a9e0d-9f1b-4e1a-9d6b-2a8c2d8e7b41",
    "name": "datadog-bridge",
    "role": {
      "id": "aaaa1111-bbbb-2222-cccc-3333dddd4444",
      "name": "Integrations"
    },
    "expirationDate": "2027-05-18T00:00:00Z"
  },
  "after": null,

  "occurredAt": "2026-05-20T09:30:00Z"
}
```

* * *

### `audit.role.create`

Published when a role is created.

**Allowed actors:** `user`, `serviceAccount`.

```
{
  "actorType": "user",
  "actorContext": {
    "id": "99999999-9999-9999-9999-999999999999",
    "firstName": "Olha",
    "lastName": "Kovalenko",
    "email": "olha@example.com",
    "role": {
      "id": "dddd4444-eeee-5555-ffff-6666aaaa7777",
      "name": "Administrator",
      "permissions": [
        "user.read",
        "user.modify",
        "user.delete",
        "role.modify"
      ],
      "permissionsBitMask": 23
    }
  },

  "entity": "role",
  "action": "create",

  "before": null,
  "after": {
    "id": "cccc3333-dddd-4444-eeee-5555ffff6666",
    "name": "Team Lead",
    "description": "Lead of an engineering team",
    "permissions": [
      "incident.read",
      "incident.modify",
      "user.read"
    ],
    "permissionsBitMask": 7
  },

  "occurredAt": "2026-05-18T10:00:00Z"
}
```

### `audit.role.modify`

Published when a role is changed.

**Allowed actors:** `user`, `serviceAccount`.

```
{
  "actorType": "user",
  "actorContext": {
    "id": "99999999-9999-9999-9999-999999999999",
    "firstName": "Olha",
    "lastName": "Kovalenko",
    "email": "olha@example.com",
    "role": {
      "id": "dddd4444-eeee-5555-ffff-6666aaaa7777",
      "name": "Administrator",
      "permissions": [
        "user.read",
        "user.modify",
        "user.delete",
        "role.modify"
      ],
      "permissionsBitMask": 23
    }
  },

  "entity": "role",
  "action": "modify",

  "before": {
    "id": "cccc3333-dddd-4444-eeee-5555ffff6666",
    "name": "Team Lead",
    "description": "Lead of an engineering team",
    "permissions": [
      "incident.read",
      "incident.modify",
      "user.read"
    ],
    "permissionsBitMask": 7
  },
  "after": {
    "id": "cccc3333-dddd-4444-eeee-5555ffff6666",
    "name": "Team Lead",
    "description": "Lead of an engineering team — extended permissions",
    "permissions": [
      "incident.read",
      "incident.modify",
      "user.read",
      "user.modify"
    ],
    "permissionsBitMask": 15
  },

  "occurredAt": "2026-05-18T15:30:00Z"
}
```

### `audit.role.delete`

Published when a role is removed.

**Allowed actors:** `user`, `serviceAccount`.

```
{
  "actorType": "user",
  "actorContext": {
    "id": "99999999-9999-9999-9999-999999999999",
    "firstName": "Olha",
    "lastName": "Kovalenko",
    "email": "olha@example.com",
    "role": {
      "id": "dddd4444-eeee-5555-ffff-6666aaaa7777",
      "name": "Administrator",
      "permissions": [
        "user.read",
        "user.modify",
        "user.delete",
        "role.modify"
      ],
      "permissionsBitMask": 23
    }
  },

  "entity": "role",
  "action": "delete",

  "before": {
    "id": "cccc3333-dddd-4444-eeee-5555ffff6666",
    "name": "Team Lead",
    "description": "Lead of an engineering team",
    "permissions": ["incident.read", "incident.modify", "user.read"],
    "permissionsBitMask": 7
  },
  "after": null,

  "occurredAt": "2026-05-20T10:00:00Z"
}
```

* * *

### `audit.group.create`

Published when a group is created.

**Allowed actors:** `user`, `serviceAccount`.

```
{
  "actorType": "user",
  "actorContext": {
    "id": "99999999-9999-9999-9999-999999999999",
    "firstName": "Olha",
    "lastName": "Kovalenko",
    "email": "olha@example.com",
    "role": {
      "id": "dddd4444-eeee-5555-ffff-6666aaaa7777",
      "name": "Administrator",
      "permissions": [
        "user.read",
        "user.modify",
        "user.delete",
        "role.modify"
      ],
      "permissionsBitMask": 23
    }
  },

  "entity": "group",
  "action": "create",

  "before": null,
  "after": {
    "id": "bbbb2222-cccc-3333-dddd-4444eeee5555",
    "name": "Backend",
    "description": "Backend engineers",
    "members": []
  },

  "occurredAt": "2026-05-18T10:30:00Z"
}
```

### `audit.group.modify`

Published when group's name or description changes. Membership changes are published as `audit.group.membersModify`.

**Allowed actors:** `user`, `serviceAccount`.

```
{
  "actorType": "user",
  "actorContext": {
    "id": "99999999-9999-9999-9999-999999999999",
    "firstName": "Olha",
    "lastName": "Kovalenko",
    "email": "olha@example.com",
    "role": {
      "id": "dddd4444-eeee-5555-ffff-6666aaaa7777",
      "name": "Administrator",
      "permissions": [
        "user.read",
        "user.modify",
        "user.delete",
        "role.modify"
      ],
      "permissionsBitMask": 23
    }
  },

  "entity": "group",
  "action": "modify",

  "before": {
    "id": "bbbb2222-cccc-3333-dddd-4444eeee5555",
    "name": "Backend",
    "description": "Backend engineers",
    "members": []
  },
  "after": {
    "id": "bbbb2222-cccc-3333-dddd-4444eeee5555",
    "name": "Backend",
    "description": "Backend engineering team",
    "members": []
  },

  "occurredAt": "2026-05-18T11:30:00Z"
}
```

### `audit.group.membersModify`

Published when membership of a group changes from the group's perspective (admin edited the members list in group settings). Changes from the user's perspective are published as `audit.user.modify`.

**Allowed actors:** `user`, `serviceAccount`.

```
{
  "actorType": "user",
  "actorContext": {
    "id": "99999999-9999-9999-9999-999999999999",
    "firstName": "Olha",
    "lastName": "Kovalenko",
    "email": "olha@example.com",
    "role": {
      "id": "dddd4444-eeee-5555-ffff-6666aaaa7777",
      "name": "Administrator",
      "permissions": [
        "user.read",
        "user.modify",
        "user.delete",
        "role.modify"
      ],
      "permissionsBitMask": 23
    }
  },

  "entity": "group",
  "action": "membersModify",

  "before": {
    "id": "bbbb2222-cccc-3333-dddd-4444eeee5555",
    "name": "Backend",
    "description": "Backend engineers",
    "members": [
      {
        "id": "11111111-2222-3333-4444-555555555555",
        "firstName": "Anna",
        "lastName": "Shevchenko",
        "email": "anna@example.com"
      }
    ]
  },
  "after": {
    "id": "bbbb2222-cccc-3333-dddd-4444eeee5555",
    "name": "Backend",
    "description": "Backend engineers",
    "members": [
      {
        "id": "11111111-2222-3333-4444-555555555555",
        "firstName": "Anna",
        "lastName": "Shevchenko",
        "email": "anna@example.com"
      },
      {
        "id": "33333333-3333-3333-3333-333333333333",
        "firstName": "Ivan",
        "lastName": "Petrenko",
        "email": "ivan@example.com"
      }
    ]
  },

  "occurredAt": "2026-05-18T15:00:00Z"
}
```

### `audit.group.delete`

Published when a group is removed.

**Allowed actors:** `user`, `serviceAccount`.

```
{
  "actorType": "user",
  "actorContext": {
    "id": "99999999-9999-9999-9999-999999999999",
    "firstName": "Olha",
    "lastName": "Kovalenko",
    "email": "olha@example.com",
    "role": {
      "id": "dddd4444-eeee-5555-ffff-6666aaaa7777",
      "name": "Administrator",
      "permissions": [
        "user.read",
        "user.modify",
        "user.delete",
        "role.modify"
      ],
      "permissionsBitMask": 23
    }
  },

  "entity": "group",
  "action": "delete",

  "before": {
    "id": "bbbb2222-cccc-3333-dddd-4444eeee5555",
    "name": "Backend",
    "description": "Backend engineers",
    "members": []
  },
  "after": null,

  "occurredAt": "2026-05-20T11:00:00Z"
}
```

* * *

## Application Management events

These events cover configuration changes inside the `application_management` service: applications, services, environments, silence rules, escalations, on-call rotations and overrides, and service ACLs.

Plugins are not allowed to publish or trigger these events — only `user` and `serviceAccount` actors (with `system` reserved for rare derivative cases).

### Context envelopes

Application management entities live in different scopes. The payload includes one or more of `service`, `application`, `environment` context envelopes depending on the entity. The presence of each envelope expresses the scope of the change:

| Entity | service | application | environment |
| --- | --- | --- | --- |
| `application` | yes | —   | —   |
| `service` | —   | —   | —   |
| `environment` | —   | —   | —   |
| `silenceRule` (Service-level) | yes | —   | —   |
| `silenceRule` (App-level) | yes | yes | —   |
| `silenceRule` (App+Env-level) | yes | yes | yes |
| `escalation` | yes | —   | —   |
| `escalationOverride` | yes | yes | yes |
| `onCallRotation` (Service-level) | yes | —   | —   |
| `onCallRotation` (App+Env-level) | yes | yes | yes |
| `onCallRotationOverride` (Service-level) | yes | —   | —   |
| `onCallRotationOverride` (App+Env-level) | yes | yes | yes |
| `serviceAcl` | yes | —   | —   |

When a context envelope is present, it carries the snapshot of the surrounding entity at the moment of publication.

* * *

### `audit.application.create`

Published when a new application is created.

**Allowed actors:** `user`, `serviceAccount`.

```
{
  "actorType": "user",
  "actorContext": {
    "id": "99999999-9999-9999-9999-999999999999",
    "firstName": "Olha",
    "lastName": "Kovalenko",
    "email": "olha@example.com",
    "role": {
      "id": "dddd4444-eeee-5555-ffff-6666aaaa7777",
      "name": "Administrator",
      "permissions": ["application.create", "application.modify", "application.delete"],
      "permissionsBitMask": 7
    }
  },

  "entity": "application",
  "action": "create",

  "service": {
    "id": "22222222-2222-2222-2222-222222222222",
    "name": "Billing",
    "description": "Billing-related services",
    "tags": {"audience": "customer-facing"},
    "techOwner": null,
    "productOwner": null
  },

  "before": null,
  "after": {
    "id": "11111111-1111-1111-1111-111111111111",
    "name": "billing-api",
    "description": "Billing public API",
    "tags": {"env": "production", "tier": "critical"},
    "techOwner": {
      "id": "33333333-3333-3333-3333-333333333333",
      "firstName": "Ivan",
      "lastName": "Petrenko",
      "email": "ivan@example.com"
    },
    "productOwner": null
  },

  "occurredAt": "2026-05-18T10:00:00Z"
}
```

### `audit.application.modify`

Published when an application's name, description, tags, or owners change.

When the change is a **per-(app, env) owner override** — i.e. the application's tech/product owners are set for a specific Environment, overriding the Service-level roles for that app on that env — the payload additionally includes an `environment` context envelope identifying that Environment. In that case `before`/`after` carry the application snapshot whose `techOwner`/`productOwner` reflect the override values for that env (before and after the change). The `environment` envelope is absent for plain service-level application modifications.

**Allowed actors:** `user`, `serviceAccount`.

```
{
  "actorType": "user",
  "actorContext": { "...": "user actor envelope" },

  "entity": "application",
  "action": "modify",

  "service": {
    "id": "22222222-2222-2222-2222-222222222222",
    "name": "Billing",
    "description": "Billing-related services",
    "tags": {"audience": "customer-facing"},
    "techOwner": null,
    "productOwner": null
  },

  "before": {
    "id": "11111111-1111-1111-1111-111111111111",
    "name": "billing-api",
    "description": "Billing public API",
    "tags": {"env": "production"},
    "techOwner": null,
    "productOwner": null
  },
  "after": {
    "id": "11111111-1111-1111-1111-111111111111",
    "name": "billing-api",
    "description": "Billing public API (handles invoicing and refunds)",
    "tags": {"env": "production", "tier": "critical"},
    "techOwner": {
      "id": "33333333-3333-3333-3333-333333333333",
      "firstName": "Ivan",
      "lastName": "Petrenko",
      "email": "ivan@example.com"
    },
    "productOwner": null
  },

  "occurredAt": "2026-05-18T15:00:00Z"
}
```

### `audit.application.delete`

Published when an application is removed.

**Allowed actors:** `user`, `serviceAccount`.

```
{
  "actorType": "user",
  "actorContext": { "...": "user actor envelope" },

  "entity": "application",
  "action": "delete",

  "service": {
    "id": "22222222-2222-2222-2222-222222222222",
    "name": "Billing",
    "description": "Billing-related services",
    "tags": {"audience": "customer-facing"},
    "techOwner": null,
    "productOwner": null
  },

  "before": {
    "id": "11111111-1111-1111-1111-111111111111",
    "name": "billing-api",
    "description": "Billing public API",
    "tags": {"env": "production", "tier": "critical"},
    "techOwner": null,
    "productOwner": null
  },
  "after": null,

  "occurredAt": "2026-05-20T12:00:00Z"
}
```

* * *

### `audit.service.create`

Published when a service is created.

**Allowed actors:** `user`, `serviceAccount`.

```
{
  "actorType": "user",
  "actorContext": { "...": "user actor envelope" },

  "entity": "service",
  "action": "create",

  "before": null,
  "after": {
    "id": "22222222-2222-2222-2222-222222222222",
    "name": "Billing",
    "description": "Billing-related services",
    "tags": {"audience": "customer-facing"},
    "techOwner": null,
    "productOwner": null
  },

  "occurredAt": "2026-05-18T09:00:00Z"
}
```

### `audit.service.modify`

Published when a service's name, description, tags, or owners change.

**Allowed actors:** `user`, `serviceAccount`.

```
{
  "actorType": "user",
  "actorContext": { "...": "user actor envelope" },

  "entity": "service",
  "action": "modify",

  "before": {
    "id": "22222222-2222-2222-2222-222222222222",
    "name": "Billing",
    "description": "Billing-related services",
    "tags": {"audience": "customer-facing"},
    "techOwner": null,
    "productOwner": null
  },
  "after": {
    "id": "22222222-2222-2222-2222-222222222222",
    "name": "Billing",
    "description": "Billing — invoicing, refunds, payments",
    "tags": {"audience": "customer-facing", "tier": "critical"},
    "techOwner": {
      "id": "33333333-3333-3333-3333-333333333333",
      "firstName": "Ivan",
      "lastName": "Petrenko",
      "email": "ivan@example.com"
    },
    "productOwner": null
  },

  "occurredAt": "2026-05-18T16:00:00Z"
}
```

### `audit.service.delete`

Published when a service is removed.

**Allowed actors:** `user`, `serviceAccount`.

```
{
  "actorType": "user",
  "actorContext": { "...": "user actor envelope" },

  "entity": "service",
  "action": "delete",

  "before": {
    "id": "22222222-2222-2222-2222-222222222222",
    "name": "Billing",
    "description": "Billing-related services",
    "tags": {"audience": "customer-facing"},
    "techOwner": null,
    "productOwner": null
  },
  "after": null,

  "occurredAt": "2026-05-20T13:00:00Z"
}
```

* * *

### `audit.environment.create`

Published when an environment is created.

**Allowed actors:** `user`, `serviceAccount`.

```
{
  "actorType": "user",
  "actorContext": { "...": "user actor envelope" },

  "entity": "environment",
  "action": "create",

  "before": null,
  "after": {
    "id": "44444444-4444-4444-4444-444444444444",
    "name": "production",
    "description": "Production environment serving live traffic"
  },

  "occurredAt": "2026-05-18T08:00:00Z"
}
```

### `audit.environment.modify`

Published when an environment's name or description changes.

**Allowed actors:** `user`, `serviceAccount`.

```
{
  "actorType": "user",
  "actorContext": { "...": "user actor envelope" },

  "entity": "environment",
  "action": "modify",

  "before": {
    "id": "44444444-4444-4444-4444-444444444444",
    "name": "production",
    "description": "Production"
  },
  "after": {
    "id": "44444444-4444-4444-4444-444444444444",
    "name": "production",
    "description": "Production environment serving live traffic"
  },

  "occurredAt": "2026-05-18T17:00:00Z"
}
```

### `audit.environment.delete`

Published when an environment is removed.

At least one environment must exist per organization at all times — the platform rejects requests that would leave the organization without any environment. When this rule prevents a deletion, no audit event is published (the deletion did not occur). This event is published only for deletions that actually went through.

**Allowed actors:** `user`, `serviceAccount`.

```
{
  "actorType": "user",
  "actorContext": { "...": "user actor envelope" },

  "entity": "environment",
  "action": "delete",

  "before": {
    "id": "55555555-5555-5555-5555-555555555555",
    "name": "staging",
    "description": "Staging"
  },
  "after": null,

  "occurredAt": "2026-05-20T14:00:00Z"
}
```

* * *

### `audit.silenceRule.create`

Published when a silence rule is created. The scope of the rule (Service / Application / App+Env) is expressed by the set of context envelopes present in the payload.

**Allowed actors:** `user`, `serviceAccount`.

```
{
  "actorType": "user",
  "actorContext": { "...": "user actor envelope" },

  "entity": "silenceRule",
  "action": "create",

  "service": {
    "id": "22222222-2222-2222-2222-222222222222",
    "name": "Billing",
    "description": "Billing-related services",
    "tags": {"audience": "customer-facing"},
    "techOwner": null,
    "productOwner": null
  },
  "application": {
    "id": "11111111-1111-1111-1111-111111111111",
    "name": "billing-api",
    "description": "Billing public API",
    "tags": {"env": "production", "tier": "critical"},
    "techOwner": null,
    "productOwner": null
  },
  "environment": {
    "id": "44444444-4444-4444-4444-444444444444",
    "name": "production",
    "description": "Production"
  },

  "before": null,
  "after": {
    "id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
    "name": "Suppress noisy disk-usage alerts overnight",
    "action": "skipNotification",
    "condition": {
      "type": "complex",
      "operator": "and",
      "children": [
        { "type": "simple", "field": "tags", "operator": "contains", "value": "disk" },
        { "type": "simple", "field": "priority", "operator": "greater_or_equal", "value": 3 }
      ]
    }
  },

  "occurredAt": "2026-05-18T18:00:00Z"
}
```

### `audit.silenceRule.modify`

Published when any field of a silence rule changes — name, action, condition, enabled (toggle), or order.

**Allowed actors:** `user`, `serviceAccount`.

```
{
  "actorType": "user",
  "actorContext": { "...": "user actor envelope" },

  "entity": "silenceRule",
  "action": "modify",

  "service": { "...": "service snapshot" },
  "application": { "...": "application snapshot" },
  "environment": { "...": "environment snapshot" },

  "before": {
    "id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
    "name": "Suppress noisy disk-usage alerts overnight",
    "action": "skipNotification",
    "condition": {
      "type": "simple",
      "field": "tags",
      "operator": "contains",
      "value": "disk"
    }
  },
  "after": {
    "id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
    "name": "Suppress noisy disk-usage alerts overnight",
    "action": "drop",
    "condition": {
      "type": "simple",
      "field": "tags",
      "operator": "contains",
      "value": "disk"
    }
  },

  "occurredAt": "2026-05-19T09:00:00Z"
}
```

### `audit.silenceRule.delete`

Published when a silence rule is removed.

**Allowed actors:** `user`, `serviceAccount`.

```
{
  "actorType": "user",
  "actorContext": { "...": "user actor envelope" },

  "entity": "silenceRule",
  "action": "delete",

  "service": { "...": "service snapshot" },
  "application": { "...": "application snapshot" },
  "environment": { "...": "environment snapshot" },

  "before": {
    "id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
    "name": "Suppress noisy disk-usage alerts overnight",
    "action": "skipNotification",
    "condition": { "...": "condition tree" }
  },
  "after": null,

  "occurredAt": "2026-05-20T15:00:00Z"
}
```

* * *

### `audit.escalation.create`

Published when a Service-level escalation policy is created.

**Allowed actors:** `user`, `serviceAccount`.

```
{
  "actorType": "user",
  "actorContext": { "...": "user actor envelope" },

  "entity": "escalation",
  "action": "create",

  "service": {
    "id": "22222222-2222-2222-2222-222222222222",
    "name": "Billing",
    "description": "Billing-related services",
    "tags": {"audience": "customer-facing"},
    "techOwner": null,
    "productOwner": null
  },

  "before": null,
  "after": [
    {
      "delaySeconds": 0,
      "user": {
        "id": "33333333-3333-3333-3333-333333333333",
        "firstName": "Ivan",
        "lastName": "Petrenko",
        "email": "ivan@example.com"
      }
    },
    {
      "delaySeconds": 600,
      "user": {
        "id": "77777777-7777-7777-7777-777777777777",
        "firstName": "Bohdan",
        "lastName": "Lysenko",
        "email": "bohdan@example.com"
      }
    }
  ],

  "occurredAt": "2026-05-18T11:00:00Z"
}
```

### `audit.escalation.modify`

Published when a Service-level escalation policy is changed.

**Allowed actors:** `user`, `serviceAccount`.

```
{
  "actorType": "user",
  "actorContext": { "...": "user actor envelope" },

  "entity": "escalation",
  "action": "modify",

  "service": { "...": "service snapshot" },

  "before": [ { "delaySeconds": 0, "user": { "...": "user ref" } } ],
  "after": [ { "delaySeconds": 0, "user": { "...": "user ref" } }, { "delaySeconds": 600, "user": { "...": "user ref" } } ],

  "occurredAt": "2026-05-18T17:30:00Z"
}
```

### `audit.escalation.delete`

Published when a Service-level escalation policy is removed.

**Allowed actors:** `user`, `serviceAccount`.

```
{
  "actorType": "user",
  "actorContext": { "...": "user actor envelope" },

  "entity": "escalation",
  "action": "delete",

  "service": { "...": "service snapshot" },

  "before": [ { "delaySeconds": 0, "user": { "...": "user ref" } } ],
  "after": null,

  "occurredAt": "2026-05-20T16:00:00Z"
}
```

* * *

### `audit.escalationOverride.create`

Published when an App+Env-level escalation override is created. An override is a fully new escalation that replaces the Service-level policy for the specific App+Env combination.

**Allowed actors:** `user`, `serviceAccount`.

```
{
  "actorType": "user",
  "actorContext": { "...": "user actor envelope" },

  "entity": "escalationOverride",
  "action": "create",

  "service": { "...": "service snapshot" },
  "application": { "...": "application snapshot" },
  "environment": { "...": "environment snapshot" },

  "before": null,
  "after": [
    {
      "delaySeconds": 0,
      "user": {
        "id": "99999999-9999-9999-9999-999999999999",
        "firstName": "Olha",
        "lastName": "Kovalenko",
        "email": "olha@example.com"
      }
    }
  ],

  "occurredAt": "2026-05-18T12:00:00Z"
}
```

### `audit.escalationOverride.modify`

Published when an App+Env-level escalation override is changed.

**Allowed actors:** `user`, `serviceAccount`.

```
{
  "actorType": "user",
  "actorContext": { "...": "user actor envelope" },

  "entity": "escalationOverride",
  "action": "modify",

  "service": { "...": "service snapshot" },
  "application": { "...": "application snapshot" },
  "environment": { "...": "environment snapshot" },

  "before": [ { "delaySeconds": 0, "user": { "...": "user ref" } } ],
  "after": [ { "delaySeconds": 0, "user": { "...": "user ref" } }, { "delaySeconds": 900, "user": { "...": "user ref" } } ],

  "occurredAt": "2026-05-19T10:00:00Z"
}
```

### `audit.escalationOverride.delete`

Published when an App+Env-level escalation override is removed. After deletion, the Service-level escalation applies again for this App+Env.

**Allowed actors:** `user`, `serviceAccount`.

```
{
  "actorType": "user",
  "actorContext": { "...": "user actor envelope" },

  "entity": "escalationOverride",
  "action": "delete",

  "service": { "...": "service snapshot" },
  "application": { "...": "application snapshot" },
  "environment": { "...": "environment snapshot" },

  "before": [ { "delaySeconds": 0, "user": { "...": "user ref" } } ],
  "after": null,

  "occurredAt": "2026-05-20T17:00:00Z"
}
```

* * *

### `audit.onCallRotation.create`

Published when an on-call rotation is created. Rotations may live at Service level or at App+Env level — the scope is expressed via the context envelopes.

Rotations cannot be modified. There is no `audit.onCallRotation.modify` event.

**Allowed actors:** `user`, `serviceAccount`.

```
{
  "actorType": "user",
  "actorContext": { "...": "user actor envelope" },

  "entity": "onCallRotation",
  "action": "create",

  "service": { "...": "service snapshot" },

  "before": null,
  "after": {
    "id": "rrrr1111-2222-3333-4444-555555555555",
    "participants": [
      {
        "order": 1,
        "shiftDurationSeconds": 604800,
        "user": {
          "id": "33333333-3333-3333-3333-333333333333",
          "firstName": "Ivan",
          "lastName": "Petrenko",
          "email": "ivan@example.com"
        },
        "group": null
      },
      {
        "order": 2,
        "shiftDurationSeconds": 604800,
        "user": null,
        "group": {
          "id": "bbbb2222-cccc-3333-dddd-4444eeee5555",
          "name": "Backend"
        }
      }
    ],
    "startedAt": "2026-06-01T00:00:00Z"
  },

  "occurredAt": "2026-05-18T13:00:00Z"
}
```

### `audit.onCallRotation.delete`

Published when an on-call rotation is removed.

**Allowed actors:** `user`, `serviceAccount`.

```
{
  "actorType": "user",
  "actorContext": { "...": "user actor envelope" },

  "entity": "onCallRotation",
  "action": "delete",

  "service": { "...": "service snapshot" },

  "before": { "...": "onCallRotation snapshot" },
  "after": null,

  "occurredAt": "2026-05-20T18:00:00Z"
}
```

* * *

### `audit.onCallRotationOverride.create`

Published when an on-call rotation override is created. The override targets exactly one participant (a `user` or a `group`) and lives at the same scope as its parent rotation. The full snapshot of the parent rotation is embedded in `parentRotation`.

Overrides cannot be modified. There is no `audit.onCallRotationOverride.modify` event.

**Allowed actors:** `user`, `serviceAccount`.

```
{
  "actorType": "user",
  "actorContext": { "...": "user actor envelope" },

  "entity": "onCallRotationOverride",
  "action": "create",

  "service": { "...": "service snapshot" },

  "before": null,
  "after": {
    "id": "oooo1111-2222-3333-4444-555555555555",
    "parentRotation": {
      "id": "rrrr1111-2222-3333-4444-555555555555",
      "participants": [
        {
          "order": 1,
          "shiftDurationSeconds": 604800,
          "user": {
            "id": "33333333-3333-3333-3333-333333333333",
            "firstName": "Ivan",
            "lastName": "Petrenko",
            "email": "ivan@example.com"
          },
          "group": null
        }
      ],
      "startedAt": "2026-06-01T00:00:00Z"
    },
    "user": {
      "id": "99999999-9999-9999-9999-999999999999",
      "firstName": "Olha",
      "lastName": "Kovalenko",
      "email": "olha@example.com"
    },
    "group": null,
    "startedAt": "2026-06-10T09:00:00Z",
    "endedAt": "2026-06-15T09:00:00Z"
  },

  "occurredAt": "2026-05-18T14:00:00Z"
}
```

### `audit.onCallRotationOverride.delete`

Published when an on-call rotation override is removed.

**Allowed actors:** `user`, `serviceAccount`.

```
{
  "actorType": "user",
  "actorContext": { "...": "user actor envelope" },

  "entity": "onCallRotationOverride",
  "action": "delete",

  "service": { "...": "service snapshot" },

  "before": { "...": "onCallRotationOverride snapshot" },
  "after": null,

  "occurredAt": "2026-05-20T19:00:00Z"
}
```

* * *

### `audit.serviceAcl.modify`

Published when the ACL of a Service is modified. The ACL itself is created together with the Service as an empty list and exists for the Service's lifetime, so only `modify` is published — there is no `create` or `delete`. The `service` context envelope identifies which Service the ACL belongs to.

**Allowed actors:** `user`, `serviceAccount`.

```
{
  "actorType": "user",
  "actorContext": { "...": "user actor envelope" },

  "entity": "serviceAcl",
  "action": "modify",

  "service": {
    "id": "22222222-2222-2222-2222-222222222222",
    "name": "Billing",
    "description": "Billing-related services",
    "tags": {"audience": "customer-facing"},
    "techOwner": null,
    "productOwner": null
  },

  "before": {
    "entries": [
      {
        "user": {
          "id": "33333333-3333-3333-3333-333333333333",
          "firstName": "Ivan",
          "lastName": "Petrenko",
          "email": "ivan@example.com"
        },
        "group": null,
        "aclLevel": "Participant"
      }
    ]
  },
  "after": {
    "entries": [
      {
        "user": {
          "id": "33333333-3333-3333-3333-333333333333",
          "firstName": "Ivan",
          "lastName": "Petrenko",
          "email": "ivan@example.com"
        },
        "group": null,
        "aclLevel": "Manager"
      },
      {
        "user": null,
        "group": {
          "id": "bbbb2222-cccc-3333-dddd-4444eeee5555",
          "name": "Backend"
        },
        "aclLevel": "Participant"
      }
    ]
  },

  "occurredAt": "2026-05-19T11:00:00Z"
}
```

* * *

## Incident Management events

These events cover configuration changes inside the `incident_management` service. The only configuration entity is `IncidentRule` — a rule that automatically creates an incident in response to alert-driven events.

Plugins are not allowed to publish or trigger these events — only `user` and `serviceAccount` actors.

Operational changes to incidents themselves (creation, state transitions, role assignments, comments, postmortem lifecycle, action items) are not audit events; they are published as operational events documented on the Incident Management Events page. Each of those operational events already carries an `actorContext`, which serves as the audit trail for the action.

### Context envelopes

The rule's scope (`global` / `env` / `app` / `appEnv`) is expressed via context envelopes:

| Scope | service | application | environment |
| --- | --- | --- | --- |
| `global` | —   | —   | —   |
| `env` | —   | —   | yes |
| `app` | yes | yes | —   |
| `appEnv` | yes | yes | yes |

* * *

### `audit.incidentRule.create`

Published when an incident rule is created.

**Allowed actors:** `user`, `serviceAccount`.

```
{
  "actorType": "user",
  "actorContext": {
    "id": "99999999-9999-9999-9999-999999999999",
    "firstName": "Olha",
    "lastName": "Kovalenko",
    "email": "olha@example.com",
    "role": {
      "id": "dddd4444-eeee-5555-ffff-6666aaaa7777",
      "name": "Administrator",
      "permissions": [
        "incidentRule.create",
        "incidentRule.modify",
        "incidentRule.delete"
      ],
      "permissionsBitMask": 7
    }
  },

  "entity": "incidentRule",
  "action": "create",

  "service": {
    "id": "22222222-2222-2222-2222-222222222222",
    "name": "Billing",
    "description": "Billing-related services",
    "tags": {"audience": "customer-facing"},
    "techOwner": null,
    "productOwner": null
  },
  "application": {
    "id": "11111111-1111-1111-1111-111111111111",
    "name": "billing-api",
    "description": "Billing public API",
    "tags": {"env": "production", "tier": "critical"},
    "techOwner": null,
    "productOwner": null
  },
  "environment": {
    "id": "44444444-4444-4444-4444-444444444444",
    "name": "production",
    "description": "Production"
  },

  "before": null,
  "after": {
    "id": "iiii1111-2222-3333-4444-555555555555",
    "name": "Auto-create incident for critical billing alerts",
    "condition": {
      "type": "complex",
      "operator": "and",
      "children": [
        { "type": "simple", "field": "priority", "operator": "less_or_equal", "value": 2 },
        { "type": "simple", "field": "application.tags.tier", "operator": "eq", "value": "critical" }
      ]
    },
    "incidentSeverity": "high",
    "enabled": true,
    "roleAssignments": [
      {
        "roleLabel": "incidentCommander",
        "assigneeType": "techOwner",
        "user": null
      },
      {
        "roleLabel": "communicationsLead",
        "assigneeType": "user",
        "user": {
          "id": "33333333-3333-3333-3333-333333333333",
          "firstName": "Ivan",
          "lastName": "Petrenko",
          "email": "ivan@example.com"
        }
      },
      {
        "roleLabel": "scribe",
        "assigneeType": "none",
        "user": null
      }
    ],
    "createdAt": "2026-05-18T19:00:00Z"
  },

  "occurredAt": "2026-05-18T19:00:00Z"
}
```

### `audit.incidentRule.modify`

Published when an incident rule's name, condition, severity, enabled flag, or role assignments change. Toggling `enabled` is captured by this event (not a dedicated routing key).

**Allowed actors:** `user`, `serviceAccount`.

```
{
  "actorType": "user",
  "actorContext": { "...": "user actor envelope" },

  "entity": "incidentRule",
  "action": "modify",

  "service": { "...": "service snapshot" },
  "application": { "...": "application snapshot" },
  "environment": { "...": "environment snapshot" },

  "before": {
    "id": "iiii1111-2222-3333-4444-555555555555",
    "name": "Auto-create incident for critical billing alerts",
    "condition": { "...": "condition tree" },
    "incidentSeverity": "high",
    "enabled": true,
    "roleAssignments": [
      {
        "roleLabel": "incidentCommander",
        "assigneeType": "techOwner",
        "user": null
      }
    ],
    "createdAt": "2026-05-18T19:00:00Z"
  },
  "after": {
    "id": "iiii1111-2222-3333-4444-555555555555",
    "name": "Auto-create incident for critical billing alerts",
    "condition": { "...": "condition tree" },
    "incidentSeverity": "critical",
    "enabled": false,
    "roleAssignments": [
      {
        "roleLabel": "incidentCommander",
        "assigneeType": "techOwner",
        "user": null
      },
      {
        "roleLabel": "scribe",
        "assigneeType": "productOwner",
        "user": null
      }
    ],
    "createdAt": "2026-05-18T19:00:00Z"
  },

  "occurredAt": "2026-05-19T13:00:00Z"
}
```

### `audit.incidentRule.delete`

Published when an incident rule is removed.

**Allowed actors:** `user`, `serviceAccount`.

```
{
  "actorType": "user",
  "actorContext": { "...": "user actor envelope" },

  "entity": "incidentRule",
  "action": "delete",

  "service": { "...": "service snapshot" },
  "application": { "...": "application snapshot" },
  "environment": { "...": "environment snapshot" },

  "before": { "...": "incidentRule snapshot" },
  "after": null,

  "occurredAt": "2026-05-20T20:00:00Z"
}
```

* * *

## Connection Management events

These events cover configuration changes inside the `connection_management` service: connections and connection templates.

Plugins are not allowed to publish or trigger these events — only `user` and `serviceAccount` actors.

Operational events related to alert routing (e.g. an alert that did not match any pipeline branch and was dropped) are not audit events; they will be documented on the Connection management Events page.

### Context envelopes

Connections and connection templates are organisation-scoped and do not live inside a `service` / `application` / `environment` scope. The payloads do not include any context envelopes — `before` and `after` carry the full snapshot of the entity itself.

### `audit.connection.create`

Published when a new connection is created.

**Allowed actors:** `user`, `serviceAccount`.

```
{
  "actorType": "user",
  "actorContext": {
    "id": "99999999-9999-9999-9999-999999999999",
    "firstName": "Olha",
    "lastName": "Kovalenko",
    "email": "olha@example.com",
    "role": {
      "id": "dddd4444-eeee-5555-ffff-6666aaaa7777",
      "name": "Administrator",
      "permissions": ["WriteConnectionsApplicationsEnvironments"],
      "permissionsBitMask": 2
    }
  },

  "entity": "connection",
  "action": "create",

  "before": null,
  "after": {
    "id": "cccc1111-2222-3333-4444-555555555555",
    "name": "Datadog production webhooks",
    "description": "Production Datadog alerts pipeline",
    "enabled": true,
    "source": "datadog",
    "template": {
      "id": "tttt1111-2222-3333-4444-555555555555",
      "name": "Datadog default"
    },
    "pipelines": {
      "open": { "...": "pipelineTree snapshot" },
      "close": { "...": "pipelineTree snapshot" },
      "update": null
    }
  },

  "occurredAt": "2026-05-25T10:00:00Z"
}
```

### `audit.connection.modify`

Published when any field of a connection is changed: name, description, source, the referenced template, the pipeline trees (open / close / update), or the `enabled` flag. Toggling `enabled` is captured by this event (not a dedicated routing key).

**Allowed actors:** `user`, `serviceAccount`.

```
{
  "actorType": "user",
  "actorContext": { "...": "user actor envelope" },

  "entity": "connection",
  "action": "modify",

  "before": {
    "id": "cccc1111-2222-3333-4444-555555555555",
    "name": "Datadog production webhooks",
    "description": "Production Datadog alerts pipeline",
    "enabled": true,
    "source": "datadog",
    "template": {
      "id": "tttt1111-2222-3333-4444-555555555555",
      "name": "Datadog default"
    },
    "pipelines": { "...": "pipeline trees" }
  },
  "after": {
    "id": "cccc1111-2222-3333-4444-555555555555",
    "name": "Datadog production webhooks",
    "description": "Production Datadog alerts pipeline",
    "enabled": false,
    "source": "datadog",
    "template": {
      "id": "tttt1111-2222-3333-4444-555555555555",
      "name": "Datadog default"
    },
    "pipelines": { "...": "pipeline trees" }
  },

  "occurredAt": "2026-05-25T11:30:00Z"
}
```

### `audit.connection.delete`

Published when a connection is removed.

**Allowed actors:** `user`, `serviceAccount`.

```
{
  "actorType": "user",
  "actorContext": { "...": "user actor envelope" },

  "entity": "connection",
  "action": "delete",

  "before": { "...": "connection snapshot" },
  "after": null,

  "occurredAt": "2026-05-25T12:00:00Z"
}
```

* * *

### `audit.connectionTemplate.create`

Published when a new connection template is created. This includes YAML import (no dedicated routing key for imports — the resulting created template is published as a normal `create`).

The Blank template is provisioned by the platform itself during initial setup and does not produce this event.

**Allowed actors:** `user`, `serviceAccount`.

```
{
  "actorType": "user",
  "actorContext": { "...": "user actor envelope" },

  "entity": "connectionTemplate",
  "action": "create",

  "before": null,
  "after": {
    "id": "tttt2222-3333-4444-5555-666666666666",
    "name": "Custom Prometheus alerts",
    "description": "Tailored Prometheus webhook pipeline",
    "source": "prometheus",
    "instruction": "Configure Alertmanager with webhook_url=...",
    "isBlank": false,
    "pipelines": {
      "open": { "...": "pipelineTree snapshot" },
      "close": null,
      "update": null
    },
    "keywords": [
      { "name": "mySubject", "macro": "$?.get('Body').get('annotations').get('summary')" },
      { "name": "myPriority", "macro": "$?.get('Body').get('labels').get('severity')" }
    ]
  },

  "occurredAt": "2026-05-25T13:00:00Z"
}
```

### `audit.connectionTemplate.modify`

Published when any field of a connection template is changed: name, description, source, instruction, pipeline trees, or keywords.

**Allowed actors:** `user`, `serviceAccount`.

```
{
  "actorType": "user",
  "actorContext": { "...": "user actor envelope" },

  "entity": "connectionTemplate",
  "action": "modify",

  "before": { "...": "connectionTemplate snapshot before changes" },
  "after": { "...": "connectionTemplate snapshot after changes" },

  "occurredAt": "2026-05-25T14:00:00Z"
}
```

### `audit.connectionTemplate.delete`

Published when a connection template is removed. Never published for the Blank template (it cannot be deleted).

YAML export is a read-only operation and does not produce any audit event.

**Allowed actors:** `user`, `serviceAccount`.

```
{
  "actorType": "user",
  "actorContext": { "...": "user actor envelope" },

  "entity": "connectionTemplate",
  "action": "delete",

  "before": { "...": "connectionTemplate snapshot" },
  "after": null,

  "occurredAt": "2026-05-25T15:00:00Z"
}
```

* * *

## Plugin Management events

These events cover configuration changes inside the `plugin_management` service: the plugin lifecycle (install / uninstall / enable / disable / update), plugin config at any scope, and user-configured reaction rows.

Lifecycle and global config are admin operations (`WritePlugins`); rules are authorized by global perms (`owner: "global"`), the service-manager ACL (`owner: "service"`), or by the owning user themselves and nobody else (`owner: "user"`). Plugins are not allowed to publish these events — only `user` and `serviceAccount` actors.

Two conventions specific to this service:

- **Lifecycle uses discrete action verbs**, not `create` / `modify` / `delete`: `install`, `uninstall`, `enable`, `disable`, `update`. A plugin package is installed and registered, not "created"; enable/disable/update are distinct auditable actions a consumer can bind to directly. `update` is an in-place version swap (same plugin `id`), not a config-style `modify` — it's its own lifecycle verb, same family as install/uninstall.
- **Secrets are never recorded.** Config `before` / `after` snapshots redact every secret field to `value: null` (see [pluginConfig](#pluginconfig)); a rule's `reactionBlocks[].fields` needs no such redaction — a plugin capability's declared fields can never include a secret field in the first place.

### Context envelopes

Plugins themselves are organisation-scoped, so lifecycle events carry no context envelopes. `pluginConfig` events carry none either — only global config exists (per-scope config was retired in the 3.0 rules rework). `pluginRule` events carry a `service` envelope iff the rule's `owner` is `"service"` — no envelope at all for `owner: "global"` or `owner: "user"` (a user-owned rule's `actorContext` already identifies the owner, since only that user may ever touch it):

| Entity | service |
| --- | --- |
| `plugin` (install / uninstall / enable / disable / update) | — |
| `pluginConfig` (modify) | — |
| `pluginRule` (owner: global) | — |
| `pluginRule` (owner: service) | yes |
| `pluginRule` (owner: user) | — |

`pluginConfig` events additionally carry a top-level `plugin` reference (`id`, `name` — deliberately no `version`) identifying which plugin the change belongs to. `pluginRule` events carry **no** top-level plugin reference — a rule's `reactionBlocks` can span multiple different plugins, so each block in the snapshot carries its own `pluginId`/`pluginName` instead.

* * *

### `audit.plugin.install`

Published when a plugin package is installed. The plugin is registered **disabled** by default.

**Allowed actors:** `user`, `serviceAccount`.

```
{
  "actorType": "user",
  "actorContext": { "...": "user actor envelope" },

  "entity": "plugin",
  "action": "install",

  "before": null,
  "after": {
    "id": "pppp1111-2222-3333-4444-555555555555",
    "name": "slack",
    "version": "2.1.0",
    "displayName": "Slack",
    "enabled": false,
    "isSystem": false,
    "license": "MIT"
  },

  "occurredAt": "2026-08-09T10:00:00Z"
}
```

### `audit.plugin.uninstall`

Published when a plugin is uninstalled and removed. System plugins cannot be uninstalled.

**Allowed actors:** `user`, `serviceAccount`.

```
{
  "actorType": "user",
  "actorContext": { "...": "user actor envelope" },

  "entity": "plugin",
  "action": "uninstall",

  "before": {
    "id": "pppp1111-2222-3333-4444-555555555555",
    "name": "slack",
    "version": "2.1.0",
    "displayName": "Slack",
    "enabled": false,
    "isSystem": false,
    "license": "MIT"
  },
  "after": null,

  "occurredAt": "2026-08-09T12:00:00Z"
}
```

### `audit.plugin.enable`

Published when a plugin is enabled.

**Allowed actors:** `user`, `serviceAccount`.

```
{
  "actorType": "user",
  "actorContext": { "...": "user actor envelope" },

  "entity": "plugin",
  "action": "enable",

  "before": {
    "id": "pppp1111-2222-3333-4444-555555555555",
    "name": "slack",
    "version": "2.1.0",
    "displayName": "Slack",
    "enabled": false,
    "isSystem": false,
    "license": "MIT"
  },
  "after": {
    "id": "pppp1111-2222-3333-4444-555555555555",
    "name": "slack",
    "version": "2.1.0",
    "displayName": "Slack",
    "enabled": true,
    "isSystem": false,
    "license": "MIT"
  },

  "occurredAt": "2026-08-09T10:05:00Z"
}
```

### `audit.plugin.disable`

Published when a plugin is disabled. Same shape as `audit.plugin.enable` with `enabled` flipping from `true` to `false`.

**Allowed actors:** `user`, `serviceAccount`.

### `audit.plugin.update`

Published when a plugin is updated in place to a new version (same plugin `id` — not an uninstall + install). `before`/`after` differ in `version`, and possibly `displayName`/`license` if the new manifest's metadata changed; `enabled` is preserved across the swap.

**Allowed actors:** `user`, `serviceAccount`.

```
{
  "actorType": "user",
  "actorContext": { "...": "user actor envelope" },

  "entity": "plugin",
  "action": "update",

  "before": {
    "id": "pppp1111-2222-3333-4444-555555555555",
    "name": "slack",
    "version": "2.1.0",
    "displayName": "Slack",
    "enabled": true,
    "isSystem": false,
    "license": "MIT"
  },
  "after": {
    "id": "pppp1111-2222-3333-4444-555555555555",
    "name": "slack",
    "version": "2.2.0",
    "displayName": "Slack",
    "enabled": true,
    "isSystem": false,
    "license": "MIT"
  },

  "occurredAt": "2026-08-16T10:00:00Z"
}
```

### `audit.pluginConfig.modify`

Published when a plugin's config is changed at any scope. `scope` is one of `global` / `service` / `app` / `app_env`; the matching context envelopes are present per the table above. Secret fields are redacted in `before` / `after`.

**Allowed actors:** `user`, `serviceAccount`.

```
{
  "actorType": "user",
  "actorContext": { "...": "user actor envelope" },

  "entity": "pluginConfig",
  "action": "modify",

  "plugin": {
    "id": "pppp1111-2222-3333-4444-555555555555",
    "name": "slack",
    "version": "2.1.0"
  },
  "scope": "app_env",
  "service": { "...": "service snapshot" },
  "application": { "...": "application snapshot" },
  "environment": { "...": "environment snapshot" },

  "before": {
    "fields": [
      { "key": "channel", "type": "string", "isSecret": false, "isSet": true, "value": "#alerts" },
      { "key": "token", "type": "secret", "isSecret": true, "isSet": false, "value": null }
    ]
  },
  "after": {
    "fields": [
      { "key": "channel", "type": "string", "isSecret": false, "isSet": true, "value": "#ops" },
      { "key": "token", "type": "secret", "isSecret": true, "isSet": true, "value": null }
    ]
  },

  "occurredAt": "2026-08-09T11:00:00Z"
}
```

### `audit.pluginRule.create`

Published when a user-configured rule is created. `service` is present iff `owner: "service"` — omitted entirely for `owner: "global"` and `owner: "user"`.

**Allowed actors:** `user`, `serviceAccount`.

```
{
  "actorType": "user",
  "actorContext": { "...": "user actor envelope" },

  "entity": "pluginRule",
  "action": "create",

  "service": { "...": "service snapshot" },

  "before": null,
  "after": {
    "id": "rrrr1111-2222-3333-4444-555555555555",
    "owner": "service",
    "eventDomain": "incident",
    "events": ["incident.created"],
    "conditionTree": {
      "type": "group", "op": "AND",
      "children": [
        {"type": "condition", "field": "incident.severity", "operator": "=", "value": "critical"}
      ]
    },
    "reactionBlocks": [
      {
        "pluginId": "pppp1111-2222-3333-4444-555555555555",
        "pluginName": "slack",
        "stepOrder": 1,
        "capability": "send_message",
        "stopOnError": true,
        "fields": { "channel": "#incidents-critical", "message_template": "Critical incident {{incident.title}} just opened" }
      },
      {
        "pluginId": "jjjj1111-2222-3333-4444-555555555555",
        "pluginName": "jira",
        "stepOrder": 1,
        "capability": "create_ticket",
        "stopOnError": false,
        "fields": { "project_key": "INC", "issue_type": "Task" }
      }
    ]
  },

  "occurredAt": "2026-08-09T11:30:00Z"
}
```

Note `stepOrder: 1` on **both** blocks here — order is per-plugin (each plugin's own sub-sequence), not a single global ordering across the whole rule. Slack and Jira run independently and in parallel; a rule with two Slack blocks would have `stepOrder: 1` and `stepOrder: 2` on those two, run in sequence.

### `audit.pluginRule.modify`

Published when a rule's events, condition, or reaction blocks change. Always a **full** before/after snapshot of the whole rule, same convention as everywhere else in this domain — not a diff.

**Allowed actors:** `user`, `serviceAccount`.

```
{
  "actorType": "user",
  "actorContext": { "...": "user actor envelope" },

  "entity": "pluginRule",
  "action": "modify",

  "service": { "...": "service snapshot" },

  "before": { "...": "full pluginRule snapshot, as above" },
  "after": { "...": "full pluginRule snapshot, as above" },

  "occurredAt": "2026-08-09T12:30:00Z"
}
```

### `audit.pluginRule.delete`

Published when a rule is removed.

**Allowed actors:** `user`, `serviceAccount`.

```
{
  "actorType": "user",
  "actorContext": { "...": "user actor envelope" },

  "entity": "pluginRule",
  "action": "delete",

  "service": { "...": "service snapshot" },

  "before": { "...": "full pluginRule snapshot" },
  "after": null,

  "occurredAt": "2026-08-09T13:00:00Z"
}
```

* * *

## Quick reference

### User Management

| Routing key | Allowed actors |
| --- | --- |
| `audit.user.create` | user, serviceAccount, idp |
| `audit.user.modify` | user, serviceAccount, idp |
| `audit.user.delete` | user, serviceAccount |
| `audit.serviceAccount.create` | user, serviceAccount |
| `audit.serviceAccount.delete` | user, serviceAccount |
| `audit.role.create` | user, serviceAccount |
| `audit.role.modify` | user, serviceAccount |
| `audit.role.delete` | user, serviceAccount |
| `audit.group.create` | user, serviceAccount |
| `audit.group.modify` | user, serviceAccount |
| `audit.group.membersModify` | user, serviceAccount |
| `audit.group.delete` | user, serviceAccount |

### Application Management

| Routing key | Allowed actors |
| --- | --- |
| `audit.application.create` | user, serviceAccount |
| `audit.application.modify` | user, serviceAccount |
| `audit.application.delete` | user, serviceAccount |
| `audit.service.create` | user, serviceAccount |
| `audit.service.modify` | user, serviceAccount |
| `audit.service.delete` | user, serviceAccount |
| `audit.environment.create` | user, serviceAccount |
| `audit.environment.modify` | user, serviceAccount |
| `audit.environment.delete` | user, serviceAccount |
| `audit.silenceRule.create` | user, serviceAccount |
| `audit.silenceRule.modify` | user, serviceAccount |
| `audit.silenceRule.delete` | user, serviceAccount |
| `audit.escalation.create` | user, serviceAccount |
| `audit.escalation.modify` | user, serviceAccount |
| `audit.escalation.delete` | user, serviceAccount |
| `audit.escalationOverride.create` | user, serviceAccount |
| `audit.escalationOverride.modify` | user, serviceAccount |
| `audit.escalationOverride.delete` | user, serviceAccount |
| `audit.onCallRotation.create` | user, serviceAccount |
| `audit.onCallRotation.delete` | user, serviceAccount |
| `audit.onCallRotationOverride.create` | user, serviceAccount |
| `audit.onCallRotationOverride.delete` | user, serviceAccount |
| `audit.serviceAcl.modify` | user, serviceAccount |

### Incident Management

| Routing key | Allowed actors |
| --- | --- |
| `audit.incidentRule.create` | user, serviceAccount |
| `audit.incidentRule.modify` | user, serviceAccount |
| `audit.incidentRule.delete` | user, serviceAccount |

### Connection Management

| Routing key | Allowed actors |
| --- | --- |
| `audit.connection.create` | user, serviceAccount |
| `audit.connection.modify` | user, serviceAccount |
| `audit.connection.delete` | user, serviceAccount |
| `audit.connectionTemplate.create` | user, serviceAccount |
| `audit.connectionTemplate.modify` | user, serviceAccount |
| `audit.connectionTemplate.delete` | user, serviceAccount |

### Plugin Management

| Routing key | Allowed actors |
| --- | --- |
| `audit.plugin.install` | user, serviceAccount |
| `audit.plugin.uninstall` | user, serviceAccount |
| `audit.plugin.enable` | user, serviceAccount |
| `audit.plugin.disable` | user, serviceAccount |
| `audit.plugin.update` | user, serviceAccount |
| `audit.pluginConfig.modify` | user, serviceAccount |
| `audit.pluginRule.create` | user, serviceAccount |
| `audit.pluginRule.modify` | user, serviceAccount |
| `audit.pluginRule.delete` | user, serviceAccount |