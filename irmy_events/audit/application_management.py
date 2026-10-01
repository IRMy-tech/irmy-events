from typing import Literal, Optional
from .base import AuditEventBase
from .snapshots import (
    AuditApplicationSnapshot,
    AuditServiceSnapshot,
    AuditEnvironmentSnapshot,
    AuditSilenceRuleSnapshot,
    AuditEscalationStepSnapshot,
    AuditOnCallRotationSnapshot,
    AuditOnCallRotationOverrideSnapshot,
    AuditServiceAclSnapshot,
)


class AuditApplicationCreate(AuditEventBase):
    entity: Literal["application"]
    action: Literal["create"]
    service: AuditServiceSnapshot
    before: None
    after: AuditApplicationSnapshot


class AuditApplicationModify(AuditEventBase):
    entity: Literal["application"]
    action: Literal["modify"]
    service: AuditServiceSnapshot
    # Present only for app+env role-override changes; identifies which Environment
    # the per-(app,env) owner override applies to. Absent for service-level app modify.
    environment: Optional[AuditEnvironmentSnapshot] = None
    before: AuditApplicationSnapshot
    after: AuditApplicationSnapshot


class AuditApplicationDelete(AuditEventBase):
    entity: Literal["application"]
    action: Literal["delete"]
    service: AuditServiceSnapshot
    before: AuditApplicationSnapshot
    after: None


class AuditServiceCreate(AuditEventBase):
    entity: Literal["service"]
    action: Literal["create"]
    before: None
    after: AuditServiceSnapshot


class AuditServiceModify(AuditEventBase):
    entity: Literal["service"]
    action: Literal["modify"]
    before: AuditServiceSnapshot
    after: AuditServiceSnapshot


class AuditServiceDelete(AuditEventBase):
    entity: Literal["service"]
    action: Literal["delete"]
    before: AuditServiceSnapshot
    after: None


class AuditEnvironmentCreate(AuditEventBase):
    entity: Literal["environment"]
    action: Literal["create"]
    before: None
    after: AuditEnvironmentSnapshot


class AuditEnvironmentModify(AuditEventBase):
    entity: Literal["environment"]
    action: Literal["modify"]
    before: AuditEnvironmentSnapshot
    after: AuditEnvironmentSnapshot


class AuditEnvironmentDelete(AuditEventBase):
    entity: Literal["environment"]
    action: Literal["delete"]
    before: AuditEnvironmentSnapshot
    after: None


class AuditSilenceRuleCreate(AuditEventBase):
    """Scope expressed by which context envelopes are present:
    global (no envelopes), service-only, service+application, or service+application+environment."""

    entity: Literal["silenceRule"]
    action: Literal["create"]
    service: Optional[AuditServiceSnapshot] = None
    application: Optional[AuditApplicationSnapshot] = None
    environment: Optional[AuditEnvironmentSnapshot] = None
    before: None
    after: AuditSilenceRuleSnapshot


class AuditSilenceRuleModify(AuditEventBase):
    entity: Literal["silenceRule"]
    action: Literal["modify"]
    service: Optional[AuditServiceSnapshot] = None
    application: Optional[AuditApplicationSnapshot] = None
    environment: Optional[AuditEnvironmentSnapshot] = None
    before: AuditSilenceRuleSnapshot
    after: AuditSilenceRuleSnapshot


class AuditSilenceRuleDelete(AuditEventBase):
    entity: Literal["silenceRule"]
    action: Literal["delete"]
    service: Optional[AuditServiceSnapshot] = None
    application: Optional[AuditApplicationSnapshot] = None
    environment: Optional[AuditEnvironmentSnapshot] = None
    before: AuditSilenceRuleSnapshot
    after: None


class AuditEscalationCreate(AuditEventBase):
    """Service-level escalation steps created (replaces all previous steps)."""

    entity: Literal["escalation"]
    action: Literal["create"]
    service: AuditServiceSnapshot
    before: None
    after: list[AuditEscalationStepSnapshot]


class AuditEscalationModify(AuditEventBase):
    entity: Literal["escalation"]
    action: Literal["modify"]
    service: AuditServiceSnapshot
    before: list[AuditEscalationStepSnapshot]
    after: list[AuditEscalationStepSnapshot]


class AuditEscalationDelete(AuditEventBase):
    entity: Literal["escalation"]
    action: Literal["delete"]
    service: AuditServiceSnapshot
    before: list[AuditEscalationStepSnapshot]
    after: None


class AuditEscalationOverrideCreate(AuditEventBase):
    """App+Env-level escalation override steps created (replaces all previous steps)."""

    entity: Literal["escalationOverride"]
    action: Literal["create"]
    service: AuditServiceSnapshot
    application: AuditApplicationSnapshot
    environment: AuditEnvironmentSnapshot
    before: None
    after: list[AuditEscalationStepSnapshot]


class AuditEscalationOverrideModify(AuditEventBase):
    entity: Literal["escalationOverride"]
    action: Literal["modify"]
    service: AuditServiceSnapshot
    application: AuditApplicationSnapshot
    environment: AuditEnvironmentSnapshot
    before: list[AuditEscalationStepSnapshot]
    after: list[AuditEscalationStepSnapshot]


class AuditEscalationOverrideDelete(AuditEventBase):
    entity: Literal["escalationOverride"]
    action: Literal["delete"]
    service: AuditServiceSnapshot
    application: AuditApplicationSnapshot
    environment: AuditEnvironmentSnapshot
    before: list[AuditEscalationStepSnapshot]
    after: None


class AuditOnCallRotationCreate(AuditEventBase):
    """Rotations cannot be modified — only created or deleted."""

    entity: Literal["onCallRotation"]
    action: Literal["create"]
    service: AuditServiceSnapshot
    application: Optional[AuditApplicationSnapshot] = None
    environment: Optional[AuditEnvironmentSnapshot] = None
    before: None
    after: AuditOnCallRotationSnapshot


class AuditOnCallRotationDelete(AuditEventBase):
    entity: Literal["onCallRotation"]
    action: Literal["delete"]
    service: AuditServiceSnapshot
    application: Optional[AuditApplicationSnapshot] = None
    environment: Optional[AuditEnvironmentSnapshot] = None
    before: AuditOnCallRotationSnapshot
    after: None


class AuditOnCallRotationOverrideCreate(AuditEventBase):
    """Overrides cannot be modified — only created or deleted."""

    entity: Literal["onCallRotationOverride"]
    action: Literal["create"]
    service: AuditServiceSnapshot
    application: Optional[AuditApplicationSnapshot] = None
    environment: Optional[AuditEnvironmentSnapshot] = None
    before: None
    after: AuditOnCallRotationOverrideSnapshot


class AuditOnCallRotationOverrideDelete(AuditEventBase):
    entity: Literal["onCallRotationOverride"]
    action: Literal["delete"]
    service: AuditServiceSnapshot
    application: Optional[AuditApplicationSnapshot] = None
    environment: Optional[AuditEnvironmentSnapshot] = None
    before: AuditOnCallRotationOverrideSnapshot
    after: None


class AuditServiceAclModify(AuditEventBase):
    """audit.serviceAcl.modify — only modify is published; create/delete do not exist
    because the ACL is created and destroyed together with the service."""

    entity: Literal["serviceAcl"]
    action: Literal["modify"]
    service: AuditServiceSnapshot
    before: AuditServiceAclSnapshot
    after: AuditServiceAclSnapshot
