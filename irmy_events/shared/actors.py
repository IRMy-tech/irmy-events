from typing import Any, Literal, Union
from pydantic import BaseModel, model_validator


class RoleContext(BaseModel):
    id: str
    name: str
    permissions: list[str]
    permissionsBitMask: int


class UserActorContext(BaseModel):
    id: str
    firstName: str
    lastName: str
    email: str
    role: RoleContext


class ServiceAccountActorContext(BaseModel):
    id: str
    name: str
    role: RoleContext


class PluginActorContext(BaseModel):
    id: str
    name: str


class SystemActorContext(BaseModel):
    reason: str


class RuleActorContext(BaseModel):
    id: str
    name: str


class IdpActorContext(BaseModel):
    id: str
    name: str
    protocol: Literal["saml", "oidc"]


ActorContext = Union[
    UserActorContext,
    ServiceAccountActorContext,
    PluginActorContext,
    SystemActorContext,
    RuleActorContext,
    IdpActorContext,
]

_ACTOR_CONTEXT_MAP: dict[str, type[BaseModel]] = {
    "user": UserActorContext,
    "serviceAccount": ServiceAccountActorContext,
    "plugin": PluginActorContext,
    "system": SystemActorContext,
    "rule": RuleActorContext,
    "idp": IdpActorContext,
}


class EventBase(BaseModel):
    """Base for all RabbitMQ events.

    The model_validator discriminates actorContext to the correct typed model
    based on actorType before field validation runs.  Subclasses can narrow
    actorType and actorContext to the specific literals / types they accept.
    """

    actorType: str
    actorContext: ActorContext

    @model_validator(mode="before")
    @classmethod
    def _discriminate_actor_context(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        actor_type = data.get("actorType")
        ctx = data.get("actorContext")
        if isinstance(ctx, dict) and actor_type in _ACTOR_CONTEXT_MAP:
            data = {**data, "actorContext": _ACTOR_CONTEXT_MAP[actor_type].model_validate(ctx)}
        return data

    @model_validator(mode="after")
    def _check_actor_context_matches_type(self) -> "EventBase":
        # The before-validator only discriminates dict input; a model instance passed
        # directly (the usual way Python producers build events) must match too.
        expected = _ACTOR_CONTEXT_MAP.get(self.actorType)
        if expected is not None and not isinstance(self.actorContext, expected):
            raise ValueError(
                f"actorContext must be {expected.__name__} for actorType {self.actorType!r}, "
                f"got {type(self.actorContext).__name__}"
            )
        return self
