from typing import Literal
from .base import AuditEventBase
from .snapshots import (
    AuditConnectionSnapshot,
    AuditConnectionTemplateSnapshot,
)


class AuditConnectionCreate(AuditEventBase):
    """Connections are organisation-scoped: no context envelopes."""

    entity: Literal["connection"]
    action: Literal["create"]
    before: None
    after: AuditConnectionSnapshot


class AuditConnectionModify(AuditEventBase):
    """Toggling the enabled flag is captured by this event."""

    entity: Literal["connection"]
    action: Literal["modify"]
    before: AuditConnectionSnapshot
    after: AuditConnectionSnapshot


class AuditConnectionDelete(AuditEventBase):
    entity: Literal["connection"]
    action: Literal["delete"]
    before: AuditConnectionSnapshot
    after: None


class AuditConnectionTemplateCreate(AuditEventBase):
    """YAML import produces this event too. The platform-provisioned Blank
    template does not."""

    entity: Literal["connectionTemplate"]
    action: Literal["create"]
    before: None
    after: AuditConnectionTemplateSnapshot


class AuditConnectionTemplateModify(AuditEventBase):
    entity: Literal["connectionTemplate"]
    action: Literal["modify"]
    before: AuditConnectionTemplateSnapshot
    after: AuditConnectionTemplateSnapshot


class AuditConnectionTemplateDelete(AuditEventBase):
    """Never published for the Blank template — it cannot be deleted."""

    entity: Literal["connectionTemplate"]
    action: Literal["delete"]
    before: AuditConnectionTemplateSnapshot
    after: None
