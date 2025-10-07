# Implementation Summary: onCondition Variable Manipulation System

## Date Implemented
October 7, 2025

## Feature Description

Implemented a comprehensive **onCondition** event system that allows form questions to dynamically manipulate variables in the `vars` object based on conditional logic. This feature works independently of the existing `visibleWhen` system and enables forms to maintain complex internal state.

## What Was Built

### 1. Data Schema Design

Created a flexible JSON schema for `onCondition` rules that supports:

```json
{
  "onCondition": [
    {
      "condition": {
        "path": "question_id",
        "op": "operator", 
        "value": "comparison_value"
        // OR: { "allOf": [...] } OR { "anyOf": [...] }
      },
      "action": {
        "type": "set|append|increment|decrement",
        "varName": "variable_name",
        "value": "action_value"
      }
    }
  ]
}
```

**Condition Types:**
- Simple conditions (path, op, value)
- `allOf` - Multiple conditions with AND logic
- `anyOf` - Multiple conditions with OR logic

**Action Types:**
- `set` - Set/overwrite a variable value
- `append` - Append value to array variable
- `increment` - Add to numeric variable
- `decrement` - Subtract from numeric variable

**Operators:**
All existing operators from `visibleWhen`:
- Comparison: equals, not_equals, greater_than, less_than, greaterThanOrEqual, lessThanOrEqual
- String/Array: contains, not_contains
- Empty checks: isEmpty, isNotEmpty
- Date operators: before, after, on, isPast, isFuture, isToday, daysAgo, etc.

### 2. Editor UI Components

**Location:** `formgen/templates/core/editor.html`

**Added UI Elements:**

1. **Main Section** (lines 343-356):
   - "Variable Actions (onCondition)" section in question editor
   - Container for multiple onCondition rules
   - "Add Variable Action" button

2. **JavaScript Functions** (lines 1972-2182):
   - `addOnCondition()` - Creates a new onCondition rule UI element
   - `removeOnCondition()` - Removes a rule
   - `updateOnConditionType()` - Switches between simple/allOf/anyOf
   - `addOnConditionCondition()` - Adds condition to allOf list
   - `addOnConditionAnyOfCondition()` - Adds condition to anyOf list

3. **Rule UI Structure:**
   - Visual separation with color-coded sections:
     - Blue section: WHEN (Condition) 
     - Green section: THEN (Action)
   - Dropdown for condition type selection
   - Dynamic condition fields based on type
   - Action type selector
   - Variable name input
   - Action value input

### 3. Data Persistence

**Load Logic** (lines 901-953 in editor.html):
- Reads existing `onCondition` data from questions
- Populates UI elements with saved values
- Handles all condition types (simple, allOf, anyOf)
- Restores multiple rules per question

**Save Logic** (lines 1592-1696 in editor.html):
- Collects data from all onCondition rule UI elements
- Validates conditions and actions
- Builds proper JSON structure
- Saves to question object
- Cleans up empty/invalid rules

### 4. Sample Data

**File:** `sample_form.json`

Added three comprehensive examples:

1. **Employment Status** (Question ID 4):
   - Tags users as "professional" when employed
   - Tags users as "education" when student
   - Demonstrates: Multiple rules, append action

2. **Skills Selection** (Question ID 6):
   - Detects frontend stack when JavaScript selected
   - Detects backend stack when Python selected
   - Demonstrates: contains operator, tech categorization

3. **Years of Experience** (Question ID 8):
   - Sets experience_level to "senior" or "mid" based on years
   - Adds "expert" tag for 10+ years with senior status
   - Demonstrates: Numeric comparison, allOf conditions, mixed actions

**Added Variables to vars:**
```json
"vars": {
  "user_tags": [],
  "tech_stack": [],
  "experience_level": "junior"
}
```

### 5. Documentation

Created three comprehensive documentation files:

1. **ONCONDITION_DOCUMENTATION.md** (Complete Reference)
   - Full schema explanation
   - All operators and action types
   - Multiple complete examples
   - Best practices
   - Implementation status
   - Future enhancements

2. **ONCONDITION_QUICKSTART.md** (Quick Start Guide)
   - Brief overview
   - Common use cases with code
   - Cheat sheets for actions and operators
   - Tips and dos/don'ts

3. **ONCONDITION_FEATURE_SUMMARY.md** (Feature Overview)
   - High-level description
   - Use cases
   - Files modified
   - Schema structure
   - Integration notes

4. **IMPLEMENTATION_SUMMARY.md** (This File)
   - Technical implementation details
   - Code locations
   - Testing guidance

## Files Modified

### Primary Implementation
- **formgen/templates/core/editor.html**
  - Added UI section (lines 343-356)
  - Added load logic (lines 901-953) 
  - Added save logic (lines 1592-1696)
  - Added JavaScript functions (lines 1972-2182)
  - Total additions: ~350 lines

### Sample Data
- **sample_form.json**
  - Added onCondition to 3 questions
  - Added 3 new vars
  - Total additions: ~100 lines

### Documentation
- **ONCONDITION_DOCUMENTATION.md** (New file, ~550 lines)
- **ONCONDITION_QUICKSTART.md** (New file, ~150 lines)
- **ONCONDITION_FEATURE_SUMMARY.md** (New file, ~200 lines)
- **IMPLEMENTATION_SUMMARY.md** (This file)

## Technical Details

### UI Component Architecture

The onCondition UI uses a hierarchical structure:

```
Variable Action Rule (blue border)
├── WHEN Section (white background)
│   ├── Condition Type Selector
│   ├── Simple Condition (default visible)
│   ├── AllOf Conditions (hidden)
│   │   ├── Condition 1
│   │   ├── Condition 2
│   │   └── + Add Condition
│   └── AnyOf Conditions (hidden)
│       └── Similar to AllOf
└── THEN Section (green background)
    ├── Action Type Selector
    ├── Variable Name Input
    └── Value Input
```

### CSS Classes Used

**Structural:**
- `.border-blue-200` - Main rule container
- `.bg-blue-50` - Rule background
- `.bg-white` - Condition section
- `.bg-green-50` - Action section

**Functional:**
- `.onConditionType` - Condition type selector
- `.onConditionSimple` - Simple condition container
- `.onConditionAllOf` - AllOf conditions container
- `.onConditionAnyOf` - AnyOf conditions container
- `.onConditionSimplePath/Op/Value` - Simple condition inputs
- `.onConditionPath/Op/Value` - AllOf condition inputs
- `.onConditionAnyOfPath/Op/Value` - AnyOf condition inputs
- `.onConditionActionType` - Action type selector
- `.onConditionVarName` - Variable name input
- `.onConditionActionValue` - Action value input

### Data Flow

1. **Loading:**
   - `editQuestion()` called → reads `question.onCondition` array
   - For each rule: calls `addOnCondition()` → populates UI
   - Handles condition type → calls `updateOnConditionType()`
   - Populates all condition and action fields

2. **Saving:**
   - Form submit → iterates `#onConditionsList > div` elements
   - For each rule: extracts condition and action data
   - Validates and builds JSON structure
   - Sets `question.onCondition` or deletes if empty
   - Triggers `renderSectionEditor()` and `updateJSONPreview()`

### Validation Logic

- Skips rules without variable name
- Skips conditions without path or operator
- Skips conditions without value (except isEmpty/isNotEmpty)
- Only saves if at least one valid rule exists
- Cleans up by deleting `onCondition` property if no valid rules

## Testing Recommendations

### Manual Testing

1. **Create New Rule:**
   - Open question editor
   - Add onCondition rule
   - Fill in all fields
   - Save and verify JSON

2. **Test Each Condition Type:**
   - Simple condition
   - Multiple conditions (AND)
   - Multiple conditions (OR)

3. **Test Each Action Type:**
   - Set value
   - Append to array
   - Increment number
   - Decrement number

4. **Test Edge Cases:**
   - Multiple rules on one question
   - Empty variable names (should be skipped)
   - Missing condition values
   - Edit existing rules
   - Delete rules

5. **Test Persistence:**
   - Add rules and save form
   - Reload editor
   - Verify rules are loaded correctly

### JSON Validation

Verify the generated JSON matches this structure:

```json
{
  "onCondition": [
    {
      "condition": { /* valid condition object */ },
      "action": {
        "type": "set|append|increment|decrement",
        "varName": "string",
        "value": "string"
      }
    }
  ]
}
```

## Integration Requirements

### For Full Functionality

The current implementation handles the **schema and editor**. To make this functional in a form renderer, implement:

1. **Condition Evaluator:**
   ```javascript
   function evaluateCondition(condition, formData) {
     // Implement operator logic
     // Handle allOf/anyOf
     // Return true/false
   }
   ```

2. **Action Executor:**
   ```javascript
   function executeAction(action, vars) {
     switch(action.type) {
       case 'set': vars[action.varName] = action.value; break;
       case 'append': vars[action.varName].push(action.value); break;
       case 'increment': vars[action.varName] += parseFloat(action.value); break;
       case 'decrement': vars[action.varName] -= parseFloat(action.value); break;
     }
   }
   ```

3. **Form State Monitor:**
   ```javascript
   onFormChange(questionId, value) {
     // Find all questions with onCondition
     // Evaluate conditions
     // Execute actions if conditions met
     // Update vars
     // Trigger re-render if needed
   }
   ```

## Future Enhancements

### Near Term
- Add validation feedback in UI
- Show variable preview/current value
- Add help tooltips
- Syntax highlighting for variable names

### Long Term
- Expression evaluation in values
- Variable references in conditions
- Custom operators
- Action chaining
- Debugging tools
- Undo/redo for rule changes
- Template/preset rules
- Variable usage analysis

## Success Criteria

✅ **Completed:**
- [x] Schema design for onCondition
- [x] UI for creating rules
- [x] UI for editing rules
- [x] UI for deleting rules
- [x] Support for all condition types
- [x] Support for all action types
- [x] Data persistence (save/load)
- [x] Multiple rules per question
- [x] Sample data with examples
- [x] Comprehensive documentation
- [x] Quick start guide
- [x] No linting errors

⏳ **Pending:**
- [ ] Runtime condition evaluation
- [ ] Runtime action execution
- [ ] Variable state management
- [ ] Form renderer integration
- [ ] End-to-end testing

## Conclusion

The onCondition system provides a complete schema and editor implementation for dynamic variable manipulation in forms. The system is designed to be:

- **Flexible**: Supports simple to complex conditional logic
- **Extensible**: Easy to add new action types or operators
- **User-Friendly**: Intuitive UI with clear WHEN/THEN structure
- **Well-Documented**: Comprehensive guides for users and developers

The next step is implementing the runtime evaluation engine in the form renderer to bring this feature to life during actual form usage.

