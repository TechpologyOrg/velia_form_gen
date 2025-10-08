# Frontend Implementation Guide: onCondition Runtime System

## Overview for Frontend Developers

The **onCondition** system is a new event-driven feature that automatically updates variables when users answer questions. Think of it as "if-then" rules that run whenever form data changes.

**What's Already Done:**
- ✅ Schema design
- ✅ Editor UI to create rules
- ✅ JSON serialization

**What You Need to Build:**
- ⏳ Runtime evaluation engine
- ⏳ Variable state management
- ⏳ Action executors

---

## Core Concept

```javascript
// When user answers a question, check if it has onCondition rules
// If yes, evaluate the conditions
// If conditions are met, execute the actions on the vars object

User answers question → Evaluate onCondition rules → Update vars → Re-render if needed
```

---

## Data Structure You'll Receive

### Form Schema Structure
```json
{
  "answers": [
    {
      "id": 0,
      "title": "Personal Information",
      "type": "form",
      "questions": [
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
      ]
    }
  ],
  "vars": {
    "user_tags": [],
    "score": 0,
    "status": "pending"
  }
}
```

### onCondition Rule Structure
```typescript
interface OnConditionRule {
  condition: Condition;
  action: Action;
}

// Condition can be simple or complex
type Condition = 
  | SimpleCondition 
  | { allOf: SimpleCondition[] }  // AND logic
  | { anyOf: SimpleCondition[] }  // OR logic

interface SimpleCondition {
  path: string;        // Question ID to check
  op: string;          // Operator (see list below)
  value: string | boolean | number;  // Value to compare
}

interface Action {
  type: 'set' | 'append' | 'increment' | 'decrement';
  varName: string;     // Variable name in vars object
  value: string;       // Value to use in action
}
```

---

## Implementation Steps

### Step 1: Set Up State Management

```javascript
class FormStateManager {
  constructor(formSchema) {
    this.schema = formSchema;
    this.formData = {}; // User's answers: { questionId: value }
    this.vars = { ...formSchema.vars }; // Clone initial vars
    this.listeners = []; // For re-rendering
  }

  // Get current form data
  getFormData() {
    return this.formData;
  }

  // Get current vars
  getVars() {
    return this.vars;
  }

  // Update a question's answer
  updateQuestion(questionId, value) {
    this.formData[questionId] = value;
    
    // Find the question and process its onCondition rules
    const question = this.findQuestion(questionId);
    if (question && question.onCondition) {
      this.processOnCondition(question.onCondition);
    }
    
    // Notify listeners (for re-rendering)
    this.notifyListeners();
  }

  // Helper to find question by ID
  findQuestion(questionId) {
    for (const section of this.schema.answers) {
      const question = section.questions.find(q => q.id === questionId);
      if (question) return question;
    }
    return null;
  }

  // Subscribe to state changes
  subscribe(listener) {
    this.listeners.push(listener);
  }

  notifyListeners() {
    this.listeners.forEach(listener => listener());
  }
}
```

### Step 2: Implement Condition Evaluator

```javascript
class ConditionEvaluator {
  constructor(formData) {
    this.formData = formData;
  }

  // Main evaluation function
  evaluate(condition) {
    // Check for complex conditions
    if (condition.allOf) {
      return condition.allOf.every(c => this.evaluateSimple(c));
    }
    
    if (condition.anyOf) {
      return condition.anyOf.some(c => this.evaluateSimple(c));
    }
    
    // Simple condition
    return this.evaluateSimple(condition);
  }

  // Evaluate a single condition
  evaluateSimple(condition) {
    const { path, op, value } = condition;
    const actualValue = this.formData[path];

    switch (op) {
      // Equality operators
      case 'equals':
        return actualValue == value; // Loose equality for type flexibility
      
      case 'not_equals':
        return actualValue != value;

      // Numeric comparisons
      case 'greater_than':
        return parseFloat(actualValue) > parseFloat(value);
      
      case 'less_than':
        return parseFloat(actualValue) < parseFloat(value);
      
      case 'greaterThanOrEqual':
        return parseFloat(actualValue) >= parseFloat(value);
      
      case 'lessThanOrEqual':
        return parseFloat(actualValue) <= parseFloat(value);

      // String/Array operators
      case 'contains':
        if (Array.isArray(actualValue)) {
          return actualValue.includes(value);
        }
        return String(actualValue).includes(String(value));
      
      case 'not_contains':
        if (Array.isArray(actualValue)) {
          return !actualValue.includes(value);
        }
        return !String(actualValue).includes(String(value));

      // Empty checks
      case 'isEmpty':
        return !actualValue || 
               actualValue === '' || 
               (Array.isArray(actualValue) && actualValue.length === 0);
      
      case 'isNotEmpty':
        return actualValue && 
               actualValue !== '' && 
               (!Array.isArray(actualValue) || actualValue.length > 0);

      // Date operators (if you have date questions)
      case 'before':
        return new Date(actualValue) < new Date(value);
      
      case 'after':
        return new Date(actualValue) > new Date(value);
      
      case 'on':
        return new Date(actualValue).toDateString() === new Date(value).toDateString();
      
      case 'isPast':
        return new Date(actualValue) < new Date();
      
      case 'isFuture':
        return new Date(actualValue) > new Date();
      
      case 'isToday':
        return new Date(actualValue).toDateString() === new Date().toDateString();

      default:
        console.warn(`Unknown operator: ${op}`);
        return false;
    }
  }
}
```

### Step 3: Implement Action Executor

```javascript
class ActionExecutor {
  constructor(vars) {
    this.vars = vars;
  }

  // Execute an action on the vars object
  execute(action) {
    const { type, varName, value } = action;

    switch (type) {
      case 'set':
        // Set or overwrite the variable
        this.vars[varName] = value;
        break;

      case 'append':
        // Add to array (create array if doesn't exist)
        if (!this.vars[varName]) {
          this.vars[varName] = [];
        }
        if (!Array.isArray(this.vars[varName])) {
          console.warn(`Variable ${varName} is not an array, converting to array`);
          this.vars[varName] = [this.vars[varName]];
        }
        this.vars[varName].push(value);
        break;

      case 'increment':
        // Add to number (create with 0 if doesn't exist)
        if (this.vars[varName] === undefined) {
          this.vars[varName] = 0;
        }
        this.vars[varName] = parseFloat(this.vars[varName]) + parseFloat(value);
        break;

      case 'decrement':
        // Subtract from number (create with 0 if doesn't exist)
        if (this.vars[varName] === undefined) {
          this.vars[varName] = 0;
        }
        this.vars[varName] = parseFloat(this.vars[varName]) - parseFloat(value);
        break;

      default:
        console.warn(`Unknown action type: ${type}`);
    }
  }

  // Get updated vars
  getVars() {
    return this.vars;
  }
}
```

### Step 4: Integrate Everything

```javascript
class FormStateManager {
  constructor(formSchema) {
    this.schema = formSchema;
    this.formData = {};
    this.vars = { ...formSchema.vars };
    this.listeners = [];
  }

  updateQuestion(questionId, value) {
    // Update form data
    this.formData[questionId] = value;
    
    // Find the question
    const question = this.findQuestion(questionId);
    
    // Process onCondition rules
    if (question && question.onCondition) {
      this.processOnCondition(question.onCondition);
    }
    
    // Notify listeners
    this.notifyListeners();
  }

  processOnCondition(rules) {
    const evaluator = new ConditionEvaluator(this.formData);
    const executor = new ActionExecutor(this.vars);

    // Process each rule
    for (const rule of rules) {
      // Evaluate the condition
      const conditionMet = evaluator.evaluate(rule.condition);
      
      // If condition is met, execute the action
      if (conditionMet) {
        executor.execute(rule.action);
        console.log(`Executed action: ${rule.action.type} on ${rule.action.varName}`);
      }
    }

    // Update vars with executed actions
    this.vars = executor.getVars();
  }

  findQuestion(questionId) {
    for (const section of this.schema.answers) {
      const question = section.questions.find(q => q.id == questionId);
      if (question) return question;
    }
    return null;
  }

  subscribe(listener) {
    this.listeners.push(listener);
  }

  notifyListeners() {
    this.listeners.forEach(listener => listener());
  }

  getVars() {
    return this.vars;
  }

  getFormData() {
    return this.formData;
  }
}
```

---

## Usage Example

```javascript
// Initialize form
const formSchema = /* your form JSON */;
const formManager = new FormStateManager(formSchema);

// Subscribe to changes (for re-rendering)
formManager.subscribe(() => {
  console.log('Form state changed!');
  console.log('Current vars:', formManager.getVars());
  
  // Re-render your form or update display fields
  renderForm();
});

// When user answers a question
function handleQuestionChange(questionId, value) {
  formManager.updateQuestion(questionId, value);
}

// Example: User selects "employed" for question 4
handleQuestionChange(4, 'employed');
// This will automatically:
// 1. Update formData[4] = 'employed'
// 2. Evaluate onCondition rules for question 4
// 3. If condition matches, append "professional" to vars.user_tags
// 4. Notify listeners
// 5. Trigger re-render
```

---

## React Example

```jsx
import React, { useState, useEffect } from 'react';

function DynamicForm({ formSchema }) {
  const [formManager] = useState(() => new FormStateManager(formSchema));
  const [vars, setVars] = useState(formManager.getVars());
  const [formData, setFormData] = useState({});

  useEffect(() => {
    // Subscribe to state changes
    const unsubscribe = formManager.subscribe(() => {
      setVars({ ...formManager.getVars() });
      setFormData({ ...formManager.getFormData() });
    });

    return unsubscribe;
  }, [formManager]);

  const handleChange = (questionId, value) => {
    formManager.updateQuestion(questionId, value);
  };

  return (
    <div>
      {/* Render your form questions */}
      {formSchema.answers.map(section => (
        <div key={section.id}>
          <h2>{section.title}</h2>
          {section.questions.map(question => (
            <Question
              key={question.id}
              question={question}
              value={formData[question.id]}
              onChange={(value) => handleChange(question.id, value)}
            />
          ))}
        </div>
      ))}

      {/* Display variables */}
      <div className="debug-panel">
        <h3>Current Variables:</h3>
        <pre>{JSON.stringify(vars, null, 2)}</pre>
      </div>
    </div>
  );
}
```

---

## Vue Example

```vue
<template>
  <div>
    <!-- Render form questions -->
    <div v-for="section in formSchema.answers" :key="section.id">
      <h2>{{ section.title }}</h2>
      <Question
        v-for="question in section.questions"
        :key="question.id"
        :question="question"
        :value="formData[question.id]"
        @change="handleChange(question.id, $event)"
      />
    </div>

    <!-- Display variables -->
    <div class="debug-panel">
      <h3>Current Variables:</h3>
      <pre>{{ JSON.stringify(vars, null, 2) }}</pre>
    </div>
  </div>
</template>

<script>
export default {
  props: ['formSchema'],
  data() {
    return {
      formManager: null,
      vars: {},
      formData: {}
    };
  },
  created() {
    this.formManager = new FormStateManager(this.formSchema);
    this.vars = this.formManager.getVars();
    
    // Subscribe to changes
    this.formManager.subscribe(() => {
      this.vars = { ...this.formManager.getVars() };
      this.formData = { ...this.formManager.getFormData() };
    });
  },
  methods: {
    handleChange(questionId, value) {
      this.formManager.updateQuestion(questionId, value);
    }
  }
};
</script>
```

---

## Displaying Variables in Forms

If you have questions with `type: "display"`, they reference variables:

```json
{
  "id": 10,
  "title": "Welcome Message",
  "type": "display",
  "key": "welcome_text"
}
```

To render this:

```javascript
function renderDisplayQuestion(question, vars) {
  const value = vars[question.key] || '';
  
  return `
    <div class="display-question">
      <h3>${question.title}</h3>
      <div class="display-value">${value}</div>
    </div>
  `;
}
```

When `vars` changes, these display questions will automatically update.

---

## Testing Your Implementation

### Test Case 1: Simple Append
```javascript
// Question 4: Employment Status = "employed"
formManager.updateQuestion(4, 'employed');

// Expected: vars.user_tags should include "professional"
console.assert(
  formManager.getVars().user_tags.includes('professional'),
  'Failed: user_tags should contain professional'
);
```

### Test Case 2: Multiple Conditions (AND)
```javascript
// Question 8: Years of Experience = 15
// Question 7: Is Senior = true
formManager.updateQuestion(7, true);
formManager.updateQuestion(8, 15);

// Expected: vars.user_tags should include "expert"
console.assert(
  formManager.getVars().user_tags.includes('expert'),
  'Failed: user_tags should contain expert'
);
```

### Test Case 3: Set Action
```javascript
// Question 8: Years of Experience = 6
formManager.updateQuestion(8, 6);

// Expected: vars.experience_level should be "senior"
console.assert(
  formManager.getVars().experience_level === 'senior',
  'Failed: experience_level should be senior'
);
```

---

## Performance Considerations

### 1. Debounce Updates
For text inputs, debounce the updates:

```javascript
let debounceTimer;
function handleTextInput(questionId, value) {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    formManager.updateQuestion(questionId, value);
  }, 300);
}
```

### 2. Only Process Affected Questions
Only evaluate onCondition rules for the question that changed, not all questions.

### 3. Memoize Condition Results
If conditions are complex, consider caching results until dependencies change.

---

## Common Pitfalls

### ❌ Don't Forget Type Coercion
```javascript
// Question values might be strings
const value = "5";  // String from input

// Your comparison should handle this
parseFloat(value) > 3  // ✅ Correct
value > 3              // ❌ Might fail
```

### ❌ Don't Mutate vars Directly
```javascript
// Bad
this.vars.user_tags.push(value);

// Good
this.vars = { ...this.vars, user_tags: [...this.vars.user_tags, value] };
```

### ❌ Handle Missing Variables
```javascript
// Bad
this.vars[varName]++  // Fails if undefined

// Good
this.vars[varName] = (this.vars[varName] || 0) + 1;
```

---

## Debugging Tips

### 1. Add Logging
```javascript
processOnCondition(rules) {
  console.group('Processing onCondition rules');
  
  for (const rule of rules) {
    console.log('Evaluating rule:', rule);
    const conditionMet = evaluator.evaluate(rule.condition);
    console.log('Condition met:', conditionMet);
    
    if (conditionMet) {
      console.log('Executing action:', rule.action);
      executor.execute(rule.action);
    }
  }
  
  console.log('Final vars:', this.vars);
  console.groupEnd();
}
```

### 2. Create a Debug Panel
Show current state in development:

```html
<div class="debug-panel" style="position: fixed; bottom: 0; right: 0; background: white; padding: 1rem; border: 1px solid #ccc;">
  <h4>Debug Info</h4>
  <div>
    <strong>Form Data:</strong>
    <pre id="debug-formdata"></pre>
  </div>
  <div>
    <strong>Variables:</strong>
    <pre id="debug-vars"></pre>
  </div>
</div>

<script>
formManager.subscribe(() => {
  document.getElementById('debug-formdata').textContent = 
    JSON.stringify(formManager.getFormData(), null, 2);
  document.getElementById('debug-vars').textContent = 
    JSON.stringify(formManager.getVars(), null, 2);
});
</script>
```

---

## Summary

**What you need to do:**

1. ✅ Copy the `FormStateManager`, `ConditionEvaluator`, and `ActionExecutor` classes
2. ✅ Initialize `FormStateManager` with your form schema
3. ✅ Call `formManager.updateQuestion(id, value)` whenever a question is answered
4. ✅ Subscribe to changes to re-render display fields
5. ✅ Test with the provided test cases

**The system will automatically:**
- Evaluate conditions when questions change
- Execute actions when conditions are met
- Update the `vars` object
- Trigger re-renders

**Key operators to implement:** equals, not_equals, greater_than, less_than, contains, isEmpty

**Key action types to implement:** set, append, increment, decrement

That's it! The heavy lifting is done by the condition evaluator and action executor. Your main job is to hook it up to your form state management and trigger updates when users interact with questions.

