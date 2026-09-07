# Helper Extraction Pattern

Use when the same control flow pattern is repeated 3+ times in a single file or method.

## When to Use

Look for:
- Identical if/error/return blocks repeated across pipeline stages
- Same report-saving loop with minor variations
- Duplicated data formatting or validation logic

**Rule of three**: 2 repetitions don't justify extraction. 3+ do.

## Pattern: Error-Check Helper

```python
# BEFORE: 6 copies of this
if not scout_result.is_success:
    logger.error(f"Scout failed: {scout_result.errors}")
    pipeline_result.completed = False
    return self._finalize(pipeline_result, start_time)

if not analyst_result.is_success:
    logger.error(f"Analyst failed: {analyst_result.errors}")
    pipeline_result.completed = False
    return self._finalize(pipeline_result, start_time)
# ...4 more identical blocks...

# AFTER: 1 helper, 6 call sites
def _check_result(self, result, name, pipeline_result, start_time, *, check_attr=None):
    """Return early result on failure, or None on success."""
    if check_attr is not None:
        failed = not getattr(result, check_attr, None)
        err_msg = f"{name} failed: No {check_attr.replace('_', ' ')} generated"
    else:
        failed = not result.is_success
        err_msg = f"{name} failed: {result.errors}"

    if failed:
        logger.error(err_msg)
        pipeline_result.completed = False
        return self._finalize(pipeline_result, start_time)
    return None

# Call sites become:
early = self._check_result(scout_result, "Scout", result, start_time)
if early:
    return early
```

## Pattern: Save-Reports Helper

```python
# BEFORE: 2 copies (standard + multi-period) with slight variations
for rec in recommendations:
    name = get_display_name(rec)
    html = generate_html(rec)
    # ...save to file...
    json_str = generate_json(rec)
    # ...save to file...

# AFTER: 1 helper with mode branching
def _save_reports(self, recommendations, mode, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for rec in recommendations:
        name = self.get_display_name(rec)
        if mode == "multi_period":
            html = self.generate_multi_period_report(rec)
            json_str = json.dumps(rec.to_dict(), indent=2)
            suffix = "multi_period_report"
        else:
            html = self.generate_report(rec)
            json_str = self.generate_json(rec)
            suffix = "report"
        # Save both files...
```

## Pattern: Context Dataclass

When a helper needs multiple parameters that travel together, create a dataclass:

```python
@dataclass
class PipelineContext:
    """Configuration snapshot for a single pipeline run."""
    mode: str       # "standard" or "multi_period"
    days: int
    output_dir: str
```

This avoids long parameter lists and makes the helper self-documenting.

## Design Rules

1. **Helpers are private** (`_` prefix) — they're internal implementation details
2. **Use keyword-only args for variants** — `*, check_attr=None` clearly separates the common path from the variant
3. **Preserve exact behavior** — the helper must produce the same logs, return values, and side effects as the inline code
4. **Keep helpers in the same class/file** — don't create a new module just for 2-3 helpers
5. **Don't over-abstract** — if the helper needs 8 parameters and a complex mode switch, it's not a good extraction

## Verification

After extracting helpers, verify:
1. All tests pass
2. Log output is identical (grep logs for the error messages)
3. Return values match (the caller must handle the helper's return the same way)
4. No behavior changed — the PR should be a pure refactor with +N/-M lines where N < M (fewer lines after extraction)

## Common Mistakes

- **Extracting too early** — wait for 3 repetitions, not 2
- **Changing behavior during extraction** — resist the urge to "improve" the logic while extracting. Do the mechanical extraction first, improve in a separate commit.
- **Forgetting edge cases** — if one of the 6 inline blocks had a slightly different condition, the helper must handle that variant (via a parameter, not by dropping it)
