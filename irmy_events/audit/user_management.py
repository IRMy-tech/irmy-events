from typing import Literal
from .base import AuditEventBase
from .snapshots import (
    AuditUserSnapshot,
    AuditServiceAccountSnapshot,
    AuditRoleSnapshot,
    AuditGroupSnapshot,
)


class AuditUserCreate(AuditEventBase):
    entity: Literal["user"]
    action: Literal["create"]
    before: None
    after: AuditUserSnapshot


class AuditUserModify(AuditEventBase):
    entity: Literal["user"]
    action: Literal["modify"]
    before: AuditUserSnapshot
    after: AuditUserSnapshot


class AuditUserDelete(AuditEventBase):
    entity: Literal["user"]
    action: Literal["delete"]
    before: AuditUserSnapshot
    after: None


class AuditServiceAccountCreate(AuditEventBase):
    entity: Literal["serviceAccount"]
    action: Literal["create"]
    before: None
    after: AuditServiceAccountSnapshot


class AuditServiceAccountDelete(AuditEventBase):
    entity: Literal["serviceAccount"]
    action: Literal["delete"]
    before: AuditServiceAccountSnapshot
    after: None


class AuditRoleCreate(AuditEventBase):
    entity: Literal["role"]
    action: Literal["create"]
    before: None
    after: AuditRoleSnapshot


class AuditRoleModify(AuditEventBase):
    entity: Literal["role"]
    action: Literal["modify"]
    before: AuditRoleSnapshot
    after: AuditRoleSnapshot


class AuditRoleDelete(AuditEventBase):
    entity: Literal["role"]
    action: Literal["delete"]
    before: AuditRoleSnapshot
    after: None


class AuditGroupCreate(AuditEventBase):
    entity: Literal["group"]
    action: Literal["create"]
    before: None
    after: AuditGroupSnapshot


class AuditGroupModify(AuditEventBase):
    entity: Literal["group"]
    action: Literal["modify"]
    before: AuditGroupSnapshot
    after: AuditGroupSnapshot


class AuditGroupMembersModify(AuditEventBase):
    entity: Literal["group"]
    action: Literal["membersModify"]
    before: AuditGroupSnapshot
    after: AuditGroupSnapshot


class AuditGroupDelete(AuditEventBase):
    entity: Literal["group"]
    action: Literal["delete"]
    before: AuditGroupSnapshot
    after: None
