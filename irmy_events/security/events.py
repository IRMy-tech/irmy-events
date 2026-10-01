from typing import Literal
from .base import SecurityEventBase
from .snapshots import (
    FailureReason,
    SecurityLoginEventData,
    SecurityEmptyEventData,
    SecurityTargetUserEventData,
    SecurityTargetServiceAccountEventData,
)


class SecurityLoginSuccess(SecurityEventBase):
    """security.login.success -- a principal authenticated successfully."""

    event: Literal["login.success"]
    eventData: SecurityLoginEventData
    failureReason: Literal[None] = None


class SecurityLoginFailed(SecurityEventBase):
    """security.login.failed -- authentication failed. `failureReason`
    identifies why; `principal` identifying fields are null when the
    platform could not resolve a matching user/service account, and
    populated with the matched identity when the login was rejected for
    another reason (blocked, soft-deleted, wrong password)."""

    event: Literal["login.failed"]
    eventData: SecurityLoginEventData
    failureReason: FailureReason


class SecurityPasswordChange(SecurityEventBase):
    """security.passwordChange -- a user changes their own password
    (self-service). `principal` is the user performing the change."""

    event: Literal["passwordChange"]
    eventData: SecurityEmptyEventData
    failureReason: Literal[None] = None


class SecurityPasswordReset(SecurityEventBase):
    """security.passwordReset -- an administrator resets another user's
    password. `principal` is the administrator; `eventData.targetUser` is
    the user whose password was reset."""

    event: Literal["passwordReset"]
    eventData: SecurityTargetUserEventData
    failureReason: Literal[None] = None


class SecurityOwnPasswordReset(SecurityEventBase):
    """security.ownPasswordReset -- a user resets their own password via the
    unauthenticated "Forgot password" flow. `principal.type` is always
    `system` since there is no authenticated actor to attribute the action
    to; `eventData.targetUser` is the user whose password was reset."""

    event: Literal["ownPasswordReset"]
    eventData: SecurityTargetUserEventData
    failureReason: Literal[None] = None


class SecurityServiceAccountTokenRotated(SecurityEventBase):
    """security.serviceAccount.tokenRotated -- an administrator rotates a
    service account's secret; the old secret is invalidated. `principal` is
    the administrator; `eventData.targetServiceAccount` identifies the
    service account whose secret was rotated."""

    event: Literal["serviceAccount.tokenRotated"]
    eventData: SecurityTargetServiceAccountEventData
    failureReason: Literal[None] = None
