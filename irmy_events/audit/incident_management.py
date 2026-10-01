from typing import Literal, Optional
from .base import AuditEventBase
from .snapshots import (
    AuditServiceSnapshot,
    AuditApplicationSnapshot,
    AuditEnvironmentSnapshot,
    AuditIncidentRuleSnapshot,
)


class AuditIncidentRuleCreate(AuditEventBase):
    """Scope: global (no envelopes), env (environment only),
    app (service+application), app_env (service+application+environment)."""

    entity: Literal["incidentRule"]
    action: Literal["create"]
    service: Optional[AuditServiceSnapshot] = None
    application: Optional[AuditApplicationSnapshot] = None
    environment: Optional[AuditEnvironmentSnapshot] = None
    before: None
    after: AuditIncidentRuleSnapshot


class AuditIncidentRuleModify(AuditEventBase):
    """Toggling the enabled flag is captured by this event."""

    entity: Literal["incidentRule"]
    action: Literal["modify"]
    service: Optional[AuditServiceSnapshot] = None
    application: Optional[AuditApplicationSnapshot] = None
    environment: Optional[AuditEnvironmentSnapshot] = None
    before: AuditIncidentRuleSnapshot
    after: AuditIncidentRuleSnapshot


class AuditIncidentRuleDelete(AuditEventBase):
    entity: Literal["incidentRule"]
    action: Literal["delete"]
    service: Optional[AuditServiceSnapshot] = None
    application: Optional[AuditApplicationSnapshot] = None
    environment: Optional[AuditEnvironmentSnapshot] = None
    before: AuditIncidentRuleSnapshot
    after: None
