"""Registry completeness and payload-model coverage.

Run with pytest, or standalone: ``python tests/test_registry.py``.
"""
from collections import Counter

from pydantic import BaseModel

from irmy_events import RoutingKeys, EVENT_REGISTRY, CATEGORY_REGISTRY, EventCategory


def test_registry_is_complete():
    """Every routing key has a metadata entry."""
    missing = [rk.name for rk in RoutingKeys if rk not in EVENT_REGISTRY]
    assert not missing, f"routing keys without a registry entry: {missing}"


def test_routing_key_field_matches_key():
    """Each entry's routing_key field matches the dict key it is stored under."""
    mismatched = [rk.name for rk, meta in EVENT_REGISTRY.items() if meta.routing_key != rk]
    assert not mismatched, f"entries whose routing_key field mismatches their key: {mismatched}"


def test_payload_model_is_a_base_model_or_none():
    """payload_model is either a BaseModel subclass or an explicit None."""
    bad = [
        rk.name for rk, meta in EVENT_REGISTRY.items()
        if meta.payload_model is not None
        and not (isinstance(meta.payload_model, type) and issubclass(meta.payload_model, BaseModel))
    ]
    assert not bad, f"payload_model is neither a BaseModel subclass nor None: {bad}"


def test_plugin_facing_keys_have_a_payload_model():
    """Any key a plugin can subscribe to or publish must be deserializable."""
    offenders = [
        rk.name for rk, meta in EVENT_REGISTRY.items()
        if (meta.plugin_subscribable or meta.plugin_publishable) and meta.payload_model is None
    ]
    assert not offenders, f"plugin-facing keys without a payload_model: {offenders}"


def test_payload_models_are_unique_per_key():
    """A payload model maps to exactly one routing key (no accidental reuse)."""
    counts = Counter(
        meta.payload_model for meta in EVENT_REGISTRY.values() if meta.payload_model is not None
    )
    dupes = {model.__name__: n for model, n in counts.items() if n > 1}
    assert not dupes, f"payload models reused across keys: {dupes}"



def test_subscribable_display_names_are_unique():
    """Plugin-subscribable events are picked by display_name in the UI, so two
    of them must never share one."""
    counts = Counter(meta.display_name for meta in EVENT_REGISTRY.values() if meta.plugin_subscribable)
    dupes = {name: n for name, n in counts.items() if n > 1}
    assert not dupes, f"display_name shared by several plugin-subscribable keys: {dupes}"


def test_category_registry_is_complete():
    """Every event category has a metadata entry."""
    missing = [c.name for c in EventCategory if c not in CATEGORY_REGISTRY]
    assert not missing, f"event categories without a registry entry: {missing}"


def test_category_field_matches_key():
    """Each category entry's category field matches the dict key it is stored under."""
    mismatched = [c.name for c, meta in CATEGORY_REGISTRY.items() if meta.category != c]
    assert not mismatched, f"entries whose category field mismatches their key: {mismatched}"


def test_category_display_names_are_unique():
    """No two categories share a display_name."""
    counts = Counter(meta.display_name for meta in CATEGORY_REGISTRY.values())
    dupes = {name: n for name, n in counts.items() if n > 1}
    assert not dupes, f"display_name shared by several categories: {dupes}"


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("all registry tests passed")
