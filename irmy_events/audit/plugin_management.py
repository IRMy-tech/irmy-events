from typing import Literal, Optional
from .base import AuditEventBase
from .snapshots import (
    AuditPluginRef,
    AuditPluginSnapshot,
    AuditPluginConfigSnapshot,
    AuditPluginRuleSnapshot,
    AuditServiceSnapshot,
)


# ---------------------------------------------------------------------------
# Plugin lifecycle. Plugins are organisation-scoped: no context envelopes.
# Discrete action verbs (install/uninstall/enable/disable) — a subscriber can
# bind the exact key it cares about instead of diffing before/after.
# ---------------------------------------------------------------------------


class AuditPluginInstall(AuditEventBase):
    """Installing a plugin is not creating one — the package is uploaded and
    registered, disabled by default."""

    entity: Literal["plugin"]
    action: Literal["install"]
    before: None
    after: AuditPluginSnapshot


class AuditPluginUninstall(AuditEventBase):
    entity: Literal["plugin"]
    action: Literal["uninstall"]
    before: AuditPluginSnapshot
    after: None


class AuditPluginEnable(AuditEventBase):
    entity: Literal["plugin"]
    action: Literal["enable"]
    before: AuditPluginSnapshot
    after: AuditPluginSnapshot


class AuditPluginDisable(AuditEventBase):
    entity: Literal["plugin"]
    action: Literal["disable"]
    before: AuditPluginSnapshot
    after: AuditPluginSnapshot


class AuditPluginUpdate(AuditEventBase):
    """In-place version swap (same plugin id) -- not modeled as a config-style
    `modify`, its own verb like install/uninstall. `before`/`after` differ in
    `version` (and whatever else the new manifest changed: displayName,
    license, ...); `enabled` is preserved across the swap."""

    entity: Literal["plugin"]
    action: Literal["update"]
    before: AuditPluginSnapshot
    after: AuditPluginSnapshot


# ---------------------------------------------------------------------------
# Plugin config. Only global config exists (per-scope service/app/app_env
# config was retired in the 3.0 rules rework) -- no scope field, no context
# envelope needed. before/after are the config with secrets redacted.
# ---------------------------------------------------------------------------


class AuditPluginConfigModify(AuditEventBase):
    entity: Literal["pluginConfig"]
    action: Literal["modify"]
    plugin: AuditPluginRef
    before: AuditPluginConfigSnapshot
    after: AuditPluginConfigSnapshot


# ---------------------------------------------------------------------------
# Plugin rules (user-configured event reactions, 3.0) — genuine CRUD.
# No top-level `plugin` ref here (unlike pluginConfig above) -- a rule's
# reactionBlocks can span multiple different plugins, so there is no single
# "the plugin" at the rule level; each block in the snapshot carries its own
# pluginId/pluginName. `owner` on the snapshot says who the rule belongs to;
# the `service` envelope here is present iff owner == "service". No envelope
# for owner == "user" -- only the owning user may ever touch their own rule,
# so actorContext on the event already identifies them unambiguously.
# ---------------------------------------------------------------------------


class AuditPluginRuleCreate(AuditEventBase):
    entity: Literal["pluginRule"]
    action: Literal["create"]
    service: Optional[AuditServiceSnapshot] = None
    before: None
    after: AuditPluginRuleSnapshot


class AuditPluginRuleModify(AuditEventBase):
    entity: Literal["pluginRule"]
    action: Literal["modify"]
    service: Optional[AuditServiceSnapshot] = None
    before: AuditPluginRuleSnapshot
    after: AuditPluginRuleSnapshot


class AuditPluginRuleDelete(AuditEventBase):
    entity: Literal["pluginRule"]
    action: Literal["delete"]
    service: Optional[AuditServiceSnapshot] = None
    before: AuditPluginRuleSnapshot
    after: None
