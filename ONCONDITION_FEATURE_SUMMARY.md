# onCondition Feature Summary

## Overview

The **onCondition** system is a new event-driven feature that allows form questions to dynamically manipulate variables based on conditional logic. This powerful addition works alongside the existing `visibleWhen` feature to create intelligent, reactive forms.

## What's New

### Core Functionality
- **Conditional Variable Manipulation**: Questions can now modify variables in the `vars` object when specific conditions are met
- **Multiple Action Types**: Support for `set`, `append`, `increment`, and `decrement` operations
- **Complex Conditions**: Simple, AND (`allOf`), and OR (`anyOf`) condition logic
- **Full Operator Support**: All existing operators from `visibleWhen` are available

### UI Features
- **Visual Editor**: Intuitive UI for creating and managing onCondition rules
- **WHEN/THEN Interface**: Clear separation between conditions and actions
- **Multiple Rules**: Add multiple onCondition rules to a single question
- **Live Preview**: See the JSON structure update in real-time

## Use Cases

1. **User Segmentation**: Automatically tag users based on their answers
2. **Dynamic Scoring**: Build scoring systems that calculate points based on responses
3. **State Management**: Track complex form states without manual calculation
4. **Data Aggregation**: Collect and organize information across multiple questions
5. **Conditional Logic**: Create forms that adapt their internal state based on user input

## Example

```json
{
  "id": 4,
  "title": "Employment Status",
  "type": "choice",
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

When a user selects "employed", the system automatically appends "professional" to the `user_tags` array in the `vars` object.

## Files Modified

- `formgen/templates/core/editor.html`: Added UI controls and JavaScript logic for onCondition
- `sample_form.json`: Added comprehensive examples of onCondition usage
- New documentation files:
  - `ONCONDITION_DOCUMENTATION.md`: Complete reference guide
  - `ONCONDITION_QUICKSTART.md`: Quick start guide with examples

## Schema Structure

```json
{
  "question": {
    "id": "...",
    "title": "...",
    "type": "...",
    "onCondition": [
      {
        "condition": {
          "path": "question_id",
          "op": "operator",
          "value": "comparison_value"
        },
        "action": {
          "type": "set|append|increment|decrement",
          "varName": "variable_name",
          "value": "action_value"
        }
      }
    ]
  }
}
```

## Action Types

| Type | Description | Use Case |
|------|-------------|----------|
| `set` | Set/overwrite variable value | Status flags, single values |
| `append` | Add value to array | Tags, categories, lists |
| `increment` | Add to numeric value | Scoring, counting |
| `decrement` | Subtract from numeric value | Remaining attempts, lives |

## Condition Types

1. **Simple Condition**: Single path, operator, and value
2. **allOf (AND)**: All conditions must be true
3. **anyOf (OR)**: At least one condition must be true

## Integration Notes

### Current Implementation
✅ Schema design
✅ Editor UI
✅ JSON serialization/deserialization
✅ Example forms
✅ Documentation

### Pending (Frontend Runtime)
The data structure and editor are complete. To make this fully functional in a form renderer, you'll need to implement:

1. **Condition Evaluation Engine**: Evaluate conditions when questions are answered
2. **Variable State Manager**: Update `vars` object based on actions
3. **Action Executors**: Implement set, append, increment, decrement logic
4. **Change Detection**: Monitor form state and trigger evaluations

## Benefits

- **Reduced Backend Logic**: Handle simple data transformations on the frontend
- **Real-time Feedback**: Variables update immediately as users interact
- **Flexible Architecture**: Easy to extend with new action types
- **Clean Separation**: Conditions separate from visibility logic
- **Developer Friendly**: Intuitive JSON structure, easy to debug

## Future Enhancements

Potential additions:
- `remove` action for array manipulation
- `toggle` action for boolean values
- Expression evaluation in action values
- Variable references in conditions
- Debugging/tracing tools
- Export variable change history

## Getting Started

1. **Read the Docs**: Start with `ONCONDITION_QUICKSTART.md`
2. **Explore Examples**: Check `sample_form.json` for real-world examples
3. **Try the Editor**: Open any form and add Variable Actions to questions
4. **Deep Dive**: Read `ONCONDITION_DOCUMENTATION.md` for complete details

## Questions?

Refer to the documentation files or examine the implementation in `formgen/templates/core/editor.html` for detailed usage examples.

---

**Feature Status**: ✅ Schema & UI Complete | ⏳ Runtime Evaluation Pending

