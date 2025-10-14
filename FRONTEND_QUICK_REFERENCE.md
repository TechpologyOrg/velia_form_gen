# Frontend Quick Reference: onCondition System

## TL;DR - What You Need to Know

When a user answers a question, check if it has `onCondition` rules. If yes:
1. **Evaluate** the condition against form data
2. **Execute** the action if condition is true
3. **Update** the vars object
4. **Re-render** any display fields

---

## The Flow

```
User answers Question 4 → "employed"
         ↓
Check: Does Question 4 have onCondition? → YES
         ↓
Evaluate: formData[4] === "employed" → TRUE
         ↓
Execute: append "professional" to vars.user_tags
         ↓
vars.user_tags = ["professional"]
         ↓
Re-render display fields using vars
```

---

## Minimal Implementation (Copy-Paste Ready)

```javascript
class FormOnConditionHandler {
  constructor(formSchema) {
    this.schema = formSchema;
    this.formData = {}; // { questionId: value }
    this.vars = { ...formSchema.vars };
  }

  // Call this when user answers a question
  handleQuestionChange(questionId, value) {
    this.formData[questionId] = value;
    
    const question = this.findQuestion(questionId);
    if (question?.onCondition) {
      this.processRules(question.onCondition, questionId);
    }
    
    return this.vars; // Return updated vars for re-render
  }

  processRules(rules, questionId) {
    rules.forEach(rule => {
      if (this.checkCondition(rule.condition)) {
        // Pass the question value for actions that need it
        const questionValue = this.formData[questionId];
        this.executeAction(rule.action, questionValue);
      }
    });
  }

  checkCondition(condition) {
    if (condition.allOf) {
      return condition.allOf.every(c => this.evalSimple(c));
    }
    if (condition.anyOf) {
      return condition.anyOf.some(c => this.evalSimple(c));
    }
    return this.evalSimple(condition);
  }

  evalSimple({ path, op, value }) {
    const actual = this.formData[path];
    
    switch (op) {
      case 'equals': return actual == value;
      case 'not_equals': return actual != value;
      case 'greater_than': return parseFloat(actual) > parseFloat(value);
      case 'less_than': return parseFloat(actual) < parseFloat(value);
      case 'contains': 
        return Array.isArray(actual) 
          ? actual.includes(value)
          : String(actual).includes(value);
      case 'isEmpty': return !actual || actual === '';
      case 'isNotEmpty': return actual && actual !== '';
      default: return false;
    }
  }

  executeAction({ type, varName, value, objectKey }, questionValue) {
    switch (type) {
      case 'set':
        this.vars[varName] = value;
        break;
      case 'append':
        if (!this.vars[varName]) this.vars[varName] = [];
        this.vars[varName].push(value);
        break;
      case 'increment':
        this.vars[varName] = (this.vars[varName] || 0) + parseFloat(value);
        break;
      case 'decrement':
        this.vars[varName] = (this.vars[varName] || 0) - parseFloat(value);
        break;
      case 'setObjectKey':
        if (!this.vars[varName]) this.vars[varName] = {};
        this.vars[varName][objectKey] = value;
        break;
      case 'setObjectKeyFromQuestion':
        if (!this.vars[varName]) this.vars[varName] = {};
        this.vars[varName][objectKey] = questionValue; // Use the question's value
        break;
    }
  }

  findQuestion(id) {
    for (const section of this.schema.answers) {
      const q = section.questions.find(q => q.id == id);
      if (q) return q;
    }
    return null;
  }
}

// Usage
const handler = new FormOnConditionHandler(formSchema);

// When user answers a question
const updatedVars = handler.handleQuestionChange(4, 'employed');
console.log(updatedVars); // { user_tags: ['professional'], ... }
```

---

## Operators Cheat Sheet

| Operator | Code | Example |
|----------|------|---------|
| Equals | `actual == value` | `"employed" == "employed"` |
| Not equals | `actual != value` | `"student" != "employed"` |
| Greater than | `parseFloat(actual) > parseFloat(value)` | `10 > 5` |
| Less than | `parseFloat(actual) < parseFloat(value)` | `3 < 5` |
| ≥ | `parseFloat(actual) >= parseFloat(value)` | `5 >= 5` |
| ≤ | `parseFloat(actual) <= parseFloat(value)` | `3 <= 5` |
| Contains | `actual.includes(value)` | `["js", "py"].includes("js")` |
| Not contains | `!actual.includes(value)` | `!["js"].includes("py")` |
| Is empty | `!actual \|\| actual === ''` | Check if blank |
| Is not empty | `actual && actual !== ''` | Check if filled |

---

## Action Types Cheat Sheet

### `set` - Overwrite value
```javascript
// Before: vars.status = "pending"
// Action: { type: "set", varName: "status", value: "active" }
// After: vars.status = "active"

this.vars[varName] = value;
```

### `append` - Add to array
```javascript
// Before: vars.tags = ["user"]
// Action: { type: "append", varName: "tags", value: "premium" }
// After: vars.tags = ["user", "premium"]

if (!this.vars[varName]) this.vars[varName] = [];
this.vars[varName].push(value);
```

### `increment` - Add number
```javascript
// Before: vars.score = 10
// Action: { type: "increment", varName: "score", value: "5" }
// After: vars.score = 15

this.vars[varName] = (this.vars[varName] || 0) + parseFloat(value);
```

### `decrement` - Subtract number
```javascript
// Before: vars.lives = 3
// Action: { type: "decrement", varName: "lives", value: "1" }
// After: vars.lives = 2

this.vars[varName] = (this.vars[varName] || 0) - parseFloat(value);
```

### `setObjectKey` - Set object property ✨
```javascript
// Before: vars.user_profile = {}
// Action: { type: "setObjectKey", varName: "user_profile", objectKey: "email", value: "john@example.com" }
// After: vars.user_profile = { email: "john@example.com" }

if (!this.vars[varName]) this.vars[varName] = {};
this.vars[varName][objectKey] = value;
```

### `setObjectKeyFromQuestion` - Set object property from question value ✨ NEW
```javascript
// Question 3 value: 30
// Before: vars.user_profile = {}
// Action: { type: "setObjectKeyFromQuestion", varName: "user_profile", objectKey: "age", value: "" }
// After: vars.user_profile = { age: 30 }

if (!this.vars[varName]) this.vars[varName] = {};
this.vars[varName][objectKey] = questionValue; // Auto uses question's value
```

---

## React Hook (Copy-Paste)

```javascript
import { useState, useCallback } from 'react';

function useFormWithOnCondition(formSchema) {
  const [handler] = useState(() => new FormOnConditionHandler(formSchema));
  const [vars, setVars] = useState(handler.vars);
  const [formData, setFormData] = useState({});

  const updateQuestion = useCallback((questionId, value) => {
    const updatedVars = handler.handleQuestionChange(questionId, value);
    setVars({ ...updatedVars });
    setFormData({ ...handler.formData });
  }, [handler]);

  return { vars, formData, updateQuestion };
}

// Usage in component
function MyForm() {
  const { vars, formData, updateQuestion } = useFormWithOnCondition(formSchema);

  return (
    <div>
      <input onChange={(e) => updateQuestion(4, e.target.value)} />
      <div>Tags: {vars.user_tags?.join(', ')}</div>
    </div>
  );
}
```

---

## Vue Composable (Copy-Paste)

```javascript
import { ref, readonly } from 'vue';

function useFormWithOnCondition(formSchema) {
  const handler = new FormOnConditionHandler(formSchema);
  const vars = ref(handler.vars);
  const formData = ref({});

  const updateQuestion = (questionId, value) => {
    const updatedVars = handler.handleQuestionChange(questionId, value);
    vars.value = { ...updatedVars };
    formData.value = { ...handler.formData };
  };

  return {
    vars: readonly(vars),
    formData: readonly(formData),
    updateQuestion
  };
}

// Usage in component
export default {
  setup() {
    const { vars, formData, updateQuestion } = useFormWithOnCondition(formSchema);
    return { vars, formData, updateQuestion };
  }
};
```

---

## Debugging One-Liner

```javascript
// Add this to see what's happening
console.log('onCondition:', { 
  questionId, 
  value, 
  conditionMet: this.checkCondition(rule.condition), 
  action: rule.action,
  newVars: this.vars 
});
```

---

## Testing Checklist

```javascript
// Test 1: Simple condition
handler.handleQuestionChange(4, 'employed');
assert(handler.vars.user_tags.includes('professional')); ✓

// Test 2: Numeric comparison
handler.handleQuestionChange(8, 6);
assert(handler.vars.experience_level === 'senior'); ✓

// Test 3: Multiple rules
handler.handleQuestionChange(4, 'student');
assert(handler.vars.user_tags.includes('education')); ✓

// Test 4: Array contains
handler.handleQuestionChange(6, ['JavaScript', 'Python']);
assert(handler.vars.tech_stack.includes('frontend')); ✓
assert(handler.vars.tech_stack.includes('backend')); ✓
```

---

## Common Mistakes

❌ **Forgetting to clone vars**
```javascript
return this.vars; // Bad - returns reference
return { ...this.vars }; // Good - returns copy
```

❌ **Not handling undefined**
```javascript
this.vars[varName]++; // Fails if undefined
this.vars[varName] = (this.vars[varName] || 0) + 1; // Safe
```

❌ **String vs Number comparison**
```javascript
"5" > 3 // true (lucky)
"5" > "10" // true (wrong! string comparison)
parseFloat("5") > parseFloat("10") // false (correct)
```

❌ **Not creating arrays for append**
```javascript
this.vars[varName].push(value); // Fails if undefined
if (!this.vars[varName]) this.vars[varName] = [];
this.vars[varName].push(value); // Safe
```

---

## Performance Tips

✓ Only process onCondition for the changed question (not all questions)
✓ Debounce text input updates (300ms)
✓ Use shallow comparison for re-renders
✓ Clone vars efficiently: `{ ...this.vars }` not `JSON.parse(JSON.stringify())`

---

## Example Form Data Structure

```javascript
// What you receive
const formSchema = {
  answers: [
    {
      questions: [
        {
          id: 4,
          onCondition: [
            {
              condition: { path: "4", op: "equals", value: "employed" },
              action: { type: "append", varName: "user_tags", value: "professional" }
            }
          ]
        }
      ]
    }
  ],
  vars: { user_tags: [] }
};

// What you track
const formData = { 4: "employed", 8: 6, 7: true };
const vars = { user_tags: ["professional"], experience_level: "senior" };
```

---

## Need More Details?

See `FRONTEND_IMPLEMENTATION_GUIDE.md` for:
- Complete class implementations
- All operator implementations
- Framework-specific examples
- Testing strategies
- Debugging techniques

