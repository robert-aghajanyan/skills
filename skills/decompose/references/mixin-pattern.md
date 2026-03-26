# Mixin Composition Pattern

Use when a single file has 1000+ lines with 5+ distinct capability areas and methods that cluster cleanly by domain.

## Target Structure

```
BEFORE: src/module/thing.py (5000 lines)

AFTER:  src/module/thing/
        ├── __init__.py        — Composed class + re-exports for backward compat
        ├── models.py          — Dataclasses, enums extracted from the monolith
        ├── capability_a.py    — CapabilityAMixin (one domain area)
        ├── capability_b.py    — CapabilityBMixin (another domain)
        ├── capability_c.py    — CapabilityCMixin
        └── ...
```

## Composition Pattern

```python
# __init__.py
from .models import SomeModel, SomeEnum
from .capability_a import CapabilityAMixin
from .capability_b import CapabilityBMixin
from .base_or_parent import BaseClass

class Thing(
    CapabilityBMixin,    # Higher-level (may call A's methods)
    CapabilityAMixin,    # Lower-level
    BaseClass,           # ALWAYS LAST — provides __init__, shared state
):
    """Composed class — all behavior comes from mixins."""
    # Class-level constants and __init__ go here
    # Or in BaseClass if there's a separate base
    pass

# Re-export all public symbols for backward compatibility
__all__ = ["Thing", "SomeModel", "SomeEnum"]
```

## Mixin Rules

1. **Each mixin is a plain class with methods only** — no `__init__`, no instance state
2. **Mixins access shared state via `self.*`** — the composed class or base provides attributes
3. **Base class goes LAST** in the inheritance list (Python MRO resolves right-to-left for `__init__`)
4. **Zero method name collisions** — verify programmatically that no two mixins define the same method
5. **One domain per mixin** — if you can't name it in 2-3 words (e.g., "HTML report generation"), it's too broad
6. **Mixins can call other mixins' methods via `self`** — they're all mixed into one class at runtime

## MRO (Method Resolution Order)

Python uses C3 linearization. The key rule: **base class goes last**, higher-level mixins go first.

```python
class MyClass(HighLevelMixin, MidLevelMixin, LowLevelMixin, BaseClass):
    pass

# MRO: MyClass → HighLevelMixin → MidLevelMixin → LowLevelMixin → BaseClass → object
```

If `HighLevelMixin` and `LowLevelMixin` both define `do_thing()`, `HighLevelMixin.do_thing()` wins. But this should never happen — collisions are a design bug.

## Verifying No Collisions

```python
mixins = [CapabilityAMixin, CapabilityBMixin, CapabilityCMixin]
for i in range(len(mixins)):
    for j in range(i+1, len(mixins)):
        a_methods = {m for m in mixins[i].__dict__ if not m.startswith('__')}
        b_methods = {m for m in mixins[j].__dict__ if not m.startswith('__')}
        overlap = a_methods & b_methods
        assert not overlap, f"Collision: {mixins[i].__name__} vs {mixins[j].__name__}: {overlap}"
```

## Backward Compatibility

When converting `module/thing.py` (a file) to `module/thing/` (a package), Python automatically treats `module/thing/__init__.py` as the same import path. So:

```python
# This still works — no shim needed
from module.thing import Thing
```

But you MUST re-export all public symbols from `__init__.py`:
- All classes, functions, and constants that were importable from the old file
- Use `__all__` to make the public API explicit
- If other files imported specific names (e.g., `from module.thing import SomeEnum`), those must be importable from the new `__init__.py`

## Line Count Sanity Check

After decomposition, the new total should be close to the old file plus ~5-10% for module boilerplate (docstrings, imports, class declarations). A much larger delta means code was added or duplicated — investigate.

## Common Mistakes

- **Forgetting to re-export models/enums** — if the old file had `class NotificationChannel(Enum)`, it must still be importable from the package
- **Circular imports** — mixin A imports something from mixin B which imports from A. Fix by moving shared types to `models.py`
- **Putting `__init__` in a mixin** — only the base class or composed class should have `__init__`
- **Not checking MRO** — run `print([c.__name__ for c in Thing.__mro__])` to verify
