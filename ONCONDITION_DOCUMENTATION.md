# onCondition: Dynamic Variable Manipulation System

## Overview

The `onCondition` system allows form questions to dynamically modify variables in the `vars` object based on conditional logic. This is a powerful feature that enables forms to:

- Build dynamic tag arrays based on user selections
- Calculate and set derived values
- Track aggregated information across form responses
- Create smart forms that adapt their internal state

## Key Differences from `visibleWhen`

| Feature | `visibleWhen` | `onCondition` |
|---------|---------------|---------------|
| Purpose | Controls question visibility | Modifies form variables |
| UI Effect | Shows/hides questions | No visual change (affects internal state) |
| Execution | Evaluated on every form state change | Evaluated when conditions are met |
| Data Impact | None | Modifies `vars` object |

## Schema Structure

```json
{
  "id": 4,
  "title": "Employment Status",
  "type": "choice",
  "value": "",
  "choices": ["employed", "student", "unemployed"],
  "onCondition": [
    {
      "condition": {
        "path": "4",
        "op": "equals",
        "value": "employed"
      },
      "action": {
        "type": "append",
        "varName": "user_tags",
        "value": "professional"
      }
    }
  ]
}
```

## Condition Types

### 1. Simple Condition

A single condition that must be met:

```json
{
  "condition": {
    "path": "4",
    "op": "equals",
    "value": "employed"
  },
  "action": { ... }
}
```

### 2. Multiple Conditions (AND) - `allOf`

All conditions must be true:

```json
{
  "condition": {
    "allOf": [
      {
        "path": "8",
        "op": "greater_than",
        "value": "10"
      },
      {
        "path": "7",
        "op": "equals",
        "value": true
      }
    ]
  },
  "action": { ... }
}
```

### 3. Multiple Conditions (OR) - `anyOf`

At least one condition must be true:

```json
{
  "condition": {
    "anyOf": [
      {
        "path": "4",
        "op": "equals",
        "value": "employed"
      },
      {
        "path": "4",
        "op": "equals",
        "value": "student"
      }
    ]
  },
  "action": { ... }
}
```

## Operators

The `onCondition` system supports the same operators as `visibleWhen`:

### Comparison Operators
- `equals` - Exact match
- `not_equals` - Not equal to
- `greater_than` - Greater than (numeric)
- `less_than` - Less than (numeric)
- `greaterThanOrEqual` - Greater than or equal (numeric)
- `lessThanOrEqual` - Less than or equal (numeric)

### Array/String Operators
- `contains` - Value contains substring or array includes item
- `not_contains` - Value does not contain substring or array does not include item

### Empty Check Operators
- `isEmpty` - Value is empty/null/undefined
- `isNotEmpty` - Value has content

### Date Operators (for date type fields)
- `before` - Date is before specified date
- `after` - Date is after specified date
- `on` - Date equals specified date
- `isPast` - Date is in the past
- `isFuture` - Date is in the future
- `isToday` - Date is today
- `daysAgo` - Date is N days ago
- `daysFromNow` - Date is N days from now
- `monthsAgo` - Date is N months ago
- `monthsFromNow` - Date is N months from now
- `yearsAgo` - Date is N years ago
- `yearsFromNow` - Date is N years from now

## Action Types

### 1. `set` - Set Variable Value

Sets or overwrites the variable with a new value:

```json
{
  "action": {
    "type": "set",
    "varName": "experience_level",
    "value": "senior"
  }
}
```

**Behavior:**
- Creates the variable if it doesn't exist
- Overwrites existing value
- Best for: Status flags, categorical values, single values

### 2. `append` - Append to Array

Adds a value to an array variable:

```json
{
  "action": {
    "type": "append",
    "varName": "user_tags",
    "value": "professional"
  }
}
```

**Behavior:**
- Creates an empty array if variable doesn't exist
- Appends value to existing array
- Allows duplicate values
- Best for: Tags, categories, multi-select aggregation

### 3. `increment` - Increment Number

Increases a numeric variable by the specified value:

```json
{
  "action": {
    "type": "increment",
    "varName": "score",
    "value": "10"
  }
}
```

**Behavior:**
- Creates variable with value 0 if it doesn't exist
- Adds the specified value to current value
- Best for: Scoring, counting, totals

### 4. `decrement` - Decrement Number

Decreases a numeric variable by the specified value:

```json
{
  "action": {
    "type": "decrement",
    "varName": "remaining_attempts",
    "value": "1"
  }
}
```

**Behavior:**
- Creates variable with value 0 if it doesn't exist
- Subtracts the specified value from current value
- Best for: Counters, limits, remaining items

## Complete Examples

### Example 1: Building User Tags Based on Employment

```json
{
  "id": 4,
  "title": "Employment Status",
  "type": "choice",
  "value": "",
  "choices": ["employed", "student", "unemployed", "retired"],
  "onCondition": [
    {
      "condition": {
        "path": "4",
        "op": "equals",
        "value": "employed"
      },
      "action": {
        "type": "append",
        "varName": "user_tags",
        "value": "professional"
      }
    },
    {
      "condition": {
        "path": "4",
        "op": "equals",
        "value": "student"
      },
      "action": {
        "type": "append",
        "varName": "user_tags",
        "value": "education"
      }
    }
  ]
}
```

**Result:** When user selects "employed", `vars.user_tags` becomes `["professional"]`

### Example 2: Multi-Level Skill Assessment

```json
{
  "id": 8,
  "title": "Years of Experience",
  "type": "numeric",
  "value": "",
  "placeholder": "Enter years of experience",
  "onCondition": [
    {
      "condition": {
        "path": "8",
        "op": "greater_than",
        "value": "5"
      },
      "action": {
        "type": "set",
        "varName": "experience_level",
        "value": "senior"
      }
    },
    {
      "condition": {
        "path": "8",
        "op": "lessThanOrEqual",
        "value": "5"
      },
      "action": {
        "type": "set",
        "varName": "experience_level",
        "value": "mid"
      }
    },
    {
      "condition": {
        "allOf": [
          {
            "path": "8",
            "op": "greater_than",
            "value": "10"
          },
          {
            "path": "7",
            "op": "equals",
            "value": true
          }
        ]
      },
      "action": {
        "type": "append",
        "varName": "user_tags",
        "value": "expert"
      }
    }
  ]
}
```

**Result:** 
- If years > 5: `vars.experience_level = "senior"`
- If years ≤ 5: `vars.experience_level = "mid"`
- If years > 10 AND is senior developer: `"expert"` is appended to `vars.user_tags`

### Example 3: Tech Stack Detection

```json
{
  "id": 6,
  "title": "Skills",
  "type": "toggleList",
  "value": "",
  "choices": ["JavaScript", "Python", "React", "Node.js", "Django", "Vue.js"],
  "onCondition": [
    {
      "condition": {
        "path": "6",
        "op": "contains",
        "value": "JavaScript"
      },
      "action": {
        "type": "append",
        "varName": "tech_stack",
        "value": "frontend"
      }
    },
    {
      "condition": {
        "path": "6",
        "op": "contains",
        "value": "Python"
      },
      "action": {
        "type": "append",
        "varName": "tech_stack",
        "value": "backend"
      }
    }
  ]
}
```

**Result:** If user selects both JavaScript and Python, `vars.tech_stack = ["frontend", "backend"]`

### Example 4: Scoring System

```json
{
  "id": 12,
  "title": "Quality Rating",
  "type": "choice",
  "value": "",
  "choices": ["Excellent", "Good", "Fair", "Poor"],
  "onCondition": [
    {
      "condition": {
        "path": "12",
        "op": "equals",
        "value": "Excellent"
      },
      "action": {
        "type": "increment",
        "varName": "total_score",
        "value": "100"
      }
    },
    {
      "condition": {
        "path": "12",
        "op": "equals",
        "value": "Good"
      },
      "action": {
        "type": "increment",
        "varName": "total_score",
        "value": "75"
      }
    },
    {
      "condition": {
        "path": "12",
        "op": "equals",
        "value": "Fair"
      },
      "action": {
        "type": "increment",
        "varName": "total_score",
        "value": "50"
      }
    },
    {
      "condition": {
        "path": "12",
        "op": "equals",
        "value": "Poor"
      },
      "action": {
        "type": "increment",
        "varName": "total_score",
        "value": "25"
      }
    }
  ]
}
```

## Usage in Editor

### Adding onCondition Rules

1. Open the question editor for any question
2. Scroll to the "Variable Actions (onCondition)" section
3. Click "+ Add Variable Action"
4. Configure the WHEN (Condition):
   - Select condition type (Simple, AND, OR)
   - Set the path to the question you're checking
   - Choose the operator
   - Enter the comparison value
5. Configure the THEN (Action):
   - Select action type (Set, Append, Increment, Decrement)
   - Enter the variable name (will be created in `vars` if it doesn't exist)
   - Enter the value to set/append/add/subtract
6. Click "Save"

### Multiple Rules per Question

A single question can have multiple `onCondition` rules. Each rule is evaluated independently when its condition is met.

## Best Practices

### 1. Initialize Variables in `vars`

Always initialize variables in the `vars` object with appropriate default values:

```json
"vars": {
  "user_tags": [],           // Empty array for append operations
  "experience_level": "junior", // Default value for set operations
  "total_score": 0           // Zero for increment/decrement
}
```

### 2. Use Descriptive Variable Names

Choose clear, self-explanatory names:
- ✅ `user_tags`, `tech_stack`, `experience_level`
- ❌ `arr1`, `temp`, `data`

### 3. Avoid Circular Dependencies

Don't create conditions that reference variables modified by the same question chain, as this can lead to infinite loops.

### 4. Combine with `visibleWhen`

Use both systems together for powerful conditional logic:
- Use `visibleWhen` to show/hide questions
- Use `onCondition` to track internal state based on those answers

### 5. Document Complex Logic

For forms with many `onCondition` rules, maintain separate documentation explaining the variable flow and dependencies.

## Implementation Status

### ✅ Completed Features
- Full schema support for simple, allOf, and anyOf conditions
- All action types (set, append, increment, decrement)
- UI editor for creating and managing onCondition rules
- JSON serialization and deserialization
- Example forms with onCondition demonstrations

### 🚧 Pending Implementation (Frontend Evaluation)
- Runtime evaluation engine for conditions
- Variable state management during form filling
- Real-time variable updates as users answer questions
- Display of computed variables in form

The current implementation provides the **data structure and editor UI**. To make this fully functional, you'll need to implement the evaluation logic in your form renderer that:
1. Monitors form state changes
2. Evaluates onCondition rules when relevant questions are answered
3. Updates the `vars` object according to action types
4. Triggers re-renders when variables change (for display fields using those variables)

## Future Enhancements

Potential additions to the system:
- `remove` action type to remove items from arrays
- `toggle` action type for boolean variables
- `concat` action type to join string values
- Expression support in action values (e.g., referencing other variables)
- Conditional chaining (one condition triggering another)
- Variable history/rollback capabilities
- Debug mode to trace variable changes

## Support

For questions, issues, or feature requests related to the onCondition system, please refer to the main project documentation or create an issue in the project repository.

