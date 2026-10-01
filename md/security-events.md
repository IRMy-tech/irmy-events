# Security Events

This page documents the canonical payload structure for security RabbitMQ events published by IRMy services.

- [What security events are](#what-security-events-are)
- [Conventions](#conventions)
  - [Routing keys](#routing-keys)
  - [Common payload skeleton](#common-payload-skeleton)
- [Principal](#principal)
- [failureReason](#failurereason)
- [security.login.success](#securityloginsuccess)
- [security.login.failed](#securityloginfailed)
- [security.passwordChange](#securitypasswordchange)
- [security.passwordReset](#securitypasswordreset)
- [security.ownPasswordReset](#securityownpasswordreset)
- [security.serviceAccount.tokenRotated](#securityserviceaccounttokenrotated)
- [Quick reference](#quick-reference)

## What security events are

Security events describe **authentication-related activity and credential operations** on the platform. They answer questions such as: who logged in, when, from where, by which method; who tried and failed; who changed or reset a password; who rotated a service account secret.

Security events are intentionally separate from audit events:

- **Audit events** cover changes to configuration entities (Application, Service, User, Role, Group, IncidentRule, etc.). They use `before` / `after` snapshots of an entity.
- **Security events** cover the authentication flow and credential operations. They have no `before` / `after` — each event is a discrete fact, not a state change of an entity.

Security events are intended for:

- Compliance trails (SOC 2, ISO 27001) covering authentication and credential changes
- Security investigations (brute-force attempts, suspicious sign-ins, credential rotations)
- Forensic correlation with audit and operational events

## Conventions

- RabbitMQ event payloads use **camelCase** for all keys.
- All UUIDs are RFC 4122 strings; all timestamps are ISO 8601 in UTC.
- Payloads represent state **at the moment of publication**.

### Routing keys

The routing key shape is `security.{event}` in camelCase, e.g. `security.login.success`, `security.passwordReset`, `security.serviceAccount.tokenRotated`.

### Common payload skeleton

```json
{
  "event": "string",

  "principal": {
    "type": "user | serviceAccount | system",
    "method": "password | saml | oidc | serviceAccountSecret | null",
    "id": "UUID | null",
    "firstName": "string | null",
    "lastName": "string | null",
    "email": "string | null",
    "name": "string | null"
  },

  "requestContext": {
    "ipAddress": "string",
    "userAgent": "string | null"
  },

  "eventData": { "...": "event-specific" },

  "failureReason": "string | null",

  "occurredAt": "ISO 8601"
}
```

- `event` mirrors the event segment of the routing key (e.g. `login.success`, `passwordReset`).
- `principal` identifies who was authenticated, who attempted to authenticate, or who performed a credential operation. See [Principal](#principal).
- `requestContext` captures network-level metadata about the request that produced the event. `ipAddress` is always present; `userAgent` is opportunistic and may be `null` (not every client sends it).
- `eventData` carries event-specific information (identity provider, attempted token prefix, target user / service account, etc.).
- `failureReason` is filled **only** for `login.failed` events; for all other events it is `null`.

## Principal

`principal.type` is always known — the platform routes user-targeted and service-account-targeted authentication through different endpoints, so the type is determined by the endpoint rather than inferred from credentials.

`principal.method` is filled for `login.*` events and `null` for all other events (`passwordChange`, `passwordReset`, `serviceAccount.tokenRotated`). For credential-operation events, the authentication of the actor performing the operation is already represented by their session and does not need to be re-stated in the event.

### type: `user` (successful authentication or authenticated actor)

```json
{
  "type": "user",
  "method": "password | saml | oidc | null",
  "id": "UUID",
  "firstName": "string",
  "lastName": "string",
  "email": "string",
  "name": null
}
```

### type: `serviceAccount` (successful authentication)

```json
{
  "type": "serviceAccount",
  "method": "serviceAccountSecret | null",
  "id": "UUID",
  "firstName": null,
  "lastName": null,
  "email": null,
  "name": "string"
}
```

### Failed authentication where the principal cannot be matched

When authentication fails and the platform cannot resolve the principal to a known user or service account (e.g. the email does not exist, or the SA secret is unknown), identifying fields are `null` while `type` and `method` are still set based on the endpoint and method used.

```json
{
  "type": "user",
  "method": "password",
  "id": null,
  "firstName": null,
  "lastName": null,
  "email": "stranger@example.com",
  "name": null
}
```

For password-based failed login, `email` carries the value the client tried to log in with, even though no user matched. For SA failed login, the attempted secret prefix is surfaced through `eventData.attemptedTokenPrefix` instead.

When the platform **does** match a user but rejects the login for another reason (blocked, soft-deleted, wrong password), `principal` is populated with the matched user's identity. `failureReason` indicates why the login was rejected.

## failureReason

`failureReason` is set only for `security.login.failed`. The platform uses a stable set of values:

| Value | Meaning |
| --- | --- |
| `invalidCredentials` | The supplied password did not match the matched user |
| `userNotFound` | No user exists in the database with the supplied email |
| `userBlocked` | The matched user is currently blocked |
| `userDeleted` | The matched user is soft-deleted |
| `samlAssertionInvalid` | SAML assertion signature/structure could not be validated |
| `samlAssertionExpired` | SAML assertion was outside its validity window |
| `oidcTokenInvalid` | OIDC id_token could not be validated |
| `invalidToken` | The supplied service account secret did not match any service account |
| `identityProviderNotConfigured` | A login attempt referenced an identity provider that does not exist in the platform |

---

## `security.login.success`

Published when a principal authenticates successfully.

**Model:** `SecurityLoginSuccess` (`irmy_events.security`)

### Example — user logging in with password

```json
{
  "event": "login.success",
  "principal": {
    "type": "user",
    "method": "password",
    "id": "33333333-3333-3333-3333-333333333333",
    "firstName": "Ivan",
    "lastName": "Petrenko",
    "email": "ivan@example.com",
    "name": null
  },
  "requestContext": {
    "ipAddress": "203.0.113.42",
    "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4)"
  },
  "eventData": {},
  "failureReason": null,
  "occurredAt": "2026-05-18T09:00:00Z"
}
```

### Example — user logging in via SAML SSO

```json
{
  "event": "login.success",
  "principal": {
    "type": "user",
    "method": "saml",
    "id": "33333333-3333-3333-3333-333333333333",
    "firstName": "Ivan",
    "lastName": "Petrenko",
    "email": "ivan@example.com",
    "name": null
  },
  "requestContext": {
    "ipAddress": "203.0.113.42",
    "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4)"
  },
  "eventData": {
    "identityProvider": {
      "id": "ad000000-1111-2222-3333-444455556666",
      "name": "Okta-prod",
      "protocol": "saml"
    }
  },
  "failureReason": null,
  "occurredAt": "2026-05-18T09:02:00Z"
}
```

### Example — service account exchanging its secret for a JWT

```json
{
  "event": "login.success",
  "principal": {
    "type": "serviceAccount",
    "method": "serviceAccountSecret",
    "id": "5c2a9e0d-9f1b-4e1a-9d6b-2a8c2d8e7b41",
    "firstName": null,
    "lastName": null,
    "email": null,
    "name": "datadog-bridge"
  },
  "requestContext": {
    "ipAddress": "10.0.42.7",
    "userAgent": "datadog-bridge/1.4.0"
  },
  "eventData": {},
  "failureReason": null,
  "occurredAt": "2026-05-18T09:01:23Z"
}
```

---

## `security.login.failed`

Published when authentication fails. `failureReason` identifies why.

**Model:** `SecurityLoginFailed` (`irmy_events.security`)

### Example — wrong password for a known user

```json
{
  "event": "login.failed",
  "principal": {
    "type": "user",
    "method": "password",
    "id": "33333333-3333-3333-3333-333333333333",
    "firstName": "Ivan",
    "lastName": "Petrenko",
    "email": "ivan@example.com",
    "name": null
  },
  "requestContext": {
    "ipAddress": "203.0.113.42",
    "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4)"
  },
  "eventData": {},
  "failureReason": "invalidCredentials",
  "occurredAt": "2026-05-18T09:05:00Z"
}
```

### Example — attempt to log in with an unknown email

```json
{
  "event": "login.failed",
  "principal": {
    "type": "user",
    "method": "password",
    "id": null,
    "firstName": null,
    "lastName": null,
    "email": "stranger@example.com",
    "name": null
  },
  "requestContext": {
    "ipAddress": "198.51.100.7",
    "userAgent": "Mozilla/5.0 (X11; Linux x86_64)"
  },
  "eventData": {},
  "failureReason": "userNotFound",
  "occurredAt": "2026-05-18T09:05:30Z"
}
```

`principal.email` carries the value the client tried to log in with, even though no user matched. `principal.id`, `firstName`, `lastName` are `null`.

### Example — blocked user attempting SAML SSO

```json
{
  "event": "login.failed",
  "principal": {
    "type": "user",
    "method": "saml",
    "id": "33333333-3333-3333-3333-333333333333",
    "firstName": "Ivan",
    "lastName": "Petrenko",
    "email": "ivan@example.com",
    "name": null
  },
  "requestContext": {
    "ipAddress": "203.0.113.42",
    "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4)"
  },
  "eventData": {
    "identityProvider": {
      "id": "ad000000-1111-2222-3333-444455556666",
      "name": "Okta-prod",
      "protocol": "saml"
    }
  },
  "failureReason": "userBlocked",
  "occurredAt": "2026-05-18T09:06:00Z"
}
```

The SAML provider accepted the user, but the platform rejected the login because the matched user is blocked. `principal` is populated with the matched user's identity; `failureReason` indicates why.

### Example — deleted user attempting OIDC SSO

```json
{
  "event": "login.failed",
  "principal": {
    "type": "user",
    "method": "oidc",
    "id": "33333333-3333-3333-3333-333333333333",
    "firstName": "Ivan",
    "lastName": "Petrenko",
    "email": "ivan@example.com",
    "name": null
  },
  "requestContext": {
    "ipAddress": "203.0.113.42",
    "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4)"
  },
  "eventData": {
    "identityProvider": {
      "id": "ad000000-1111-2222-3333-444455556666",
      "name": "Azure AD",
      "protocol": "oidc"
    }
  },
  "failureReason": "userDeleted",
  "occurredAt": "2026-05-18T09:06:30Z"
}
```

### Example — invalid service account secret

```json
{
  "event": "login.failed",
  "principal": {
    "type": "serviceAccount",
    "method": "serviceAccountSecret",
    "id": null,
    "firstName": null,
    "lastName": null,
    "email": null,
    "name": null
  },
  "requestContext": {
    "ipAddress": "203.0.113.99",
    "userAgent": "curl/8.4.0"
  },
  "eventData": {
    "attemptedTokenPrefix": "abc12345"
  },
  "failureReason": "invalidToken",
  "occurredAt": "2026-05-18T09:07:00Z"
}
```

`attemptedTokenPrefix` carries the first 8 characters of the supplied secret to support tracking of brute-force activity without leaking the full secret.

---

## `security.passwordChange`

Published when a user changes their own password (self-service password change). `principal` is the user performing the change.

**Model:** `SecurityPasswordChange` (`irmy_events.security`)

```json
{
  "event": "passwordChange",
  "principal": {
    "type": "user",
    "method": null,
    "id": "33333333-3333-3333-3333-333333333333",
    "firstName": "Ivan",
    "lastName": "Petrenko",
    "email": "ivan@example.com",
    "name": null
  },
  "requestContext": {
    "ipAddress": "203.0.113.42",
    "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4)"
  },
  "eventData": {},
  "failureReason": null,
  "occurredAt": "2026-05-18T10:00:00Z"
}
```

---

## `security.passwordReset`

Published when an administrator resets another user's password. `principal` is the administrator; `eventData.targetUser` is the user whose password was reset.

**Model:** `SecurityPasswordReset` (`irmy_events.security`)

```json
{
  "event": "passwordReset",
  "principal": {
    "type": "user",
    "method": null,
    "id": "99999999-9999-9999-9999-999999999999",
    "firstName": "Olha",
    "lastName": "Kovalenko",
    "email": "olha@example.com",
    "name": null
  },
  "requestContext": {
    "ipAddress": "203.0.113.42",
    "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4)"
  },
  "eventData": {
    "targetUser": {
      "id": "33333333-3333-3333-3333-333333333333",
      "firstName": "Ivan",
      "lastName": "Petrenko",
      "email": "ivan@example.com"
    }
  },
  "failureReason": null,
  "occurredAt": "2026-05-18T10:30:00Z"
}
```

---

## `security.ownPasswordReset`

Published when a user resets their own password within the "Forgot password" mechanism. In this case `principal.type: "system"`, with `method`, `id`, `firstName`, `lastName`, `email` and `name` all `null`.

**Model:** `SecurityOwnPasswordReset` (`irmy_events.security`)

```json
{
  "event": "ownPasswordReset",
  "principal": {
    "type": "system",
    "method": null,
    "id": null,
    "firstName": null,
    "lastName": null,
    "email": null,
    "name": null
  },
  "requestContext": {
    "ipAddress": "203.0.113.42",
    "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4)"
  },
  "eventData": {
    "targetUser": {
      "id": "33333333-3333-3333-3333-333333333333",
      "firstName": "Ivan",
      "lastName": "Petrenko",
      "email": "ivan@example.com"
    }
  },
  "failureReason": null,
  "occurredAt": "2026-05-18T10:30:00Z"
}
```

---

## `security.serviceAccount.tokenRotated`

Published when an administrator rotates a service account's secret. The old secret is invalidated and a new one is issued. `principal` is the administrator; `eventData.targetServiceAccount` identifies the service account whose secret was rotated.

**Model:** `SecurityServiceAccountTokenRotated` (`irmy_events.security`)

```json
{
  "event": "serviceAccount.tokenRotated",
  "principal": {
    "type": "user",
    "method": null,
    "id": "99999999-9999-9999-9999-999999999999",
    "firstName": "Olha",
    "lastName": "Kovalenko",
    "email": "olha@example.com",
    "name": null
  },
  "requestContext": {
    "ipAddress": "203.0.113.42",
    "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4)"
  },
  "eventData": {
    "targetServiceAccount": {
      "id": "5c2a9e0d-9f1b-4e1a-9d6b-2a8c2d8e7b41",
      "name": "datadog-bridge"
    }
  },
  "failureReason": null,
  "occurredAt": "2026-05-18T11:00:00Z"
}
```

---

## Quick reference

| Routing key | When published | Principal | eventData |
| --- | --- | --- | --- |
| `security.login.success` | Authentication succeeded | The authenticated user or service account | `identityProvider` (only for SSO methods) |
| `security.login.failed` | Authentication failed | User or service account (identifying fields `null` when no match; populated with matched identity when login was rejected for blocked/deleted user or wrong password) | `identityProvider` (for SSO), `attemptedTokenPrefix` (for service accounts when no match) |
| `security.passwordChange` | A user changed their own password | The user changing the password | `{}` |
| `security.passwordReset` | An administrator reset another user's password | The administrator | `targetUser` |
| `security.ownPasswordReset` | A user reset their own password within the "Forgot password" mechanism | System | `targetUser` |
| `security.serviceAccount.tokenRotated` | An administrator rotated a service account's secret | The administrator | `targetServiceAccount` |
