import pytest
from pydantic import ValidationError

import irmy_events
from irmy_events import (
    IncidentCommandUpdateActionItem,
    PluginActorContext,
    SystemActorContext,
    UserPasswordResetInitiated,
)

_ROLE = {"id": "r", "name": "Owner", "permissions": [], "permissionsBitMask": 1}
_USER_CTX = {"id": "u", "firstName": "A", "lastName": "B", "email": "a@b.c", "role": _ROLE}
_USER_REF = {"id": "1", "firstName": "A", "lastName": "B", "email": "a@b.c"}


def _reset_initiated(**overrides):
    data = {
        "actorType": "user",
        "actorContext": _USER_CTX,
        "user": _USER_REF,
        "resetUrl": "encrypted",
        "occurredAt": "2026-01-01T00:00:00Z",
    }
    data.update(overrides)
    return data


def test_actor_context_dict_is_discriminated():
    event = UserPasswordResetInitiated.model_validate(_reset_initiated())
    assert type(event.actorContext).__name__ == "UserActorContext"


def test_actor_context_instance_must_match_actor_type():
    with pytest.raises(ValidationError, match="actorContext must be UserActorContext"):
        UserPasswordResetInitiated(**_reset_initiated(actorContext=PluginActorContext(id="p", name="n")))


def test_actor_context_instance_matching_actor_type_is_accepted():
    from irmy_events.alert import AlertCommandReassign

    event = AlertCommandReassign(
        actorType="system", actorContext=SystemActorContext(reason="escalation"), alertId="a", userId="u"
    )
    assert event.actorContext.reason == "escalation"


def test_actor_context_roundtrip():
    event = UserPasswordResetInitiated.model_validate(_reset_initiated())
    again = UserPasswordResetInitiated.model_validate_json(event.model_dump_json())
    assert again == event


def _update_action_item(**overrides):
    data = {
        "actorType": "plugin",
        "actorContext": {"id": "p", "name": "n"},
        "incidentId": "i",
        "actionItemId": "a",
    }
    data.update(overrides)
    return IncidentCommandUpdateActionItem.model_validate(data)


@pytest.mark.parametrize("due_date", [None, "", "2026-10-01T12:00:00Z", "2026-10-01T12:00:00+02:00"])
def test_due_date_tri_state_valid(due_date):
    assert _update_action_item(dueDate=due_date).dueDate == due_date


@pytest.mark.parametrize("due_date", ["not-a-date", "tomorrow", "2026-13-01T00:00:00Z"])
def test_due_date_invalid(due_date):
    with pytest.raises(ValidationError, match="dueDate must be an ISO-8601 datetime"):
        _update_action_item(dueDate=due_date)


@pytest.mark.parametrize(
    "name", ["AuditOwnerRef", "AuditOnCallParticipant", "AuditServiceAclEntry", "AuditIncidentRoleAssignment", "ReviewedByUser"]
)
def test_nested_models_are_exported(name):
    assert hasattr(irmy_events, name)
