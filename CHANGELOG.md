# Changelog
## 1.0.1

* `CATEGORY_REGISTRY` — per event category (`EventCategoryMetadata`): its display name.
* Clearer `display_name` for plugin-subscribable events that were ambiguous in the UI
  event picker (password reset family, `alert.action.update`, `incident.updated`,
  `oncall.changed`, application alert level, `audit.serviceAcl.modify`,
  `audit.pluginRule.*` → "Event rule …", …).
* Plugin-subscribable events must have unique display names; every category must be
  in `CATEGORY_REGISTRY` (both enforced by `tests/test_registry.py`).

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
