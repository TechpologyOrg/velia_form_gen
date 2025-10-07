# System Architecture: onCondition Feature

## Overview Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        FORM SCHEMA                               │
├─────────────────────────────────────────────────────────────────┤
│  {                                                               │
│    "answers": [...],      ← Form sections                       │
│    "vars": {},           ← Global variables                     │
│    "title": "...",       ← Form metadata                        │
│    "description": "..."                                          │
│  }                                                               │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                        QUESTION OBJECT                           │
├─────────────────────────────────────────────────────────────────┤
│  {                                                               │
│    "id": 4,                                                      │
│    "title": "Employment Status",                                │
│    "type": "choice",                                             │
│    "value": "",                                                  │
│    "choices": ["employed", "student"],                           │
│    "visibleWhen": {...},  ← Controls visibility                 │
│    "onCondition": [...]   ← Manipulates variables ✨ NEW        │
│  }                                                               │
└─────────────────────────────────────────────────────────────────┘
```

## onCondition Data Flow

```
USER INTERACTION
      │
      ▼
┌──────────────────────┐
│  Question Answered   │
│  (User enters data)  │
└──────────────────────┘
      │
      ▼
┌──────────────────────────────────────────────────────────────┐
│  EVALUATE onCondition Rules                                  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Rule 1: IF employment = "employed"                    │  │
│  │          THEN append "professional" to user_tags       │  │
│  ├────────────────────────────────────────────────────────┤  │
│  │  Rule 2: IF employment = "student"                     │  │
│  │          THEN append "education" to user_tags          │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
      │
      ▼
┌──────────────────────┐
│  Condition Engine    │
│  ┌────────────────┐  │
│  │ Check path     │  │
│  │ Apply operator │  │
│  │ Compare value  │  │
│  │ Return bool    │  │
│  └────────────────┘  │
└──────────────────────┘
      │
      ▼ (If condition TRUE)
┌──────────────────────┐
│  Action Executor     │
│  ┌────────────────┐  │
│  │ Get action     │  │
│  │ type & value   │  │
│  │ Execute on     │  │
│  │ vars object    │  │
│  └────────────────┘  │
└──────────────────────┘
      │
      ▼
┌──────────────────────┐
│  Update vars Object  │
│  {                   │
│    user_tags: [      │
│      "professional"  │
│    ]                 │
│  }                   │
└──────────────────────┘
      │
      ▼
┌──────────────────────┐
│  Trigger Re-render   │
│  (For display fields)│
└──────────────────────┘
```

## Component Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                     EDITOR (editor.html)                        │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Question Editor Modal                                   │   │
│  │  ┌───────────────────────────────────────────────────┐   │   │
│  │  │  Basic Fields (title, type, value, etc.)          │   │   │
│  │  └───────────────────────────────────────────────────┘   │   │
│  │  ┌───────────────────────────────────────────────────┐   │   │
│  │  │  Visibility Condition (visibleWhen)               │   │   │
│  │  │  • Show/hide this question                        │   │   │
│  │  └───────────────────────────────────────────────────┘   │   │
│  │  ┌───────────────────────────────────────────────────┐   │   │
│  │  │  Variable Actions (onCondition) ✨ NEW            │   │   │
│  │  │  ┌─────────────────────────────────────────────┐  │   │   │
│  │  │  │  Variable Action 1                          │  │   │   │
│  │  │  │  ┌───────────────────────────────────────┐  │  │   │   │
│  │  │  │  │  WHEN (Condition)                     │  │  │   │   │
│  │  │  │  │  • Simple / AND / OR                  │  │  │   │   │
│  │  │  │  │  • Path, Operator, Value              │  │  │   │   │
│  │  │  │  └───────────────────────────────────────┘  │  │   │   │
│  │  │  │  ┌───────────────────────────────────────┐  │  │   │   │
│  │  │  │  │  THEN (Action)                        │  │  │   │   │
│  │  │  │  │  • Action Type (set/append/inc/dec)   │  │  │   │   │
│  │  │  │  │  • Variable Name                      │  │  │   │   │
│  │  │  │  │  • Value                              │  │  │   │   │
│  │  │  │  └───────────────────────────────────────┘  │  │   │   │
│  │  │  └─────────────────────────────────────────────┘  │   │   │
│  │  │  └─────────────────────────────────────────────┘   │   │   │
│  │  │  [+ Add Variable Action]                           │   │   │
│  │  └───────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

## Data Structure Comparison

```
┌────────────────────────────────────────────────────────────────┐
│                     visibleWhen vs onCondition                  │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  visibleWhen (Controls Visibility)                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  {                                                        │  │
│  │    "path": "4",          ← Which question to check       │  │
│  │    "op": "equals",       ← How to compare                │  │
│  │    "value": "employed"   ← What to compare to            │  │
│  │  }                                                        │  │
│  │                                                           │  │
│  │  Result: Show/Hide this question                         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  onCondition (Manipulates Variables) ✨                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  [                                                        │  │
│  │    {                                                      │  │
│  │      "condition": {          ← WHEN (same as visibleWhen)│  │
│  │        "path": "4",                                       │  │
│  │        "op": "equals",                                    │  │
│  │        "value": "employed"                                │  │
│  │      },                                                   │  │
│  │      "action": {             ← THEN (what to do)         │  │
│  │        "type": "append",     ← Action type               │  │
│  │        "varName": "user_tags", ← Which variable          │  │
│  │        "value": "professional" ← What value              │  │
│  │      }                                                    │  │
│  │    }                                                      │  │
│  │  ]                                                        │  │
│  │                                                           │  │
│  │  Result: Modify vars.user_tags                           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

## Action Type Behavior

```
┌─────────────────────────────────────────────────────────────────┐
│  ACTION TYPE: set                                                │
├─────────────────────────────────────────────────────────────────┤
│  Before: vars = { status: "pending" }                           │
│  Action: { type: "set", varName: "status", value: "active" }    │
│  After:  vars = { status: "active" }                            │
│                                                                  │
│  • Overwrites existing value                                    │
│  • Creates variable if it doesn't exist                         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  ACTION TYPE: append                                             │
├─────────────────────────────────────────────────────────────────┤
│  Before: vars = { tags: ["user"] }                              │
│  Action: { type: "append", varName: "tags", value: "premium" }  │
│  After:  vars = { tags: ["user", "premium"] }                   │
│                                                                  │
│  • Adds to array                                                │
│  • Creates empty array if variable doesn't exist                │
│  • Allows duplicates                                            │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  ACTION TYPE: increment                                          │
├─────────────────────────────────────────────────────────────────┤
│  Before: vars = { score: 50 }                                   │
│  Action: { type: "increment", varName: "score", value: "10" }   │
│  After:  vars = { score: 60 }                                   │
│                                                                  │
│  • Adds numeric value                                           │
│  • Creates variable with 0 if it doesn't exist                  │
│  • Converts value string to number                              │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  ACTION TYPE: decrement                                          │
├─────────────────────────────────────────────────────────────────┤
│  Before: vars = { lives: 3 }                                    │
│  Action: { type: "decrement", varName: "lives", value: "1" }    │
│  After:  vars = { lives: 2 }                                    │
│                                                                  │
│  • Subtracts numeric value                                      │
│  • Creates variable with 0 if it doesn't exist                  │
│  • Converts value string to number                              │
└─────────────────────────────────────────────────────────────────┘
```

## Condition Evaluation Logic

```
┌────────────────────────────────────────────────────────────────┐
│  SIMPLE CONDITION                                               │
├────────────────────────────────────────────────────────────────┤
│  {                                                              │
│    "path": "4",                                                 │
│    "op": "equals",                                              │
│    "value": "employed"                                          │
│  }                                                              │
│                                                                 │
│  Evaluation:                                                    │
│  1. Get value from question ID 4                               │
│  2. Apply "equals" operator                                    │
│  3. Compare with "employed"                                    │
│  4. Return true/false                                          │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│  COMPLEX CONDITION (allOf - AND)                               │
├────────────────────────────────────────────────────────────────┤
│  {                                                              │
│    "allOf": [                                                   │
│      { "path": "age", "op": "greater_than", "value": "18" },   │
│      { "path": "hasLicense", "op": "equals", "value": true }   │
│    ]                                                            │
│  }                                                              │
│                                                                 │
│  Evaluation:                                                    │
│  1. Evaluate condition 1: age > 18                             │
│  2. Evaluate condition 2: hasLicense = true                    │
│  3. Return: condition1 AND condition2                          │
│  4. Both must be true to trigger action                        │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│  COMPLEX CONDITION (anyOf - OR)                                │
├────────────────────────────────────────────────────────────────┤
│  {                                                              │
│    "anyOf": [                                                   │
│      { "path": "role", "op": "equals", "value": "admin" },     │
│      { "path": "role", "op": "equals", "value": "moderator" }  │
│    ]                                                            │
│  }                                                              │
│                                                                 │
│  Evaluation:                                                    │
│  1. Evaluate condition 1: role = "admin"                       │
│  2. Evaluate condition 2: role = "moderator"                   │
│  3. Return: condition1 OR condition2                           │
│  4. At least one must be true to trigger action                │
└────────────────────────────────────────────────────────────────┘
```

## Integration Points

```
┌────────────────────────────────────────────────────────────────┐
│  EDITOR → FORM RENDERER → BACKEND                              │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. EDITOR (Current Implementation ✅)                         │
│     • Create/edit onCondition rules                            │
│     • Save to JSON schema                                      │
│     • Load from saved forms                                    │
│                                                                 │
│  2. FORM RENDERER (To Be Implemented ⏳)                       │
│     • Display form to users                                    │
│     • Capture user input                                       │
│     • Evaluate onCondition rules                               │
│     • Update vars object                                       │
│     • Trigger re-renders                                       │
│                                                                 │
│  3. BACKEND (To Be Extended ⏳)                                │
│     • Store form responses                                     │
│     • Store final vars state                                   │
│     • Query/analyze variables                                  │
│     • Export data with computed variables                      │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

## File Organization

```
velia_form_gen/
├── formgen/
│   └── templates/
│       └── core/
│           └── editor.html ← Main implementation
│               ├── Lines 343-356:   UI section
│               ├── Lines 901-953:   Load logic
│               ├── Lines 1592-1696: Save logic
│               └── Lines 1972-2182: JavaScript functions
│
├── sample_form.json ← Examples with onCondition
│
└── Documentation/
    ├── README.md                      ← Project overview
    ├── ONCONDITION_DOCUMENTATION.md   ← Complete reference
    ├── ONCONDITION_QUICKSTART.md      ← Quick guide
    ├── ONCONDITION_FEATURE_SUMMARY.md ← Feature overview
    ├── IMPLEMENTATION_SUMMARY.md      ← Technical details
    └── SYSTEM_ARCHITECTURE.md         ← This file
```

## State Management Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                      FORM STATE LIFECYCLE                        │
└─────────────────────────────────────────────────────────────────┘
           │
           ▼
    ┌─────────────┐
    │ Form Loaded │
    └─────────────┘
           │
           ▼
    ┌─────────────────────┐
    │ Initialize vars     │
    │ from schema         │
    └─────────────────────┘
           │
           ▼
    ┌─────────────────────┐
    │ User answers        │
    │ Question A          │
    └─────────────────────┘
           │
           ▼
    ┌─────────────────────┐
    │ Check if Question A │
    │ has onCondition     │
    └─────────────────────┘
           │
           ├─ No ───────────┐
           │                 │
           ▼                 ▼
    ┌─────────────────────┐  ┌──────────────────┐
    │ Evaluate each rule  │  │ Continue to      │
    └─────────────────────┘  │ next question    │
           │                 └──────────────────┘
           ▼
    ┌─────────────────────┐
    │ Condition met?      │
    └─────────────────────┘
           │
           ├─ No ───────────┐
           │                 │
           ▼                 ▼
    ┌─────────────────────┐  ┌──────────────────┐
    │ Execute action      │  │ Skip this rule   │
    │ Update vars         │  └──────────────────┘
    └─────────────────────┘
           │
           ▼
    ┌─────────────────────┐
    │ Trigger re-render   │
    │ (if needed)         │
    └─────────────────────┘
           │
           ▼
    ┌─────────────────────┐
    │ Continue to next    │
    │ question            │
    └─────────────────────┘
```

## Summary

The onCondition system provides a declarative way to manipulate form state based on user input. The architecture is designed to be:

- **Modular**: Conditions and actions are separate concerns
- **Extensible**: Easy to add new action types or operators
- **Composable**: Multiple rules per question, complex conditions
- **Maintainable**: Clear data structure, well-documented
- **Performance**: Evaluates only when relevant questions change

The current implementation provides the schema and editor. The next phase is implementing the runtime evaluation engine in the form renderer.

