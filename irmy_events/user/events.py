from datetime import datetime
from typing import Literal
from ..shared.actors import EventBase, ActorContext
from ..shared.refs import UserRef


class UserPasswordResetRequested(EventBase):
    """user.password.resetRequested — self-service forgot-password flow.

    Published when a user restores their own forgotten password. The flow is
    unauthenticated, so actorType is always ``system``.

    ``resetUrl`` is **encrypted** at the field level following the shared Data
    Encryption Conventions (HKDF-SHA256 key + AES-256-GCM, base64(nonce ‖
    ciphertext ‖ tag)); it decrypts to a deep link carrying userId and the
    reset token.
    """

    actorType: Literal["system"]
    actorContext: ActorContext
    user: UserRef
    resetUrl: str
    occurredAt: datetime


class UserPasswordResetInitiated(EventBase):
    """user.password.resetInitiated — admin-initiated password reset.

    Published when an administrator (or a service account) triggers a password
    reset for another user. ``user`` is the target user; the actor is the
    administrator who initiated it.

    ``resetUrl`` is **encrypted** at the field level following the shared Data
    Encryption Conventions (HKDF-SHA256 key + AES-256-GCM, base64(nonce ‖
    ciphertext ‖ tag)); it decrypts to a deep link carrying userId and the
    reset token.
    """

    actorType: Literal["user", "serviceAccount"]
    actorContext: ActorContext
    user: UserRef
    resetUrl: str
    occurredAt: datetime
