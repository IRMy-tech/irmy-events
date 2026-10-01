from typing import Any

# Condition trees (SimpleCondition / ComplexCondition) are kept as raw dicts.
# The recursive structure and field semantics vary between silenceRule and
# incidentRule; callers are responsible for interpreting the tree.
ConditionTree = dict[str, Any]
