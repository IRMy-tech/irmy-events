from enum import Enum


class RoutingKeys(str, Enum):
    # ------------------------------------------------------------------
    # Alert commands — incoming to application_management
    # ------------------------------------------------------------------
    ALERT_COMMAND_CREATE = "alert.command.create"
    ALERT_COMMAND_ACKNOWLEDGE = "alert.command.acknowledge"
    ALERT_COMMAND_CLOSE = "alert.command.close"
    ALERT_COMMAND_ADD_NOTE = "alert.command.addNote"
    ALERT_COMMAND_REASSIGN = "alert.command.reassign"
    ALERT_REQUEST_PROCESS = "alert.request.process"

    # ------------------------------------------------------------------
    # Alert events — outgoing from application_management
    # ------------------------------------------------------------------
    ALERT_STATE_OPEN = "alert.state.open"
    ALERT_STATE_CLOSE = "alert.state.close"
    ALERT_STATE_ACKNOWLEDGE = "alert.state.acknowledge"
    ALERT_ACTION_UPDATE = "alert.action.update"
    ALERT_ASSIGNEE_MODIFY = "alert.assignee.modify"
    ALERT_NOTE_ADD = "alert.note.add"

    # ------------------------------------------------------------------
    # Application state events — outgoing from application_management
    # ------------------------------------------------------------------
    APPLICATION_STATE_ALERTED = "application.state.alerted"
    APPLICATION_STATE_RECOVERED = "application.state.recovered"
    APPLICATION_STATE_ALERT_LEVEL_INCREASED = "application.state.alertLevelIncreased"
    APPLICATION_STATE_ALERT_LEVEL_DECREASED = "application.state.alertLevelDecreased"

    # ------------------------------------------------------------------
    # On-call commands
    # ------------------------------------------------------------------
    ONCALL_COMMAND_EXTEND = "oncall.command.extend"
    ONCALL_COMMAND_CHECK = "oncall.command.check"

    # ------------------------------------------------------------------
    # On-call events — outgoing from application_management
    # ------------------------------------------------------------------
    ONCALL_CHANGED = "oncall.changed"

    # ------------------------------------------------------------------
    # Scheduler infrastructure
    # ------------------------------------------------------------------
    SCHEDULER_REQUEST = "scheduler.request"

    # ------------------------------------------------------------------
    # Incident commands — incoming to incident_management (from plugins)
    # ------------------------------------------------------------------
    INCIDENT_COMMAND_CREATE = "incident.command.create"
    INCIDENT_COMMAND_UPDATE = "incident.command.update"
    INCIDENT_COMMAND_CHANGE_SEVERITY = "incident.command.changeSeverity"
    INCIDENT_COMMAND_CHANGE_STATE = "incident.command.changeState"
    INCIDENT_COMMAND_ASSIGN_ROLE = "incident.command.assignRole"
    INCIDENT_COMMAND_ADD_PARTICIPANT = "incident.command.addParticipant"
    INCIDENT_COMMAND_ADD_COMMENT = "incident.command.addComment"
    INCIDENT_COMMAND_ADD_ACTION_ITEM = "incident.command.addActionItem"
    INCIDENT_COMMAND_COMPLETE_ACTION_ITEM = "incident.command.completeActionItem"
    INCIDENT_COMMAND_UPDATE_ACTION_ITEM = "incident.command.updateActionItem"

    # ------------------------------------------------------------------
    # Postmortem commands — incoming to incident_management (from plugins)
    # ------------------------------------------------------------------
    POSTMORTEM_COMMAND_CREATE_DRAFT = "postmortem.command.createDraft"
    POSTMORTEM_COMMAND_CHANGE_STATE = "postmortem.command.changeState"

    # ------------------------------------------------------------------
    # Incident events — outgoing from incident_management
    # ------------------------------------------------------------------
    INCIDENT_CREATED = "incident.created"
    INCIDENT_UPDATED = "incident.updated"
    INCIDENT_STATE_ACKNOWLEDGED = "incident.state.acknowledged"
    INCIDENT_STATE_INVESTIGATING = "incident.state.investigating"
    INCIDENT_STATE_CONFIRMED = "incident.state.confirmed"
    INCIDENT_STATE_RESOLVED = "incident.state.resolved"
    INCIDENT_STATE_CLOSED = "incident.state.closed"
    INCIDENT_STATE_REOPENED = "incident.state.reopened"
    INCIDENT_SEVERITY_ESCALATED = "incident.severity.escalated"
    INCIDENT_SEVERITY_DEESCALATED = "incident.severity.deescalated"
    INCIDENT_ROLE_ASSIGNED = "incident.roleAssigned"
    INCIDENT_PARTICIPANT_ADDED = "incident.participantAdded"
    INCIDENT_COMMENT_ADDED = "incident.commentAdded"
    INCIDENT_ACTION_ITEM_CREATED = "incident.actionItemCreated"
    INCIDENT_ACTION_ITEM_DONE = "incident.actionItemDone"
    INCIDENT_ACTION_ITEM_UPDATED = "incident.actionItemUpdated"

    # ------------------------------------------------------------------
    # Postmortem events — outgoing from incident_management
    # ------------------------------------------------------------------
    POSTMORTEM_DRAFT_CREATED = "postmortem.draft.created"
    POSTMORTEM_DRAFT_UPDATED = "postmortem.draft.updated"
    POSTMORTEM_DRAFT_DELETED = "postmortem.draft.deleted"
    POSTMORTEM_STATE_SUBMITTED = "postmortem.state.submitted"
    POSTMORTEM_STATE_BACK_TO_DRAFT = "postmortem.state.backToDraft"
    POSTMORTEM_STATE_APPROVED = "postmortem.state.approved"
    POSTMORTEM_STATE_COMPLETED = "postmortem.state.completed"

    # ------------------------------------------------------------------
    # User events — outgoing from usermanagement (operational)
    # ------------------------------------------------------------------
    USER_PASSWORD_RESET_REQUESTED = "user.password.resetRequested"
    USER_PASSWORD_RESET_INITIATED = "user.password.resetInitiated"

    # ------------------------------------------------------------------
    # Audit events — user_management
    # ------------------------------------------------------------------
    AUDIT_USER_CREATE = "audit.user.create"
    AUDIT_USER_MODIFY = "audit.user.modify"
    AUDIT_USER_DELETE = "audit.user.delete"
    AUDIT_SERVICE_ACCOUNT_CREATE = "audit.serviceAccount.create"
    AUDIT_SERVICE_ACCOUNT_DELETE = "audit.serviceAccount.delete"
    AUDIT_ROLE_CREATE = "audit.role.create"
    AUDIT_ROLE_MODIFY = "audit.role.modify"
    AUDIT_ROLE_DELETE = "audit.role.delete"
    AUDIT_GROUP_CREATE = "audit.group.create"
    AUDIT_GROUP_MODIFY = "audit.group.modify"
    AUDIT_GROUP_MEMBERS_MODIFY = "audit.group.membersModify"
    AUDIT_GROUP_DELETE = "audit.group.delete"

    # ------------------------------------------------------------------
    # Audit events — application_management
    # ------------------------------------------------------------------
    AUDIT_APPLICATION_CREATE = "audit.application.create"
    AUDIT_APPLICATION_MODIFY = "audit.application.modify"
    AUDIT_APPLICATION_DELETE = "audit.application.delete"
    AUDIT_SERVICE_CREATE = "audit.service.create"
    AUDIT_SERVICE_MODIFY = "audit.service.modify"
    AUDIT_SERVICE_DELETE = "audit.service.delete"
    AUDIT_ENVIRONMENT_CREATE = "audit.environment.create"
    AUDIT_ENVIRONMENT_MODIFY = "audit.environment.modify"
    AUDIT_ENVIRONMENT_DELETE = "audit.environment.delete"
    AUDIT_SILENCE_RULE_CREATE = "audit.silenceRule.create"
    AUDIT_SILENCE_RULE_MODIFY = "audit.silenceRule.modify"
    AUDIT_SILENCE_RULE_DELETE = "audit.silenceRule.delete"
    AUDIT_ESCALATION_CREATE = "audit.escalation.create"
    AUDIT_ESCALATION_MODIFY = "audit.escalation.modify"
    AUDIT_ESCALATION_DELETE = "audit.escalation.delete"
    AUDIT_ESCALATION_OVERRIDE_CREATE = "audit.escalationOverride.create"
    AUDIT_ESCALATION_OVERRIDE_MODIFY = "audit.escalationOverride.modify"
    AUDIT_ESCALATION_OVERRIDE_DELETE = "audit.escalationOverride.delete"
    AUDIT_ON_CALL_ROTATION_CREATE = "audit.onCallRotation.create"
    AUDIT_ON_CALL_ROTATION_DELETE = "audit.onCallRotation.delete"
    AUDIT_ON_CALL_ROTATION_OVERRIDE_CREATE = "audit.onCallRotationOverride.create"
    AUDIT_ON_CALL_ROTATION_OVERRIDE_DELETE = "audit.onCallRotationOverride.delete"
    AUDIT_SERVICE_ACL_MODIFY = "audit.serviceAcl.modify"

    # ------------------------------------------------------------------
    # Audit events — incident_management
    # ------------------------------------------------------------------
    AUDIT_INCIDENT_RULE_CREATE = "audit.incidentRule.create"
    AUDIT_INCIDENT_RULE_MODIFY = "audit.incidentRule.modify"
    AUDIT_INCIDENT_RULE_DELETE = "audit.incidentRule.delete"

    # ------------------------------------------------------------------
    # Audit events — connection_management
    # ------------------------------------------------------------------
    AUDIT_CONNECTION_CREATE = "audit.connection.create"
    AUDIT_CONNECTION_MODIFY = "audit.connection.modify"
    AUDIT_CONNECTION_DELETE = "audit.connection.delete"
    AUDIT_CONNECTION_TEMPLATE_CREATE = "audit.connectionTemplate.create"
    AUDIT_CONNECTION_TEMPLATE_MODIFY = "audit.connectionTemplate.modify"
    AUDIT_CONNECTION_TEMPLATE_DELETE = "audit.connectionTemplate.delete"

    # ------------------------------------------------------------------
    # Audit events — plugin_management
    # ------------------------------------------------------------------
    AUDIT_PLUGIN_INSTALL = "audit.plugin.install"
    AUDIT_PLUGIN_UNINSTALL = "audit.plugin.uninstall"
    AUDIT_PLUGIN_ENABLE = "audit.plugin.enable"
    AUDIT_PLUGIN_DISABLE = "audit.plugin.disable"
    AUDIT_PLUGIN_UPDATE = "audit.plugin.update"
    AUDIT_PLUGIN_CONFIG_MODIFY = "audit.pluginConfig.modify"
    AUDIT_PLUGIN_RULE_CREATE = "audit.pluginRule.create"
    AUDIT_PLUGIN_RULE_MODIFY = "audit.pluginRule.modify"
    AUDIT_PLUGIN_RULE_DELETE = "audit.pluginRule.delete"

    # ------------------------------------------------------------------
    # Security events — outgoing from usermanagement
    # ------------------------------------------------------------------
    SECURITY_LOGIN_SUCCESS = "security.login.success"
    SECURITY_LOGIN_FAILED = "security.login.failed"
    SECURITY_PASSWORD_CHANGE = "security.passwordChange"
    SECURITY_PASSWORD_RESET = "security.passwordReset"
    SECURITY_OWN_PASSWORD_RESET = "security.ownPasswordReset"
    SECURITY_SERVICE_ACCOUNT_TOKEN_ROTATED = "security.serviceAccount.tokenRotated"
