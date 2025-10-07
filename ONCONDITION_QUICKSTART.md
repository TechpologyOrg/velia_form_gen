# onCondition Quick Start Guide

## What is onCondition?

`onCondition` is a system that lets form questions automatically update variables when certain conditions are met. Unlike `visibleWhen` which controls visibility, `onCondition` modifies the form's internal state.

## Quick Example

```json
{
  "id": 4,
  "title": "Are you a student?",
  "type": "boolean",
  "value": false,
  "onCondition": [
    {
      "condition": {
        "path": "4",
        "op": "equals",
        "value": true
      },
      "action": {
        "type": "append",
        "varName": "user_tags",
        "value": "student"
      }
    }
  ]
}
```

**What it does:** When user selects `true`, it adds `"student"` to the `user_tags` array in `vars`.

## Common Use Cases

### 1. Tagging Users

```json
"onCondition": [
  {
    "condition": { "path": "employment", "op": "equals", "value": "employed" },
    "action": { "type": "append", "varName": "tags", "value": "professional" }
  }
]
```

### 2. Setting Status

```json
"onCondition": [
  {
    "condition": { "path": "age", "op": "greater_than", "value": "65" },
    "action": { "type": "set", "varName": "status", "value": "senior" }
  }
]
```

### 3. Scoring

```json
"onCondition": [
  {
    "condition": { "path": "answer", "op": "equals", "value": "correct" },
    "action": { "type": "increment", "varName": "score", "value": "10" }
  }
]
```

### 4. Multiple Conditions (AND)

```json
"onCondition": [
  {
    "condition": {
      "allOf": [
        { "path": "age", "op": "greater_than", "value": "18" },
        { "path": "hasLicense", "op": "equals", "value": true }
      ]
    },
    "action": { "type": "set", "varName": "canDrive", "value": "yes" }
  }
]
```

### 5. Multiple Conditions (OR)

```json
"onCondition": [
  {
    "condition": {
      "anyOf": [
        { "path": "role", "op": "equals", "value": "admin" },
        { "path": "role", "op": "equals", "value": "moderator" }
      ]
    },
    "action": { "type": "set", "varName": "hasPermissions", "value": true }
  }
]
```

## Action Types Cheat Sheet

| Action Type | Purpose | Example |
|-------------|---------|---------|
| `set` | Set/overwrite a value | Status, category, single value |
| `append` | Add to an array | Tags, lists, multiple selections |
| `increment` | Add to a number | Score, points, counter |
| `decrement` | Subtract from a number | Lives, attempts, countdown |

## Operators Cheat Sheet

### Basic
- `equals` - Exact match
- `not_equals` - Not equal
- `contains` - String/array contains
- `not_contains` - Doesn't contain

### Numeric
- `greater_than` - `>`
- `less_than` - `<`
- `greaterThanOrEqual` - `≥`
- `lessThanOrEqual` - `≤`

### Empty Check
- `isEmpty` - No value
- `isNotEmpty` - Has value

## In the Editor

1. Edit any question
2. Scroll to "Variable Actions (onCondition)"
3. Click "+ Add Variable Action"
4. Fill in:
   - **WHEN section**: The condition to check
   - **THEN section**: What to do with which variable
5. Save

## Tips

✅ **DO:**
- Initialize variables in `vars` object
- Use descriptive variable names
- Test your conditions

❌ **DON'T:**
- Create circular dependencies
- Forget to initialize array variables as `[]`
- Use numeric operations on non-numeric values

## See Also

- Full documentation: `ONCONDITION_DOCUMENTATION.md`
- Sample form: `sample_form.json`

