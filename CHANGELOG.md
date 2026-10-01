# Changelog
## 1.0.0
Initial release.

* Pydantic v2 models for every IRMy RabbitMQ payload: alert, application state,
  on-call, scheduler, incident, postmortem, user, audit and security events and
  commands.
* `RoutingKeys` — every routing key used on the platform.
* `EVENT_REGISTRY` — per routing key: category, display name, description, plugin
  subscribe/publish permissions and the payload model.
* `EventBase` resolves `actorContext` to the model matching `actorType` and rejects
  a mismatching context, whether given as a dict or as a model instance.
