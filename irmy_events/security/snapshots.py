from typing import Literal, Optional
from pydantic import BaseModel
from ..shared.refs import UserRef, NamedRef


FailureReason = Literal[
    "invalidCredentials",
    "userNotFound",
    "userBlocked",
    "userDeleted",
    "samlAssertionInvalid",
    "samlAssertionExpired",
    "oidcTokenInvalid",
    "invalidToken",
    "identityProviderNotConfigured",
]


class SecurityIdentityProviderRef(BaseModel):
    """Identifies the Identity Provider used for an SSO login attempt."""

    id: str
    name: str
    protocol: Literal["saml", "oidc"]


class SecurityLoginEventData(BaseModel):
    """eventData for `security.login.success` / `security.login.failed`.

    `identityProvider` is present only for SSO methods (saml/oidc).
    `attemptedTokenPrefix` is present only for service-account
    `login.failed` when no service account matched the supplied secret --
    the first 8 characters of the secret, to support brute-force tracking
    without leaking the full secret.
    """

    identityProvider: Optional[SecurityIdentityProviderRef] = None
    attemptedTokenPrefix: Optional[str] = None


class SecurityEmptyEventData(BaseModel):
    """eventData for events with no event-specific data (e.g. passwordChange)."""


class SecurityTargetUserEventData(BaseModel):
    """eventData for events that operate on a user other than the principal."""

    targetUser: UserRef


class SecurityTargetServiceAccountEventData(BaseModel):
    """eventData for events that operate on a service account."""

    targetServiceAccount: NamedRef
