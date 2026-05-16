# **Module 5, Lesson 4: Structured Outputs**

Getting Claude to return reliable JSON by parsing text is fragile. Structured outputs use a tool definition with no implementation to **force** the model to return valid, schema-conforming JSON every time.

---

## Learning Objectives

- **Explain** why text-parsed JSON is unreliable in production
- **Implement** structured extraction using `tool_choice: {"type": "tool"}`
- **Design** schemas that match your data model

---

## 1. The Problem with Text Parsing

```python
# Fragile — Claude might add explanation text, use different key names,
# or return invalid JSON on ambiguous inputs
response = client.messages.create(
    model=MODEL,
    messages=[{"role": "user", "content":
        "Extract the name, age, and city from: 'John Smith, 34, lives in Boston.' "
        "Return as JSON only."
    }]
)
data = json.loads(response.content[0].text)  # ValueError on bad days
```

---

## 2. The Structured Output Pattern

Define a tool whose *only purpose* is to structure the output. Use `tool_choice` to force Claude to call it:

```python
extract_tool = {
    "name": "extract_person",
    "description": "Extracts structured person data from text.",
    "input_schema": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age":  {"type": "integer"},
            "city": {"type": "string"},
        },
        "required": ["name", "age", "city"],
    },
}

response = client.messages.create(
    model=MODEL,
    max_tokens=256,
    tools=[extract_tool],
    tool_choice={"type": "tool", "name": "extract_person"},  # force this tool
    messages=[{"role": "user", "content":
        "Extract from: 'John Smith, 34, lives in Boston.'"
    }],
)

# Response is ALWAYS a tool_use block — no text to parse
data = response.content[0].input   # {"name": "John Smith", "age": 34, "city": "Boston"}
```

`tool_choice: {"type": "tool", "name": "..."}` means Claude **must** call this exact tool. No prose, no fallback.

---

## 3. Richer Schema Examples

**Sentiment analysis with enum:**
```python
sentiment_tool = {
    "name": "classify_sentiment",
    "description": "Classifies the sentiment of a review.",
    "input_schema": {
        "type": "object",
        "properties": {
            "sentiment": {
                "type": "string",
                "enum": ["positive", "negative", "neutral", "mixed"],
            },
            "confidence": {"type": "number", "minimum": 0, "maximum": 1},
            "key_phrases": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["sentiment", "confidence", "key_phrases"],
    },
}
```

**Document classification:**
```python
classify_tool = {
    "name": "classify_document",
    "description": "Classifies a document into categories.",
    "input_schema": {
        "type": "object",
        "properties": {
            "primary_category": {
                "type": "string",
                "enum": ["invoice", "contract", "email", "report", "other"],
            },
            "confidence":  {"type": "number"},
            "summary":     {"type": "string", "maxLength": 200},
            "action_required": {"type": "boolean"},
        },
        "required": ["primary_category", "confidence", "summary", "action_required"],
    },
}
```

---

## 4. Batch Structured Extraction

Combine with the Batch API (Module 9) for high-volume extraction:

```python
requests = [
    {
        "custom_id": f"doc-{i}",
        "params": {
            "model": MODEL_FAST,
            "max_tokens": 256,
            "tools": [extract_tool],
            "tool_choice": {"type": "tool", "name": "extract_person"},
            "messages": [{"role": "user", "content": text}],
        },
    }
    for i, text in enumerate(documents)
]
batch = client.messages.batches.create(requests=requests)
```

---

## 5. When to Use Structured Outputs

| Use case | Approach |
|----------|----------|
| Extract entities from text | Structured output tool |
| Classify documents | Structured output with enum |
| Parse user commands | Structured output |
| Free-form explanation | Plain text response |
| Mixed — explain + extract | Two separate calls or nested schema |

---

## Key Takeaways

- `tool_choice: {"type": "tool", "name": "..."}` forces a specific tool — always returns `tool_use`, never raw text
- The tool schema is the format instruction — no need for Layer 10 formatting prompts
- Use `enum` in the schema to constrain categorical fields
- Combine with the Batch API for high-volume annotation at 50% cost

---

*Up next: Module 6 — Evaluation*
