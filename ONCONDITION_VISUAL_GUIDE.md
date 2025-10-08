# onCondition Visual Guide

## The Big Picture

```
┌─────────────────────────────────────────────────────────────┐
│                         USER FILLS FORM                      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Question: "What's your employment status?"                  │
│  [x] Employed  [ ] Student  [ ] Unemployed                   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  YOUR FRONTEND CODE                                          │
│  handleChange(questionId=4, value="employed")                │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  CHECK: Does question 4 have onCondition rules?              │
│  → YES, found 2 rules                                        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  RULE 1:                                                     │
│  IF formData[4] === "employed"                               │
│  THEN append "professional" to vars.user_tags                │
│                                                              │
│  Evaluation: "employed" === "employed" → TRUE ✓              │
│  Action: vars.user_tags.push("professional")                 │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  RULE 2:                                                     │
│  IF formData[4] === "student"                                │
│  THEN append "education" to vars.user_tags                   │
│                                                              │
│  Evaluation: "employed" === "student" → FALSE ✗              │
│  Action: SKIPPED                                             │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  UPDATED STATE                                               │
│  vars = {                                                    │
│    user_tags: ["professional"],  ← NEW!                      │
│    score: 0,                                                 │
│    status: "pending"                                         │
│  }                                                           │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  RE-RENDER FORM                                              │
│  (Update any display fields showing vars)                    │
└─────────────────────────────────────────────────────────────┘
```

---

## Example: Real-World Scenario

### Scenario: Tech Skills Assessment Form

```
┌────────────────────────────────────────────────────────────────┐
│  FORM QUESTIONS                                                 │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Q1: Name: [John Doe________]                                  │
│                                                                 │
│  Q4: Employment Status:                                         │
│      (•) Employed  ( ) Student  ( ) Unemployed                  │
│      ↓                                                          │
│      onCondition: IF employed → tag "professional"              │
│                                                                 │
│  Q6: Skills (select all):                                       │
│      [x] JavaScript  [x] Python  [ ] React                      │
│      ↓                          ↓                               │
│      onCondition:               onCondition:                    │
│      IF contains JavaScript     IF contains Python              │
│      → append "frontend"        → append "backend"              │
│                                                                 │
│  Q8: Years Experience: [6_____]                                 │
│      ↓                                                          │
│      onCondition: IF > 5 → set experience_level = "senior"      │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────────┐
│  RESULTING VARS STATE                                           │
├────────────────────────────────────────────────────────────────┤
│  {                                                              │
│    user_tags: ["professional"],                                 │
│    tech_stack: ["frontend", "backend"],                         │
│    experience_level: "senior",                                  │
│    score: 0                                                     │
│  }                                                              │
└────────────────────────────────────────────────────────────────┘
                              ↓
┌────────────────────────────────────────────────────────────────┐
│  YOU CAN NOW USE THESE VARS TO:                                 │
│  • Display user profile summary                                 │
│  • Route to appropriate next steps                              │
│  • Calculate recommendations                                    │
│  • Generate reports                                             │
│  • Store in database with form submission                       │
└────────────────────────────────────────────────────────────────┘
```

---

## The Three Action Types in Action

### 1. SET - Overwrite a Value

```
Initial State:
┌──────────────┐
│ vars = {     │
│   status:    │
│   "pending"  │
│ }            │
└──────────────┘

User Action: Approves form
↓

onCondition Rule:
┌───────────────────────────────────────┐
│ IF approved === true                  │
│ THEN set status = "approved"          │
└───────────────────────────────────────┘
↓

Final State:
┌──────────────┐
│ vars = {     │
│   status:    │
│   "approved" │  ← Changed!
│ }            │
└──────────────┘
```

### 2. APPEND - Add to Array

```
Initial State:
┌──────────────┐
│ vars = {     │
│   tags: []   │
│ }            │
└──────────────┘

User Action: Selects "employed"
↓

onCondition Rule:
┌───────────────────────────────────────┐
│ IF employment === "employed"          │
│ THEN append "professional" to tags    │
└───────────────────────────────────────┘
↓

State After Rule 1:
┌─────────────────────────┐
│ vars = {                │
│   tags: ["professional"]│  ← Added!
│ }                       │
└─────────────────────────┘

User Action: Confirms senior role
↓

onCondition Rule:
┌───────────────────────────────────────┐
│ IF is_senior === true                 │
│ THEN append "expert" to tags          │
└───────────────────────────────────────┘
↓

Final State:
┌──────────────────────────────────────┐
│ vars = {                             │
│   tags: ["professional", "expert"]   │  ← Added another!
│ }                                    │
└──────────────────────────────────────┘
```

### 3. INCREMENT - Add to Number

```
Initial State:
┌──────────────┐
│ vars = {     │
│   score: 0   │
│ }            │
└──────────────┘

User Action: Answers Q1 correctly
↓

onCondition Rule:
┌───────────────────────────────────────┐
│ IF answer1 === "correct"              │
│ THEN increment score by 10            │
└───────────────────────────────────────┘
↓

State After Q1:
┌──────────────┐
│ vars = {     │
│   score: 10  │  ← 0 + 10 = 10
│ }            │
└──────────────┘

User Action: Answers Q2 correctly
↓

onCondition Rule:
┌───────────────────────────────────────┐
│ IF answer2 === "correct"              │
│ THEN increment score by 15            │
└───────────────────────────────────────┘
↓

Final State:
┌──────────────┐
│ vars = {     │
│   score: 25  │  ← 10 + 15 = 25
│ }            │
└──────────────┘
```

---

## Complex Conditions: allOf (AND)

```
Question: Years of Experience [12____]

onCondition Rule:
┌─────────────────────────────────────────────────────┐
│ IF ALL OF:                                          │
│   • years_experience > 10         ← Condition 1     │
│   • is_senior_role === true       ← Condition 2     │
│ THEN append "expert" to tags                        │
└─────────────────────────────────────────────────────┘

Evaluation Process:
┌──────────────────────────────────┐
│ Check Condition 1:               │
│ years_experience = 12            │
│ 12 > 10? → TRUE ✓                │
└──────────────────────────────────┘
         AND
┌──────────────────────────────────┐
│ Check Condition 2:               │
│ is_senior_role = true            │
│ true === true? → TRUE ✓          │
└──────────────────────────────────┘
         =
┌──────────────────────────────────┐
│ Overall Result:                  │
│ TRUE AND TRUE = TRUE ✓           │
│                                  │
│ → Execute action!                │
│ tags.push("expert")              │
└──────────────────────────────────┘
```

---

## Complex Conditions: anyOf (OR)

```
Question: User Role [moderator_____]

onCondition Rule:
┌─────────────────────────────────────────────────────┐
│ IF ANY OF:                                          │
│   • role === "admin"              ← Condition 1     │
│   • role === "moderator"          ← Condition 2     │
│   • role === "owner"              ← Condition 3     │
│ THEN set has_permissions = true                     │
└─────────────────────────────────────────────────────┘

Evaluation Process:
┌──────────────────────────────────┐
│ Check Condition 1:               │
│ role = "moderator"               │
│ "moderator" === "admin"?         │
│ → FALSE ✗                        │
└──────────────────────────────────┘
         OR
┌──────────────────────────────────┐
│ Check Condition 2:               │
│ role = "moderator"               │
│ "moderator" === "moderator"?     │
│ → TRUE ✓                         │
└──────────────────────────────────┘
         OR
┌──────────────────────────────────┐
│ Check Condition 3:               │
│ (Not evaluated - already true)   │
└──────────────────────────────────┘
         =
┌──────────────────────────────────┐
│ Overall Result:                  │
│ FALSE OR TRUE = TRUE ✓           │
│                                  │
│ → Execute action!                │
│ has_permissions = true           │
└──────────────────────────────────┘
```

---

## Data Flow Through Your Application

```
┌────────────────────────────────────────────────────────────┐
│  1. FORM SCHEMA (JSON)                                      │
│     Loaded from backend                                     │
│     Contains: questions, initial vars, onCondition rules    │
└────────────────────────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────────┐
│  2. FORM STATE MANAGER                                      │
│     • Stores form data (user answers)                       │
│     • Stores vars (computed variables)                      │
│     • Listens for changes                                   │
└────────────────────────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────────┐
│  3. USER INTERACTION                                        │
│     User types, selects, checks boxes                       │
└────────────────────────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────────┐
│  4. EVENT HANDLER                                           │
│     handleChange(questionId, value)                         │
└────────────────────────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────────┐
│  5. UPDATE FORM DATA                                        │
│     formData[questionId] = value                            │
└────────────────────────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────────┐
│  6. FIND ONCONDITION RULES                                  │
│     Does this question have onCondition?                    │
└────────────────────────────────────────────────────────────┘
                         ↓
            ┌─────────YES──────────┐
            ↓                       ↓
┌────────────────────┐    ┌────────────────────┐
│  7a. EVALUATE      │    │  7b. SKIP          │
│      CONDITIONS    │    │      (No rules)    │
└────────────────────┘    └────────────────────┘
            ↓                       ↓
┌────────────────────┐              │
│  8. EXECUTE        │              │
│     ACTIONS        │              │
└────────────────────┘              │
            ↓                       ↓
┌────────────────────────────────────────────────────────────┐
│  9. UPDATE VARS                                             │
│     vars updated with new values                            │
└────────────────────────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────────┐
│  10. NOTIFY LISTENERS                                       │
│      Trigger re-render                                      │
└────────────────────────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────────┐
│  11. RE-RENDER UI                                           │
│      • Update display fields                                │
│      • Show/hide based on visibleWhen                       │
│      • Update any vars-dependent UI                         │
└────────────────────────────────────────────────────────────┘
```

---

## Code Structure Overview

```
┌────────────────────────────────────────────────────────────┐
│  FormStateManager                                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Properties:                                         │  │
│  │  • formData: {}      ← User's answers               │  │
│  │  • vars: {}          ← Computed variables           │  │
│  │  • listeners: []     ← Re-render callbacks          │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Methods:                                            │  │
│  │  • updateQuestion(id, value)                        │  │
│  │  • processOnCondition(rules)                        │  │
│  │  • subscribe(callback)                              │  │
│  │  • getVars()                                        │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
                         ↓ uses
┌────────────────────────────────────────────────────────────┐
│  ConditionEvaluator                                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Methods:                                            │  │
│  │  • evaluate(condition)  ← Main entry                │  │
│  │  • evaluateSimple(condition)                        │  │
│  │                                                      │  │
│  │  Handles:                                            │  │
│  │  • Simple conditions                                 │  │
│  │  • allOf (AND logic)                                 │  │
│  │  • anyOf (OR logic)                                  │  │
│  │  • All operators                                     │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
                         ↓ uses
┌────────────────────────────────────────────────────────────┐
│  ActionExecutor                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Methods:                                            │  │
│  │  • execute(action)   ← Main entry                   │  │
│  │                                                      │  │
│  │  Handles:                                            │  │
│  │  • set      (overwrite)                             │  │
│  │  • append   (add to array)                          │  │
│  │  • increment (add number)                           │  │
│  │  • decrement (subtract number)                      │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
```

---

## Comparison: visibleWhen vs onCondition

```
┌────────────────────────────────────────────────────────────┐
│  visibleWhen                                                │
│  ─────────────                                              │
│  Controls what the USER SEES                                │
│                                                             │
│  Question 5: Company Name                                   │
│  visibleWhen: { path: "4", op: "equals", value: "employed" }│
│                                                             │
│  If employment !== "employed" → Question 5 is HIDDEN       │
│  If employment === "employed" → Question 5 is VISIBLE      │
│                                                             │
│  Effect: UI changes (show/hide elements)                    │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│  onCondition                                                │
│  ────────────                                               │
│  Controls INTERNAL STATE                                    │
│                                                             │
│  Question 4: Employment Status                              │
│  onCondition: [{                                            │
│    condition: { path: "4", op: "equals", value: "employed" },│
│    action: { type: "append", varName: "tags", value: "pro" }│
│  }]                                                         │
│                                                             │
│  If employment === "employed" → "pro" added to vars.tags   │
│                                                             │
│  Effect: Data changes (vars object updated)                 │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│  THEY WORK TOGETHER                                         │
│                                                             │
│  Question 4: Employment                                     │
│    • Has onCondition → Updates vars.tags                    │
│                                                             │
│  Question 5: Company Name                                   │
│    • Has visibleWhen → Shows only if employed              │
│                                                             │
│  Question 10: User Profile Display                          │
│    • type: "display"                                        │
│    • key: "tags"                                            │
│    • Shows: vars.tags (updated by onCondition)             │
└────────────────────────────────────────────────────────────┘
```

---

## Summary in One Picture

```
    USER INPUT
       ↓
    Question
       ↓
   ┌───┴───┐
   │       │
   ↓       ↓
visibleWhen  onCondition
   ↓           ↓
Show/Hide   Update vars
Question       ↓
            Display
            Fields
```

**That's it!** Your frontend just needs to:
1. Detect when a question is answered
2. Check if it has `onCondition`
3. Evaluate the condition
4. Execute the action
5. Re-render

See `FRONTEND_IMPLEMENTATION_GUIDE.md` for complete code examples.

